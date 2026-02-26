#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filesystem Watcher - Monitors a drop folder for new files.

When files are added to the Inbox folder, this watcher:
1. Copies the file to Needs_Action
2. Creates a metadata .md file with file details
3. Triggers Qwen Code processing

This is the simplest watcher for the Bronze tier - just drag and drop files!
"""

import os
import shutil
import time
import hashlib
from pathlib import Path
from datetime import datetime

# Import base watcher
from base_watcher import BaseWatcher, get_timestamp, get_date_string


class FilesystemWatcher(BaseWatcher):
    """
    Watches a folder for new files and creates action files.
    
    Usage:
        python filesystem_watcher.py /path/to/vault /path/to/watch
        python filesystem_watcher.py  # Uses default paths
    """
    
    def __init__(self, vault_path: str, watch_folder: str = None, check_interval: int = 30):
        """
        Initialize the filesystem watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            watch_folder: Folder to watch for new files (default: vault/Inbox)
            check_interval: Seconds between checks (default: 30)
        """
        super().__init__(vault_path, check_interval)
        
        # Set watch folder
        if watch_folder:
            self.watch_folder = Path(watch_folder)
        else:
            self.watch_folder = self.vault_path / 'Inbox'
        
        # Ensure watch folder exists
        self.watch_folder.mkdir(parents=True, exist_ok=True)
        
        # Track processed files by hash to avoid duplicates
        self.processed_files = set()
        
        # Track file sizes to detect new files
        self.known_files = {}
        
        self.logger.info(f'Watch folder: {self.watch_folder}')

    def _get_file_hash(self, filepath: Path) -> str:
        """Get MD5 hash of a file."""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _load_known_files(self):
        """Load known files and their sizes from disk."""
        state_file = self.vault_path / 'scripts' / '.filesystem_watcher_state.json'
        if state_file.exists():
            import json
            try:
                with open(state_file, 'r') as f:
                    self.known_files = json.load(f)
                self.logger.info(f'Loaded state: {len(self.known_files)} known files')
            except Exception as e:
                self.logger.warning(f'Could not load state file: {e}')
                self.known_files = {}

    def _save_known_files(self):
        """Save known files state to disk."""
        state_file = self.vault_path / 'scripts' / '.filesystem_watcher_state.json'
        import json
        try:
            with open(state_file, 'w') as f:
                json.dump(self.known_files, f)
        except Exception as e:
            self.logger.warning(f'Could not save state file: {e}')

    def check_for_updates(self) -> list:
        """
        Check for new files in the watch folder.
        
        Returns:
            list: List of new file paths
        """
        new_files = []
        
        try:
            # Load known files on first run
            if not self.known_files:
                self._load_known_files()
            
            # Scan watch folder
            for filepath in self.watch_folder.iterdir():
                if filepath.is_file() and not filepath.name.startswith('.'):
                    file_key = str(filepath)
                    current_size = filepath.stat().st_size
                    
                    # Check if this is a new file or modified
                    if file_key not in self.known_files:
                        # New file detected
                        new_files.append(filepath)
                        self.known_files[file_key] = current_size
                        self.logger.info(f'New file detected: {filepath.name}')
                    elif self.known_files[file_key] != current_size:
                        # File was modified
                        new_files.append(filepath)
                        self.known_files[file_key] = current_size
                        self.logger.info(f'File modified: {filepath.name}')
            
            # Save state periodically
            if new_files:
                self._save_known_files()
                
        except Exception as e:
            self.logger.error(f'Error scanning watch folder: {e}')
        
        return new_files

    def create_action_file(self, filepath: Path) -> Path:
        """
        Create an action file for a new file drop.
        
        Args:
            filepath: Path to the new file
            
        Returns:
            Path: Path to the created action file
        """
        # Get file details
        file_size = filepath.stat().st_size
        file_modified = datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
        file_hash = self._get_file_hash(filepath)
        
        # Copy file to Needs_Action
        dest_path = self.needs_action / filepath.name
        try:
            shutil.copy2(filepath, dest_path)
            self.logger.info(f'Copied file to Needs_Action: {dest_path.name}')
        except Exception as e:
            self.logger.error(f'Error copying file: {e}')
            raise
        
        # Create metadata file
        timestamp = get_timestamp()
        date_str = get_date_string()
        safe_name = filepath.stem.replace(' ', '_').replace('-', '_')
        
        metadata_content = f'''---
type: file_drop
original_name: {filepath.name}
size: {file_size}
size_human: {self._format_size(file_size)}
received: {timestamp}
modified: {file_modified}
file_hash: {file_hash}
status: pending
priority: normal
---

# File Drop for Processing

## File Details
- **Original Name:** {filepath.name}
- **Size:** {self._format_size(file_size)}
- **Received:** {timestamp}
- **Last Modified:** {file_modified}

## Content Preview
*(Add manual preview or description here)*

---

## Suggested Actions
- [ ] Review file content
- [ ] Determine required action
- [ ] Process and move to /Done
- [ ] Archive original file

---

## Processing Notes
*(Add notes here during processing)*

'''
        
        # Write metadata file
        metadata_path = self.needs_action / f'FILE_{safe_name}_{date_str}.md'
        metadata_path.write_text(metadata_content)
        
        # Remove from watch folder after processing
        try:
            filepath.unlink()
            self.logger.info(f'Removed from watch folder: {filepath.name}')
        except Exception as e:
            self.logger.warning(f'Could not remove file from watch folder: {e}')
        
        return metadata_path

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"


def main():
    """Main entry point."""
    import sys
    
    # Default paths
    script_dir = Path(__file__).parent
    vault_path = script_dir.parent  # Parent of scripts/ folder
    
    # Allow command line override
    if len(sys.argv) > 1:
        vault_path = Path(sys.argv[1])
    
    watch_folder = vault_path / 'Inbox'
    if len(sys.argv) > 2:
        watch_folder = Path(sys.argv[2])
    
    print(f"AI Employee - Filesystem Watcher")
    print(f"================================")
    print(f"Vault: {vault_path}")
    print(f"Watch Folder: {watch_folder}")
    print(f"Check Interval: 30 seconds")
    print(f"\nDrop files into: {watch_folder}")
    print("Press Ctrl+C to stop\n")
    
    watcher = FilesystemWatcher(str(vault_path), str(watch_folder))
    watcher.run()


if __name__ == '__main__':
    main()
