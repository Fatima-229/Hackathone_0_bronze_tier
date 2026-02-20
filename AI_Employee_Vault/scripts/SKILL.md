---
name: ai-employee-bronze
description: |
  AI Employee Bronze Tier - Process files from the Obsidian vault, create plans,
  execute tasks, and manage the approval workflow. Use this skill when tasks
  require file processing, task management, or human-in-the-loop approvals.
---

# AI Employee Bronze Tier Skill

Process files from the Obsidian vault and execute tasks autonomously with human-in-the-loop safeguards.

## Overview

This skill enables Claude Code to function as an AI Employee that:
- Reads action files from `/Needs_Action/` folder
- Creates execution plans in `/Plans/` folder
- Processes tasks autonomously within defined boundaries
- Requests approval for sensitive actions
- Logs all actions and updates the Dashboard

## Folder Structure

```
AI_Employee_Vault/
├── Inbox/              # Raw incoming items
├── Needs_Action/       # Items requiring processing
├── Plans/              # Active action plans
├── Approved/           # Human-approved actions
├── Rejected/           # Human-rejected actions
├── Done/               # Completed items
├── Logs/               # Action audit logs
├── Briefings/          # Reports and briefings
├── Dashboard.md        # Real-time status
├── Company_Handbook.md # Rules and guidelines
└── Business_Goals.md   # Objectives and metrics
```

## Workflow

### 1. Receive Task

Tasks arrive as `.md` files in `/Needs_Action/` folder:

```markdown
---
type: file_drop
source: report.pdf
priority: high
status: pending
---

# File Drop for Processing

Review and categorize the attached file.
```

### 2. Read and Analyze

```bash
# Read the action file
cat /Needs_Action/FILE_report_2026-02-20.md

# Read Company Handbook for rules
cat Company_Handbook.md

# Read Business Goals for context
cat Business_Goals.md
```

### 3. Create Plan

For multi-step tasks, create a plan:

```markdown
---
created: 2026-02-20T10:00:00Z
status: in_progress
source_file: FILE_report_2026-02-20.md
---

# Plan: Process Report

## Steps
- [x] Read action file
- [ ] Review attached file
- [ ] Categorize by type
- [ ] Extract key information
- [ ] Update Dashboard
- [ ] Move to /Done
```

### 4. Execute Task

Execute within boundaries defined in Company_Handbook.md:

**Auto-Approve Actions:**
- Read/write files within vault
- Move files between vault folders
- Create/update markdown files
- Generate summaries and reports

**Require Approval:**
- Delete any files
- Send external communications
- Process payments
- Access credentials

### 5. Request Approval (if needed)

For sensitive actions, create approval request:

```markdown
---
type: approval_request
action: delete_file
file: /Inbox/old_report.pdf
reason: File older than 90 days
created: 2026-02-20T10:30:00Z
status: pending
---

# Approval Required: Delete File

## Details
- **Action:** Delete file
- **File:** /Inbox/old_report.pdf
- **Reason:** File older than 90 days per retention policy

## To Approve
Move this file to `/Approved/` folder.

## To Reject
Move this file to `/Rejected/` folder.
```

### 6. Log Actions

Every action must be logged:

```json
{
  "timestamp": "2026-02-20T10:30:00Z",
  "action_type": "file_move",
  "actor": "claude_code",
  "source": "/Needs_Action/FILE_report.md",
  "destination": "/Done/FILE_report.md",
  "result": "success"
}
```

### 7. Update Dashboard

Update `Dashboard.md` with:
- Current pending count
- Completed tasks today/week
- Recent activity
- System status

### 8. Mark Complete

Move processed files to `/Done/`:

```bash
mv /Needs_Action/FILE_report.md /Done/
mv /Plans/PLAN_report.md /Done/
```

## Decision Matrix

| Action Type | Auto-Approve | Require Approval |
|-------------|--------------|------------------|
| Create file in vault | ✅ | ❌ |
| Read file in vault | ✅ | ❌ |
| Move within vault | ✅ | ❌ |
| Delete file | ❌ | ✅ |
| Summarize content | ✅ | ❌ |
| Categorize file | ✅ | ❌ |
| Send email | ❌ | ✅ |
| Process payment | ❌ | ✅ |

## Priority Levels

| Priority | Response Time | Examples |
|----------|---------------|----------|
| **High** | < 5 minutes | Urgent, ASAP, invoice, payment |
| **Medium** | < 1 hour | Deadline, review, client request |
| **Low** | < 24 hours | Note, reference, FYI |

## Examples

### Example 1: Process File Drop

**Input:** File dropped in `/Drop_Folder/`

**Action File Created:**
```markdown
---
type: file_drop
source: quarterly_report.xlsx
priority: medium
status: pending
---

# File Drop for Processing

Review and categorize the quarterly report.
```

**Claude's Response:**
1. Read the action file
2. Create plan in `/Plans/`
3. Review the file content
4. Categorize as "Financial Report"
5. Create summary in `/Briefings/`
6. Move to `/Done/`

### Example 2: Approval Request

**Scenario:** Delete old files

**Claude Creates:**
```markdown
---
type: approval_request
action: batch_delete
files: 15 files older than 90 days
---

# Approval Required: Batch Delete

Delete 15 files older than 90 days?
Move to /Approved to confirm.
```

**Human:** Moves file to `/Approved/`

**Claude:** Deletes files, logs action, moves approval file to `/Done/`

## Commands

### Start Processing

```bash
# Process all pending files
python scripts/orchestrator.py /path/to/vault

# Run file watcher
python scripts/filesystem_watcher.py /path/to/vault
```

### Claude Code Integration

```bash
# Point Claude at the vault
cd /path/to/AI_Employee_Vault
claude "Process all files in /Needs_Action/"
```

### Check Status

```bash
# View dashboard
cat Dashboard.md

# View pending items
ls Needs_Action/

# View logs
cat Logs/2026-02-20.json
```

## Error Handling

### Transient Errors
- Retry up to 3 times with exponential backoff
- Log each retry attempt

### Permanent Errors
- Create error file in `/Needs_Action/ERROR_*.md`
- Alert human via notification
- Wait for manual review

### Quarantine
For problematic files:
1. Move to `/Needs_Action/QUARANTINE/`
2. Create error log
3. Alert human

## Best Practices

1. **Always log** - Every action must be traceable
2. **Ask for approval** - When in doubt, request approval
3. **Be transparent** - Document your reasoning
4. **Respect boundaries** - Follow Company_Handbook.md rules
5. **Update Dashboard** - Keep status current
6. **Clean up** - Move completed items to /Done/

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Files not processing | Check orchestrator is running |
| Approval not acted on | Human must move file to /Approved/ |
| Dashboard not updating | Run `update_dashboard()` function |
| Claude not responding | Check claude command is available |

## Security Notes

- Never store credentials in vault
- Use environment variables for API keys
- All actions are logged for audit
- Human-in-the-loop for sensitive operations

---

*AI Employee Bronze Tier Skill v1.0*
*For use with Claude Code*
