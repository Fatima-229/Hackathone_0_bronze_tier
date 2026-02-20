# Hackathon 0: Bronze Tier - Personal AI Employee

> **Your Life and Business on Autopilot. Local-first, Agent-driven, Human-in-the-loop.**

This repository contains a complete **Bronze Tier** implementation of the Personal AI Employee Hackathon 0 - Building Autonomous FTEs (Full-Time Equivalent) in 2026.

---

## 🎯 What is a Digital FTE?

A **Digital FTE** (Full-Time Equivalent) is an AI agent built, "hired," and priced as if it were a human employee. It works 24/7, costs 85-90% less than a human, and scales exponentially.

| Feature | Human FTE | Digital FTE |
|---------|-----------|-------------|
| Availability | 40 hours/week | 168 hours/week (24/7) |
| Monthly Cost | $4,000 - $8,000+ | $500 - $2,000 |
| Ramp-up Time | 3-6 months | Instant |
| Consistency | 85-95% accuracy | 99%+ consistency |
| Annual Hours | ~2,000 hours | ~8,760 hours |

---

## 📁 Repository Structure

```
Hackathone_0_bronze_tier/
├── README.md                              # This file
├── Personal AI Employee Hackathon 0_...md # Full hackathon blueprint
├── AI_Employee_Vault/                     # The AI Employee implementation
│   ├── Dashboard.md                       # Real-time status dashboard
│   ├── Company_Handbook.md                # Rules and guidelines
│   ├── Business_Goals.md                  # Objectives and metrics
│   ├── scripts/
│   │   ├── filesystem_watcher.py          # File system monitor
│   │   ├── orchestrator.py                # Main coordination process
│   │   └── SKILL.md                       # Agent skill documentation
│   ├── Inbox/                             # Raw incoming items
│   ├── Needs_Action/                      # Items requiring processing
│   ├── Plans/                             # Active action plans
│   ├── Approved/                          # Human-approved actions
│   ├── Done/                              # Completed items
│   └── Drop_Folder/                       # Drop files for processing
└── .claude/                               # Claude Code configuration
```

---

## ⚡ Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Claude Code** installed and configured
3. **Obsidian** (optional, for viewing the vault)

### Step 1: Clone the Repository

```bash
git clone https://github.com/Fatima-229/Hackathone_0_bronze_tier.git
cd Hackathone_0_bronze_tier
```

### Step 2: Navigate to the Vault

```bash
cd AI_Employee_Vault
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

Create a test file in the `Drop_Folder`:

```bash
# Create drop folder if it doesn't exist
mkdir Drop_Folder

# Create a test file
echo "This is a test file for processing" > Drop_Folder/test_document.txt
```

Wait 30 seconds, then check the `Needs_Action/` folder for a new action file.

---

## 🔧 How It Works

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

## 📖 Documentation

- **[Full Hackathon Blueprint](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)** - Complete architectural guide
- **[AI Employee Vault README](./AI_Employee_Vault/README.md)** - Detailed setup instructions
- **[Claude Code Documentation](https://docs.anthropic.com/claude-code/)**
- **[Obsidian](https://obsidian.md/)**
- **[Model Context Protocol](https://modelcontextprotocol.io/)**

---

## 🚀 Next Steps (Silver Tier)

After mastering Bronze Tier, consider adding:

1. **Gmail Watcher**: Monitor email for action items
2. **WhatsApp Watcher**: Monitor messages for keywords
3. **MCP Integration**: Connect to external services
4. **Scheduled Tasks**: Cron-based automation
5. **Email Sending**: Automated responses (with approval)

---

## 🔗 Resources

- **Hackathon Meetings**: Wednesdays at 10:00 PM PKT on Zoom
- **YouTube**: [Panaversity Channel](https://www.youtube.com/@panaversity)

---

*Built for Hackathon 0 - Building Autonomous FTEs in 2026*
