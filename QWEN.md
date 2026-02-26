# Personal AI Employee Hackathon - Project Context

## Project Overview

This is a **hackathon project** focused on building a "Digital FTE" (Full-Time Equivalent) — an autonomous AI employee that manages personal and business affairs 24/7. The architecture is **local-first**, **agent-driven**, and uses **human-in-the-loop** patterns for sensitive actions.

### Core Architecture

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Brain** | Claude Code | Reasoning engine for task execution |
| **Memory/GUI** | Obsidian (Markdown vault) | Dashboard, knowledge base, task tracking |
| **Senses** | Python Watcher scripts | Monitor Gmail, WhatsApp, filesystems |
| **Hands** | MCP Servers | External actions (email, browser automation, payments) |
| **Persistence** | Ralph Wiggum Loop | Keeps Claude working until tasks complete |

### Key Concepts

- **Watcher Pattern**: Lightweight Python scripts run continuously, monitoring inputs and creating `.md` files in `/Needs_Action` folder
- **Ralph Wiggum Loop**: A Stop hook pattern that intercepts Claude's exit and re-injects prompts until tasks are complete
- **Human-in-the-Loop (HITL)**: Sensitive actions require approval via file movement (`/Pending_Approval` → `/Approved`)
- **Monday Morning CEO Briefing**: Autonomous weekly audit generating revenue reports, bottleneck analysis, and proactive suggestions

## Directory Structure

```
Hackathone-Personal-AI-Employe/
├── .qwen/skills/           # Qwen agent skills
│   └── browsing-with-playwright/
│       ├── SKILL.md        # Skill documentation
│       ├── references/     # Tool reference docs
│       └── scripts/        # MCP client & server helpers
├── Personal AI Employee Hackathon 0_....md  # Full hackathon blueprint
├── skills-lock.json        # Skill version tracking
└── QWEN.md                 # This file
```

## Available Skills

### browsing-with-playwright

Browser automation via Playwright MCP server. Use for:
- Web scraping and data extraction
- Form submission and UI testing
- Navigation and interaction workflows

**Server Management:**
```bash
# Start (port 8808, shared browser context)
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Stop (closes browser gracefully)
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh

# Verify running
python .qwen/skills/browsing-with-playwright/scripts/verify.py
```

**Key Tools:**
- `browser_snapshot` - Get accessibility snapshot (element refs)
- `browser_click`, `browser_type`, `browser_fill_form` - Interact with elements
- `browser_navigate`, `browser_take_screenshot` - Navigation & capture
- `browser_run_code` - Execute complex Playwright code snippets

See `.qwen/skills/browsing-with-playwright/SKILL.md` for full usage.

## Hackathon Tiers

| Tier | Description | Estimated Time |
|------|-------------|----------------|
| **Bronze** | Foundation: Obsidian vault, 1 watcher, basic Claude integration | 8-12 hours |
| **Silver** | Functional: Multiple watchers, MCP servers, HITL workflow | 20-30 hours |
| **Gold** | Autonomous: Full integration, Odoo accounting, weekly audits | 40+ hours |
| **Platinum** | Production: Cloud deployment, domain specialization, A2A sync | 60+ hours |

## Key Files

| File | Purpose |
|------|---------|
| `Personal AI Employee Hackathon 0_....md` | Complete architectural blueprint, templates, and implementation guide |
| `.qwen/skills/browsing-with-playwright/SKILL.md` | Browser automation skill documentation |
| `.qwen/skills/browsing-with-playwright/scripts/mcp-client.py` | Universal MCP client (HTTP + stdio transports) |
| `skills-lock.json` | Tracks installed skill versions |

## Development Patterns

### Watcher Script Template
```python
from pathlib import Path
from abc import ABC, abstractmethod

class BaseWatcher(ABC):
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
    
    @abstractmethod
    def check_for_updates(self) -> list:
        """Return list of new items to process"""
        pass
    
    @abstractmethod
    def create_action_file(self, item) -> Path:
        """Create .md file in Needs_Action folder"""
        pass
```

### Approval Request Pattern
For sensitive actions, Claude writes:
```markdown
---
type: approval_request
action: payment
amount: 500.00
status: pending
---
## To Approve: Move to /Approved
## To Reject: Move to /Rejected
```

### Ralph Wiggum Loop Usage
```bash
# Start loop with completion promise
/ralph-loop "Process all files in /Needs_Action" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10
```

## Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| Claude Code | Active subscription | Primary reasoning engine |
| Obsidian | v1.10.6+ | Knowledge base & dashboard |
| Python | 3.13+ | Watcher scripts |
| Node.js | v24+ LTS | MCP servers |
| GitHub Desktop | Latest | Version control |

## MCP Servers Reference

| Server | Capabilities | Use Case |
|--------|-------------|----------|
| `filesystem` | Read/write/list files | Built-in vault access |
| `email-mcp` | Send/draft/search emails | Gmail integration |
| `browser-mcp` | Navigate, click, fill forms | Payment portals, web automation |
| `calendar-mcp` | Create/update events | Scheduling |

## Weekly Research Meetings

- **When**: Wednesdays at 10:00 PM PKT
- **Zoom**: [Link in main documentation](Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md)
- **YouTube**: https://www.youtube.com/@panaversity

## Common Workflows

### 1. Form Submission
1. Navigate: `browser_navigate`
2. Snapshot: `browser_snapshot` (get element refs)
3. Fill: `browser_fill_form` or `browser_type`
4. Submit: `browser_click`
5. Verify: `browser_wait_for` + screenshot

### 2. Data Extraction
1. Navigate to page
2. Get snapshot (contains text content)
3. Use `browser_evaluate` for complex extraction
4. Process results

### 3. Human Approval Flow
1. Claude detects sensitive action needed
2. Writes approval request to `/Pending_Approval/`
3. User moves file to `/Approved` or `/Rejected`
4. Orchestrator triggers MCP action on approval

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Playwright server not responding | `bash scripts/stop-server.sh && bash scripts/start-server.sh` |
| Element not found | Run `browser_snapshot` first to get current refs |
| Click fails | Try `browser_hover` first, then click |
| Form not submitting | Use `"submit": true` with `browser_type` |

## Resources

- [Claude Code Agent Skills Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Ralph Wiggum Plugin](https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum)
- [Playwright MCP Server](https://github.com/microsoft/playwright-mcp)
- [MCP Protocol](https://modelcontextprotocol.io/)
