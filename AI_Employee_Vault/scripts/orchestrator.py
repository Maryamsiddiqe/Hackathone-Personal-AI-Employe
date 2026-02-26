#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orchestrator - Master process for the AI Employee.

This script:
1. Monitors Needs_Action folder for new items
2. Triggers Qwen Code to process pending items
3. Updates Dashboard.md with current status
4. Manages the overall workflow

For Bronze Tier: Simple polling-based orchestrator that triggers Qwen Code.
"""

import os
import sys
import subprocess
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class Orchestrator:
    """
    Main orchestrator for the AI Employee system.

    Coordinates between watchers, Qwen Code, and the vault.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.check_interval = check_interval
        
        # Key folders
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.done = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.logs = self.vault_path / 'Logs'
        self.dashboard = self.vault_path / 'Dashboard.md'
        
        # Ensure all folders exist
        for folder in [self.needs_action, self.plans, self.done, 
                       self.pending_approval, self.approved, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger('Orchestrator')
        self.logger.info(f'Initialized Orchestrator')
        self.logger.info(f'Vault: {self.vault_path}')
        
        # Track processed files
        self.processed_files = set()

    def get_pending_items(self) -> List[Path]:
        """
        Get all .md files in Needs_Action that haven't been processed.
        
        Returns:
            List[Path]: List of pending action files
        """
        pending = []
        try:
            for filepath in self.needs_action.iterdir():
                if filepath.suffix == '.md' and filepath not in self.processed_files:
                    pending.append(filepath)
        except Exception as e:
            self.logger.error(f'Error scanning Needs_Action: {e}')
        return pending

    def get_approved_items(self) -> List[Path]:
        """
        Get all files in Approved folder ready for execution.
        
        Returns:
            List[Path]: List of approved files
        """
        approved = []
        try:
            for filepath in self.approved.iterdir():
                if filepath.suffix == '.md':
                    approved.append(filepath)
        except Exception as e:
            self.logger.error(f'Error scanning Approved: {e}')
        return approved

    def trigger_qwen_processing(self, items: List[Path]) -> bool:
        """
        Trigger Qwen Code to process pending items.

        For Bronze Tier: This creates a prompt file that the user can
        manually feed to Qwen Code, or runs qwen in non-interactive mode.

        Args:
            items: List of items to process

        Returns:
            bool: True if processing was triggered
        """
        if not items:
            return False

        self.logger.info(f'Triggering Qwen Code for {len(items)} item(s)')

        # Create a processing prompt
        prompt_file = self.vault_path / 'scripts' / 'current_prompt.md'

        item_names = [item.name for item in items]

        prompt_content = f'''# AI Employee Task Processing

## Pending Items
Process the following items in /Needs_Action:

{chr(10).join(f'- {name}' for name in item_names)}

## Instructions
1. Read each file in /Needs_Action
2. Read /Company_Handbook.md for rules and guidelines
3. Read /Business_Goals.md for context
4. For each item:
   - Understand what action is needed
   - Create a plan in /Plans/
   - Execute if auto-approved, or create approval request
   - Log all actions
   - Move completed items to /Done
5. Update /Dashboard.md with current status

## Completion
When all items are processed, output: <promise>TASK_COMPLETE</promise>
'''

        prompt_file.write_text(prompt_content, encoding='utf-8')
        self.logger.info(f'Created prompt file: {prompt_file.name}')

        # Try to run Qwen Code if available
        try:
            # Check if qwen command exists - try different variants for Windows
            qwen_commands = ['qwen', 'qwen.cmd', 'qwen-code']
            qwen_cmd = None
            
            for cmd in qwen_commands:
                try:
                    result = subprocess.run(
                        [cmd, '--version'],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        shell=True
                    )
                    if result.returncode == 0:
                        qwen_cmd = cmd
                        self.logger.info(f'Found Qwen Code using command: {cmd}')
                        break
                except Exception:
                    continue
            
            if qwen_cmd:
                self.logger.info('Qwen Code found, triggering processing...')

                # Run Qwen Code with the prompt
                # Use shell=True on Windows to handle .cmd files
                # Use positional prompt (newer syntax) instead of --prompt (deprecated)
                prompt_text = f'Process items in {self.needs_action}. See {prompt_file} for instructions.'
                
                qwen_process = [
                    qwen_cmd,
                    prompt_text,
                    '--cwd',
                    str(self.vault_path)
                ]

                # Run in background for non-interactive processing
                subprocess.Popen(
                    qwen_process,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    shell=True
                )
                self.logger.info('Qwen Code processing started')
                return True
            else:
                self.logger.warning('Qwen Code not available - manual processing required')
                self.logger.info(f'Read {prompt_file} and run Qwen Code manually')

        except FileNotFoundError:
            self.logger.warning('Qwen Code not installed - showing manual instructions')
            print("\n" + "="*60)
            print("MANUAL PROCESSING REQUIRED")
            print("="*60)
            print(f"\n1. Open terminal in vault: cd {self.vault_path}")
            print("2. Run Qwen Code:")
            print("   qwen --prompt 'Process items in Needs_Action folder'")
            print(f"\n3. Or read prompt file: {prompt_file}")
            print("="*60 + "\n")

        except subprocess.TimeoutExpired:
            self.logger.warning('Qwen Code check timed out')
        except Exception as e:
            self.logger.error(f'Error triggering Qwen Code: {e}')

        return False

    def execute_approved_actions(self, items: List[Path]) -> bool:
        """
        Execute actions that have been approved.
        
        For Bronze Tier: This logs the approved actions and moves them to Done.
        Higher tiers will integrate with MCP servers for actual execution.
        
        Args:
            items: List of approved items
            
        Returns:
            bool: True if actions were executed
        """
        if not items:
            return False
        
        self.logger.info(f'Executing {len(items)} approved action(s)')
        
        for item in items:
            try:
                # Read the approved item
                content = item.read_text()
                
                # Log the action
                self.log_action(
                    action_type='approved_execution',
                    target=item.name,
                    result='logged_for_bronze_tier',
                    details='Bronze tier: Manual execution required'
                )
                
                # Move to Done
                dest = self.done / item.name
                item.rename(dest)
                self.logger.info(f'Moved to Done: {item.name}')
                
            except Exception as e:
                self.logger.error(f'Error executing approved item {item.name}: {e}')
        
        return True

    def update_dashboard(self):
        """
        Update Dashboard.md with current status.
        """
        try:
            pending_count = len(list(self.needs_action.glob('*.md')))
            approval_count = len(list(self.pending_approval.glob('*.md')))
            done_count = len(list(self.done.glob('*.md')))

            # Get today's date
            today = datetime.now().strftime('%Y-%m-%d')
            timestamp = datetime.now().isoformat()

            # Read current dashboard with UTF-8 encoding
            if self.dashboard.exists():
                content = self.dashboard.read_text(encoding='utf-8')

                # Update the status section
                lines = content.split('\n')
                new_lines = []
                in_status = False

                for line in lines:
                    if '| Pending Tasks |' in line:
                        new_lines.append(f'| Pending Tasks | {pending_count} |')
                        in_status = True
                    elif '| Awaiting Approval |' in line:
                        new_lines.append(f'| Awaiting Approval | {approval_count} |')
                    elif '| Completed Today |' in line:
                        new_lines.append(f'| Completed Today | {done_count} |')
                    elif '| Last generated by AI' in line:
                        new_lines.append(f'*Last generated by AI Employee v0.1 (Bronze Tier) - {timestamp}*')
                    else:
                        new_lines.append(line)

                content = '\n'.join(new_lines)
            else:
                # Create new dashboard
                content = f'''---
last_updated: {timestamp}
status: active
---

# AI Employee Dashboard

## Quick Status

| Metric | Value |
|--------|-------|
| Pending Tasks | {pending_count} |
| Awaiting Approval | {approval_count} |
| Completed Today | {done_count} |
| Revenue MTD | $0 |

---

*Last generated by AI Employee v0.1 (Bronze Tier) - {timestamp}*
'''

            self.dashboard.write_text(content, encoding='utf-8')
            self.logger.debug('Dashboard updated')

        except Exception as e:
            self.logger.error(f'Error updating dashboard: {e}')

    def log_action(self, action_type: str, target: str, result: str, details: str = ''):
        """
        Log an action to the logs folder.
        
        Args:
            action_type: Type of action (e.g., 'email_send', 'file_process')
            target: What the action targeted
            result: Outcome of the action
            details: Additional details
        """
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            log_file = self.logs / f'{today}.jsonl'
            
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'action_type': action_type,
                'target': target,
                'result': result,
                'details': details,
                'actor': 'orchestrator'
            }
            
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
                
            self.logger.debug(f'Logged action: {action_type} -> {result}')
            
        except Exception as e:
            self.logger.error(f'Error logging action: {e}')

    def run(self):
        """
        Main run loop - continuously monitors and processes items.
        """
        self.logger.info(f'Starting Orchestrator main loop')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        try:
            while True:
                try:
                    # Update dashboard
                    self.update_dashboard()

                    # Check for pending items
                    pending = self.get_pending_items()
                    if pending:
                        self.trigger_qwen_processing(pending)

                    # Check for approved items
                    approved = self.get_approved_items()
                    if approved:
                        self.execute_approved_actions(approved)

                    # Log heartbeat
                    self.logger.debug(f'Heartbeat - Pending: {len(pending)}, Approved: {len(approved)}')

                except Exception as e:
                    self.logger.error(f'Error in orchestration cycle: {e}')

                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info('Orchestrator stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            raise


def main():
    """Main entry point."""
    import time  # Import here to avoid issues
    
    # Default path - parent of scripts folder
    script_dir = Path(__file__).parent
    vault_path = script_dir.parent
    
    # Allow command line override
    if len(sys.argv) > 1:
        vault_path = Path(sys.argv[1])
    
    print(f"AI Employee - Orchestrator (Bronze Tier)")
    print(f"========================================")
    print(f"Vault: {vault_path}")
    print(f"Check Interval: 60 seconds")
    print(f"\nMonitoring:")
    print(f"  - /Needs_Action for new items")
    print(f"  - /Approved for execution")
    print(f"\nPress Ctrl+C to stop\n")
    
    orchestrator = Orchestrator(str(vault_path))
    orchestrator.run()


if __name__ == '__main__':
    import time  # Ensure time is available
    main()
