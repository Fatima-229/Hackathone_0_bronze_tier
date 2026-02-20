#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orchestrator - Master process for the AI Employee system.

The orchestrator:
1. Monitors the Needs_Action folder for new items
2. Triggers Claude Code to process items
3. Updates the Dashboard.md with current status
4. Manages the approval workflow
5. Logs all actions

Usage:
    python orchestrator.py /path/to/vault
"""

import os
import sys
import json
import time
import logging
import subprocess
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List


class Orchestrator:
    """
    Main orchestrator for the AI Employee system.
    
    Coordinates between watchers, Claude Code, and the approval workflow.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 30):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path: Path to the Obsidian vault root directory
            check_interval: Seconds between orchestration cycles (default: 30)
        """
        self.vault_path = Path(vault_path)
        self.check_interval = check_interval
        self.running = False
        
        # Define folder paths
        self.inbox_folder = self.vault_path / 'Inbox'
        self.needs_action_folder = self.vault_path / 'Needs_Action'
        self.plans_folder = self.vault_path / 'Plans'
        self.approved_folder = self.vault_path / 'Approved'
        self.rejected_folder = self.vault_path / 'Rejected'
        self.done_folder = self.vault_path / 'Done'
        self.logs_folder = self.vault_path / 'Logs'
        self.briefings_folder = self.vault_path / 'Briefings'
        
        # Ensure all folders exist
        for folder in [self.inbox_folder, self.needs_action_folder, self.plans_folder,
                       self.approved_folder, self.rejected_folder, self.done_folder,
                       self.logs_folder, self.briefings_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Dashboard file
        self.dashboard_file = self.vault_path / 'Dashboard.md'
        
        # Setup logging
        self._setup_logging()
        
        # Track processed files to avoid duplicates
        self.processed_files: set = set()
        self._load_processed_files()
        
        # Claude Code configuration
        self.claude_command = os.environ.get('CLAUDE_COMMAND', 'claude')
        self.max_claude_iterations = int(os.environ.get('MAX_CLAUDE_ITERATIONS', '5'))
        
        self.logger.info(f'Orchestrator initialized')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Claude command: {self.claude_command}')
    
    def _setup_logging(self):
        """Configure logging."""
        log_file = self.logs_folder / 'orchestrator.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('Orchestrator')
    
    def _load_processed_files(self):
        """Load list of processed files from disk."""
        state_file = self.vault_path / 'scripts' / 'orchestrator_state.json'
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    self.processed_files = set(state.get('processed_files', []))
            except Exception as e:
                self.logger.warning(f'Could not load state: {e}')
                self.processed_files = set()
    
    def _save_state(self):
        """Save current state to disk."""
        state_file = self.vault_path / 'scripts' / 'orchestrator_state.json'
        try:
            state = {
                'processed_files': list(self.processed_files),
                'last_updated': datetime.now().isoformat()
            }
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.logger.error(f'Could not save state: {e}')
    
    def _count_files_in_folder(self, folder: Path) -> int:
        """Count .md files in a folder."""
        try:
            return len([f for f in folder.iterdir() if f.suffix == '.md' and f.is_file()])
        except Exception:
            return 0
    
    def _get_today_completed_count(self) -> int:
        """Count files moved to Done today."""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            count = 0
            for f in self.done_folder.iterdir():
                if f.suffix == '.md' and today in f.name:
                    count += 1
            return count
        except Exception:
            return 0
    
    def _get_week_completed_count(self) -> int:
        """Count files moved to Done this week."""
        try:
            week_ago = datetime.now() - timedelta(days=7)
            count = 0
            for f in self.done_folder.iterdir():
                if f.suffix == '.md':
                    try:
                        mtime = datetime.fromtimestamp(f.stat().st_mtime)
                        if mtime >= week_ago:
                            count += 1
                    except Exception:
                        pass
            return count
        except Exception:
            return 0
    
    def update_dashboard(self):
        """
        Update the Dashboard.md with current status.
        """
        try:
            if not self.dashboard_file.exists():
                self.logger.warning('Dashboard.md not found')
                return
            
            # Count files in each folder
            inbox_count = self._count_files_in_folder(self.inbox_folder)
            needs_action_count = self._count_files_in_folder(self.needs_action_folder)
            pending_approval_count = self._count_files_in_folder(self.approved_folder)
            approved_count = self._count_files_in_folder(self.approved_folder)
            active_plans_count = self._count_files_in_folder(self.plans_folder)
            completed_today = self._get_today_completed_count()
            completed_this_week = self._get_week_completed_count()
            
            # Read current dashboard
            content = self.dashboard_file.read_text()
            
            # Update placeholders
            replacements = {
                '{{pending_count}}': str(needs_action_count),
                '{{active_plans_count}}': str(active_plans_count),
                '{{completed_today}}': str(completed_today),
                '{{completed_this_week}}': str(completed_this_week),
                '{{inbox_count}}': str(inbox_count),
                '{{needs_action_count}}': str(needs_action_count),
                '{{pending_approval_count}}': str(pending_approval_count),
                '{{approved_count}}': str(approved_count),
                '{{watcher_status}}': '🟢 Running' if self.running else '🔴 Stopped',
                '{{orchestrator_status}}': '🟢 Running' if self.running else '🔴 Stopped',
                '{{last_sync}}': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '{{timestamp}}': datetime.now().isoformat()
            }
            
            for placeholder, value in replacements.items():
                content = content.replace(placeholder, value)
            
            # Write updated dashboard
            self.dashboard_file.write_text(content)
            
            self.logger.debug('Dashboard updated')
            
        except Exception as e:
            self.logger.error(f'Error updating dashboard: {e}')
    
    def _log_action(self, action_type: str, details: Dict[str, Any], result: str = 'success'):
        """
        Log an action to the daily log file.
        
        Args:
            action_type: Type of action (e.g., 'file_processed', 'approval_requested')
            details: Action details
            result: 'success' or 'error'
        """
        try:
            log_file = self.logs_folder / f'{datetime.now().strftime("%Y-%m-%d")}.json'
            
            # Load existing logs
            logs = []
            if log_file.exists():
                try:
                    with open(log_file, 'r') as f:
                        logs = json.load(f)
                except Exception:
                    logs = []
            
            # Create new log entry
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'action_type': action_type,
                'actor': 'orchestrator',
                'parameters': details,
                'result': result
            }
            
            logs.append(log_entry)
            
            # Save logs
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            self.logger.error(f'Error logging action: {e}')
    
    def get_pending_files(self) -> List[Path]:
        """
        Get list of pending action files.
        
        Returns:
            List of file paths in Needs_Action folder
        """
        try:
            files = [f for f in self.needs_action_folder.iterdir() 
                    if f.suffix == '.md' and f.is_file()]
            return sorted(files, key=lambda f: f.stat().st_mtime)
        except Exception as e:
            self.logger.error(f'Error getting pending files: {e}')
            return []
    
    def get_approved_files(self) -> List[Path]:
        """
        Get list of approved action files.
        
        Returns:
            List of file paths in Approved folder
        """
        try:
            files = [f for f in self.approved_folder.iterdir() 
                    if f.suffix == '.md' and f.is_file()]
            return sorted(files, key=lambda f: f.stat().st_mtime)
        except Exception as e:
            self.logger.error(f'Error getting approved files: {e}')
            return []
    
    def process_with_claude(self, action_file: Path) -> bool:
        """
        Process an action file with Claude Code.
        
        Args:
            action_file: Path to the action file to process
            
        Returns:
            True if processing succeeded, False otherwise
        """
        try:
            self.logger.info(f'Processing with Claude: {action_file.name}')
            
            # Create a prompt file for Claude
            prompt = f'''
You are an AI Employee assistant. Process the following action file and complete the task.

Action file: {action_file}

Instructions:
1. Read the action file and understand what needs to be done
2. Create a plan in /Plans/ folder if this is a multi-step task
3. Execute the task step by step
4. Update the Dashboard.md with progress
5. When complete, move the action file to /Done/ folder
6. Log your actions in /Logs/

Remember:
- Always ask for approval before sensitive actions (payments, external communications)
- Log every action you take
- Be transparent about what you're doing
- If you need human approval, create a file in /Pending_Approval/

Start processing now. Output your thought process and actions.
'''
            
            # Check if claude command exists
            try:
                result = subprocess.run(
                    ['where', self.claude_command] if sys.platform == 'win32' else ['which', self.claude_command],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    self.logger.warning(f'Claude command "{self.claude_command}" not found. Skipping processing.')
                    self._log_action('claude_process', {'file': str(action_file)}, 'skipped_claude_not_found')
                    return False
            except Exception:
                pass
            
            # For Bronze tier, we'll simulate Claude processing
            # In production, this would actually call Claude Code
            self.logger.info(f'[SIMULATED] Claude would process: {action_file.name}')
            
            # Create a plan file
            plan_file = self.plans_folder / f'PLAN_{action_file.stem}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
            plan_content = f'''---
created: {datetime.now().isoformat()}
status: in_progress
source_file: {action_file.name}
---

# Plan for Processing: {action_file.name}

## Objective
Process the action file and complete the required task.

## Steps
- [x] Read action file
- [ ] Analyze requirements
- [ ] Execute required actions
- [ ] Update Dashboard
- [ ] Move to /Done when complete

## Notes
*Plan created by Orchestrator (Bronze Tier - Claude simulation)*
'''
            plan_file.write_text(plan_content)
            
            # Update action file status
            content = action_file.read_text()
            if 'status: pending' in content:
                content = content.replace('status: pending', 'status: in_progress')
                action_file.write_text(content)
            
            self._log_action('claude_process', {'file': str(action_file), 'plan': str(plan_file)}, 'success')
            
            return True
            
        except Exception as e:
            self.logger.error(f'Error processing with Claude: {e}')
            self._log_action('claude_process', {'file': str(action_file), 'error': str(e)}, 'error')
            return False
    
    def move_to_done(self, file_path: Path):
        """
        Move a completed file to the Done folder.
        
        Args:
            file_path: Path to the file to move
        """
        try:
            dest = self.done_folder / file_path.name
            shutil.move(str(file_path), str(dest))
            self.logger.info(f'Moved to Done: {file_path.name}')
            self._log_action('move_to_done', {'file': str(file_path)}, 'success')
        except Exception as e:
            self.logger.error(f'Error moving file to Done: {e}')
    
    def run(self):
        """
        Main orchestration loop.
        """
        self.running = True
        self.logger.info('Starting Orchestrator')
        
        try:
            while self.running:
                try:
                    # Update dashboard
                    self.update_dashboard()
                    
                    # Get pending files
                    pending_files = self.get_pending_files()
                    
                    if pending_files:
                        self.logger.info(f'Found {len(pending_files)} pending file(s)')
                        
                        for action_file in pending_files:
                            # Skip if already processed
                            if str(action_file) in self.processed_files:
                                continue
                            
                            # Process with Claude
                            success = self.process_with_claude(action_file)
                            
                            if success:
                                self.processed_files.add(str(action_file))
                    
                    # Check for approved files (ready for action)
                    approved_files = self.get_approved_files()
                    if approved_files:
                        self.logger.info(f'Found {len(approved_files)} approved file(s) ready for action')
                        # In Bronze tier, just move to Done
                        for approved_file in approved_files:
                            self.move_to_done(approved_file)
                    
                    # Save state
                    self._save_state()
                    
                except Exception as e:
                    self.logger.error(f'Error in orchestration cycle: {e}')
                
                # Wait before next cycle
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info('Orchestrator stopped by user')
        finally:
            self.running = False
            self._save_state()
            self.update_dashboard()
            self.logger.info('Orchestrator stopped')
    
    def stop(self):
        """Stop the orchestrator."""
        self.running = False
        self.logger.info('Stop signal received')


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='AI Employee Orchestrator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
    python orchestrator.py /path/to/vault
    python orchestrator.py /path/to/vault --interval 60
        '''
    )
    
    parser.add_argument(
        'vault_path',
        type=str,
        help='Path to the Obsidian vault root directory'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=30,
        help='Orchestration interval in seconds (default: 30)'
    )
    
    args = parser.parse_args()
    
    # Create and run orchestrator
    orchestrator = Orchestrator(
        vault_path=args.vault_path,
        check_interval=args.interval
    )
    
    try:
        orchestrator.run()
    except KeyboardInterrupt:
        orchestrator.stop()
        print('\nOrchestrator stopped.')


if __name__ == '__main__':
    main()
