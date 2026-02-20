# AI Employee Bronze Tier

> **Your Personal AI Employee - Local-first, Agent-driven, Human-in-the-loop**

A complete Bronze Tier implementation of the Personal AI Employee Hackathon. This system uses Claude Code as the reasoning engine and Obsidian as the dashboard/memory to autonomously process tasks with human oversight.

---

## 🎯 What This Does

The AI Employee Bronze Tier:
- **Monitors** a drop folder for new files
- **Creates** action items in an Obsidian vault
- **Processes** tasks using Claude Code
- **Requests approval** for sensitive actions
- **Logs** all actions for audit
- **Updates** a real-time dashboard

---

## 📁 Project Structure

```
AI_Employee_Vault/
├── scripts/
│   ├── base_watcher.py       # Base class for all watchers
│   ├── filesystem_watcher.py # File system monitor
│   ├── orchestrator.py       # Main coordination process
│   ├── SKILL.md              # Agent skill documentation
│   └── requirements.txt      # Python dependencies
├── Inbox/                     # Raw incoming items
├── Needs_Action/              # Items requiring processing
├── Plans/                     # Active action plans
├── Approved/                  # Human-approved actions
├── Rejected/                  # Human-rejected actions
├── Done/                      # Completed items
├── Logs/                      # Action audit logs
├── Briefings/                 # Reports and briefings
├── Dashboard.md               # Real-time status dashboard
├── Company_Handbook.md        # Rules and guidelines
└── Business_Goals.md          # Objectives and metrics
```

---

## ⚡ Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Claude Code** installed and configured
3. **Obsidian** (optional, for viewing the vault)

### Step 1: Clone/Setup

```bash
# Navigate to the vault directory
cd AI_Employee_Vault
```

### Step 2: Verify Python

```bash
python --version
# Should show Python 3.8 or higher
```

### Step 3: Start the File Watcher

Open a terminal and run:

```bash
# Windows
python scripts\filesystem_watcher.py .

# Mac/Linux
python scripts/filesystem_watcher.py .
```

### Step 4: Start the Orchestrator

Open a **second terminal** and run:

```bash
# Windows
python scripts\orchestrator.py .

# Mac/Linux
python scripts/orchestrator.py .
```

### Step 5: Test the System

1. Create a test file in the `Drop_Folder`:

```bash
# Create drop folder if it doesn't exist
mkdir Drop_Folder

# Create a test file
echo "This is a test file for processing" > Drop_Folder/test_document.txt
```

2. Wait 30 seconds (default check interval)

3. Check `Needs_Action/` folder - a new action file should appear

4. The orchestrator will process it and create a plan

### Step 6: View Dashboard

Open `Dashboard.md` in Obsidian or any text editor to see real-time status.

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file (see `.env.example`):

```bash
# Optional: Custom Claude command
CLAUDE_COMMAND=claude

# Optional: Max Claude iterations
MAX_CLAUDE_ITERATIONS=5

# Optional: Check interval (seconds)
CHECK_INTERVAL=30
```

### Watcher Settings

Edit `scripts/filesystem_watcher.py` to customize:

```python
# Check interval (default: 30 seconds)
check_interval = 30

# Priority keywords
priority_keywords = {
    'high': ['urgent', 'asap', 'emergency'],
    'medium': ['invoice', 'payment', 'deadline'],
    'low': ['note', 'reference', 'info']
}
```

---

## 📖 How It Works

### Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Drop Folder    │────▶│  File Watcher    │────▶│  Needs_Action/  │
│  (new files)    │     │  (polls every 30s)│     │  (action files) │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Dashboard.md   │◀────│  Orchestrator    │◀────│  Claude Code    │
│  (status)       │     │  (coordinates)   │     │  (processes)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

### Workflow

1. **File Drop**: User drops a file in `Drop_Folder/`
2. **Detection**: File Watcher detects new file (every 30s)
3. **Action Creation**: Watcher creates action file in `Needs_Action/`
4. **Processing**: Orchestrator triggers Claude Code
5. **Plan Creation**: Claude creates plan in `Plans/`
6. **Execution**: Claude processes the task
7. **Completion**: Files moved to `Done/`, dashboard updated

---

## ✅ Bronze Tier Deliverables

This implementation includes all Bronze Tier requirements:

- [x] Obsidian vault with `Dashboard.md` and `Company_Handbook.md`
- [x] One working Watcher script (File System monitoring)
- [x] Claude Code integration for reading/writing to vault
- [x] Basic folder structure: `/Inbox`, `/Needs_Action`, `/Done`
- [x] Agent Skill documentation (`SKILL.md`)

---

## 🔒 Security Notes

### What's Safe

- ✅ All data stays local in the vault
- ✅ No credentials stored in markdown
- ✅ Human approval required for sensitive actions
- ✅ All actions logged for audit

### What Requires Approval

Per `Company_Handbook.md`:

| Action | Auto-Approve | Require Approval |
|--------|--------------|------------------|
| Create/read files | ✅ | ❌ |
| Move within vault | ✅ | ❌ |
| Delete files | ❌ | ✅ |
| Send emails | ❌ | ✅ |
| Process payments | ❌ | ✅ |

---

## 📝 Usage Examples

### Example 1: Process a Document

```bash
# Drop a file for processing
echo "Meeting notes from today" > Drop_Folder/meeting_notes.txt

# Wait for processing
# Check Needs_Action/ for action file
# Check Plans/ for execution plan
# Check Done/ when complete
```

### Example 2: Manual Approval

When Claude needs approval, it creates a file in `Pending_Approval/`:

```bash
# Review the approval request
cat Pending_Approval/APPROVAL_delete_old_files.md

# To approve: move to Approved/
mv Pending_Approval/APPROVAL_* Approved/

# To reject: move to Rejected/
mv Pending_Approval/APPROVAL_* Rejected/
```

### Example 3: Check Status

```bash
# View dashboard
cat Dashboard.md

# View pending items
ls Needs_Action/

# View today's logs
cat Logs/2026-02-20.json
```

---

## 🐛 Troubleshooting

### Watcher Not Detecting Files

1. Check the drop folder path is correct
2. Verify file permissions
3. Check `scripts/filesystem_watcher.log` for errors

### Orchestrator Not Processing

1. Ensure Claude Code is installed: `claude --version`
2. Check `scripts/orchestrator.log` for errors
3. Verify vault path is correct

### Dashboard Not Updating

1. Ensure orchestrator is running
2. Check file permissions on `Dashboard.md`
3. Restart the orchestrator

---

## 🚀 Next Steps (Silver Tier)

After mastering Bronze Tier, consider adding:

1. **Gmail Watcher**: Monitor email for action items
2. **WhatsApp Watcher**: Monitor messages for keywords
3. **MCP Integration**: Connect to external services
4. **Scheduled Tasks**: Cron-based automation
5. **Email Sending**: Automated responses (with approval)

---

## 📚 Documentation

- `Company_Handbook.md` - Rules and guidelines
- `Business_Goals.md` - Objectives and metrics
- `scripts/SKILL.md` - Agent skill documentation
- `Dashboard.md` - Real-time status

---

## 🤝 Contributing

This is a hackathon project. Feel free to:
- Fork and enhance
- Add new watchers
- Improve documentation
- Share your extensions

---

## 📄 License

This project is part of the Personal AI Employee Hackathon 0.

---

## 🔗 Resources

- [Hackathon Document](../Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Claude Code Documentation](https://docs.anthropic.com/claude-code/)
- [Obsidian](https://obsidian.md/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

---

*AI Employee Bronze Tier v1.0*
*Built for Hackathon 0 - Building Autonomous FTEs in 2026*
