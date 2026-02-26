# AI Employee - Bronze Tier

> **Your Personal AI Employee - Foundation Layer**

A local-first, agent-driven automation system that processes tasks autonomously using Qwen Code and Obsidian.

---

## Quick Start

### 1. Prerequisites

Ensure you have the following installed:

| Software | Version | Purpose |
|----------|---------|---------|
| [Python](https://python.org) | 3.10+ | Watcher scripts |
| [Qwen Code](https://github.com/QwenLM/Qwen) | Latest | AI reasoning engine |
| [Obsidian](https://obsidian.md) | v1.10.6+ | Knowledge base (optional for viewing) |

### 2. Installation

```bash
# Navigate to scripts folder
cd AI_Employee_Vault/scripts

# Install Python dependencies (optional - only watchdog needed)
pip install -r requirements.txt
```

### 3. Verify Qwen Code

```bash
qwen --version
```

If not found, install Qwen Code according to the official documentation.

### 4. Start the System

**Windows:**
```batch
# Start the file watcher
start-watcher.bat

# In a new terminal, start the orchestrator
start-orchestrator.bat
```

**Mac/Linux:**
```bash
# Start both processes
bash start-all.sh
```

### 5. Test the Workflow

1. Drop a file into the `Inbox/` folder
2. Watcher will move it to `Needs_Action/` and create a metadata file
3. Orchestrator will detect the new item and trigger Qwen Code
4. Qwen Code processes the item according to `Company_Handbook.md`
5. Completed items move to `Done/`

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AI Employee                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   Watchers  │───▶│ Orchestrator│───▶│  Qwen Code  │ │
│  │  (Python)   │    │  (Python)   │    │   (Brain)   │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
│         │                  │                  │         │
│         ▼                  ▼                  ▼         │
│  ┌─────────────────────────────────────────────────────┐│
│  │              Obsidian Vault (Memory)                ││
│  │  /Inbox  /Needs_Action  /Plans  /Done  /Logs       ││
│  └─────────────────────────────────────────────────────┘│
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Folder Structure

```
AI_Employee_Vault/
├── Dashboard.md              # Real-time status dashboard
├── Company_Handbook.md       # Rules of engagement
├── Business_Goals.md         # Your business objectives
├── Inbox/                    # Drop files here for processing
├── Needs_Action/             # Items awaiting processing
├── Plans/                    # AI-created action plans
├── Pending_Approval/         # Awaiting your decision
├── Approved/                 # Ready for execution
├── Done/                     # Completed items
├── Logs/                     # Action audit logs
├── Accounting/               # Financial records
├── Briefings/                # CEO briefings
├── Invoices/                 # Generated invoices
└── scripts/                  # Python scripts
    ├── base_watcher.py       # Base class for watchers
    ├── filesystem_watcher.py # File drop watcher
    ├── orchestrator.py       # Main orchestrator
    └── requirements.txt      # Python dependencies
```

---

## Usage

### File Drop Processing

The simplest way to give tasks to your AI Employee:

1. **Drop a file** into `Inbox/` folder
2. **Watcher detects** the new file within 30 seconds
3. **File moves** to `Needs_Action/` with metadata
4. **Orchestrator triggers** Claude Code
5. **AI processes** the item and moves to `Done/`

### Manual Task Creation

Create a `.md` file directly in `Needs_Action/`:

```markdown
---
type: manual_task
priority: normal
status: pending
---

# Task Description

## Details
Describe what needs to be done...

## Expected Actions
- [ ] Action 1
- [ ] Action 2
```

### Checking Status

Open `Dashboard.md` to see:
- Pending tasks count
- Awaiting approval count
- Completed today count
- Recent activity

---

## Bronze Tier Deliverables

✅ **Completed:**

- [x] Obsidian vault with `Dashboard.md` and `Company_Handbook.md`
- [x] Filesystem Watcher script (file drop monitoring)
- [x] Claude Code integration for processing
- [x] Basic folder structure: `/Inbox`, `/Needs_Action`, `/Done`
- [x] Orchestrator for workflow coordination
- [x] Audit logging to `/Logs/`

---

## Configuration

### Watcher Settings

Edit `filesystem_watcher.py` to adjust:

```python
# Check interval (default: 30 seconds)
check_interval: int = 30

# Watch folder (default: vault/Inbox)
watch_folder: str = "Inbox"
```

### Orchestrator Settings

Edit `orchestrator.py` to adjust:

```python
# Check interval (default: 60 seconds)
check_interval: int = 60
```

---

## Troubleshooting

### Claude Code not found

```bash
# Install Claude Code
npm install -g @anthropic/claude-code

# Verify installation
claude --version
```

### Watcher not detecting files

1. Check the file is in `Inbox/` (not `Needs_Action/`)
2. Ensure file doesn't start with `.` (hidden files ignored)
3. Check watcher is running (look for heartbeat in logs)

### Orchestrator not triggering Qwen

1. Verify Qwen Code is installed: `qwen --version`
2. Check orchestrator logs for errors
3. Try manual processing:
   ```bash
   cd AI_Employee_Vault
   qwen --prompt "Process items in Needs_Action folder"
   ```

### Python errors

```bash
# Ensure Python 3.10+ is installed
python --version

# Install dependencies
pip install -r requirements.txt
```

---

## Security Notes

**Bronze Tier is read-only:**
- No external actions (email, payments) are taken automatically
- All actions are logged for audit
- Human approval required for any external actions

**Best practices:**
- Never store credentials in vault files
- Review logs regularly
- Keep vault backed up

---

## Next Steps (Silver Tier)

Upgrade to Silver Tier by adding:

1. **Gmail Watcher** - Monitor email inbox
2. **WhatsApp Watcher** - Monitor WhatsApp messages
3. **MCP Server Integration** - Send emails, make payments
4. **Human-in-the-Loop** - Approval workflow
5. **Scheduled Tasks** - Cron/Task Scheduler integration

---

## Learning Resources

- [Qwen Code Documentation](https://github.com/QwenLM/Qwen)
- [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Obsidian Help](https://help.obsidian.md/)
- [Hackathon Documentation](../../Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs in `/Logs/` folder
3. Read the full hackathon documentation
4. Join Wednesday Research Meetings (see hackathon doc)

---

*AI Employee v0.1 - Bronze Tier*
