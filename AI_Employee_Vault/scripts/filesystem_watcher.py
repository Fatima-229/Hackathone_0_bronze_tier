#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File System Watcher - Monitors a drop folder for new files.

This watcher monitors a designated "drop folder" for new files. When a file
is added, it creates an action file in the Needs_Action folder for the AI
to process.

Usage:
    python filesystem_watcher.py /path/to/vault /path/to/drop_folder
"""

import os
import sys
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher


class FileSystemWatcher(BaseWatcher):
    """
    Watcher that monitors a drop folder for new files.
    
    When a new file is detected, it creates an action file in the vault
    and optionally copies the file to the vault for processing.
    """
    
    def __init__(self, vault_path: str, drop_folder: Optional[str] = None, check_interval: int = 30):
        """
        Initialize the file system watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root directory
            drop_folder: Path to the folder to monitor (default: vault/Drop_Folder)
            check_interval: Seconds between checks (default: 30)
        """
        super().__init__(vault_path, check_interval)
        
        # Set up drop folder
        if drop_folder:
            self.drop_folder = Path(drop_folder)
        else:
            self.drop_folder = self.vault_path / 'Drop_Folder'
        
        # Ensure drop folder exists
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        
        # Track file hashes to detect new/modified files
        self.file_hashes: Dict[str, str] = {}
        self._load_file_hashes()
        
        # Priority keywords for automatic classification
        self.priority_keywords = {
            'high': ['urgent', 'asap', 'emergency', 'important', 'priority'],
            'medium': ['invoice', 'payment', 'deadline', 'review'],
            'low': ['note', 'reference', 'info', 'FYI']
        }
        
        self.logger.info(f'Drop folder: {self.drop_folder}')
    
    def _load_file_hashes(self):
        """Load previously recorded file hashes."""
        state_file = self.vault_path / 'scripts' / 'filesystem_watcher_hashes.json'
        if state_file.exists():
            try:
                import json
                with open(state_file, 'r') as f:
                    self.file_hashes = json.load(f)
                    self.logger.info(f'Loaded {len(self.file_hashes)} file hashes')
            except Exception as e:
                self.logger.warning(f'Could not load file hashes: {e}')
                self.file_hashes = {}
    
    def _save_file_hashes(self):
        """Save current file hashes to disk."""
        state_file = self.vault_path / 'scripts' / 'filesystem_watcher_hashes.json'
        try:
            import json
            with open(state_file, 'w') as f:
                json.dump(self.file_hashes, f, indent=2)
        except Exception as e:
            self.logger.error(f'Could not save file hashes: {e}')
    
    def _calculate_hash(self, file_path: Path) -> str:
        """
        Calculate MD5 hash of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MD5 hash string
        """
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.logger.error(f'Error calculating hash for {file_path}: {e}')
            return ''
    
    def _detect_priority(self, filename: str, content: str = '') -> str:
        """
        Detect priority level based on filename and content.
        
        Args:
            filename: Name of the file
            content: Optional content to analyze
            
        Returns:
            Priority level: 'high', 'medium', or 'low'
        """
        text = f'{filename} {content}'.lower()
        
        # Check for high priority keywords
        for keyword in self.priority_keywords['high']:
            if keyword in text:
                return 'high'
        
        # Check for medium priority keywords
        for keyword in self.priority_keywords['medium']:
            if keyword in text:
                return 'medium'
        
        return 'low'
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check the drop folder for new files.
        
        Returns:
            List of new file information dictionaries
        """
        new_files = []
        
        try:
            # Get all files in drop folder
            files = [f for f in self.drop_folder.iterdir() if f.is_file()]
            
            for file_path in files:
                # Skip hidden files and temporary files
                if file_path.name.startswith('.') or file_path.suffix == '.tmp':
                    continue
                
                # Calculate hash
                current_hash = self._calculate_hash(file_path)
                if not current_hash:
                    continue
                
                # Check if file is new or modified
                stored_hash = self.file_hashes.get(str(file_path))
                
                if stored_hash != current_hash:
                    # New or modified file detected
                    self.logger.info(f'New/modified file detected: {file_path.name}')
                    
                    # Read file content (if text file)
                    content = ''
                    try:
                        if file_path.suffix in ['.txt', '.md', '.json', '.csv', '.log']:
                            content = file_path.read_text(errors='ignore')[:1000]  # First 1000 chars
                    except Exception as e:
                        self.logger.warning(f'Could not read file content: {e}')
                    
                    # Detect priority
                    priority = self._detect_priority(file_path.name, content)
                    
                    new_files.append({
                        'file_path': str(file_path),
                        'file_name': file_path.name,
                        'file_size': file_path.stat().st_size,
                        'file_type': file_path.suffix,
                        'hash': current_hash,
                        'priority': priority,
                        'content_preview': content[:200] if content else ''
                    })
                    
                    # Update stored hash
                    self.file_hashes[str(file_path)] = current_hash
            
            # Save updated hashes
            self._save_file_hashes()
            
        except Exception as e:
            self.logger.error(f'Error checking drop folder: {e}')
        
        return new_files
    
    def create_action_file(self, item: Dict[str, Any]) -> Optional[Path]:
        """
        Create an action file in the Needs_Action folder.
        
        Args:
            item: File information dictionary
            
        Returns:
            Path to the created action file, or None if failed
        """
        try:
            # Generate filename
            filename = self._generate_filename('FILE', item['file_name'])
            action_file = self.needs_action_folder / filename
            
            # Create action file content
            content = f'''---
type: file_drop
source: {item['file_name']}
file_path: {item['file_path']}
file_size: {item['file_size']} bytes
file_type: {item['file_type']}
priority: {item['priority']}
detected: {datetime.now().isoformat()}
status: pending
hash: {item['hash']}
---

# File Drop for Processing

## Source File
- **Name:** {item['file_name']}
- **Size:** {item['file_size']} bytes
- **Type:** {item['file_type']}
- **Priority:** {item['priority'].upper()}

## Content Preview
```
{item['content_preview'] if item['content_preview'] else '(Binary file or could not read)'}
```

## Suggested Actions
- [ ] Review file content
- [ ] Categorize file
- [ ] Take appropriate action
- [ ] Move to /Done when complete

## Notes
*Add any notes or observations here.*

---
*Auto-generated by FileSystemWatcher*
'''
            
            # Write action file
            action_file.write_text(content)
            
            # Copy source file to vault for reference
            try:
                dest_folder = self.vault_path / 'Inbox'
                dest_folder.mkdir(parents=True, exist_ok=True)
                dest_file = dest_folder / f'copy_{item["file_name"]}'
                shutil.copy2(item['file_path'], dest_file)
                self.logger.info(f'Copied source file to {dest_file}')
            except Exception as e:
                self.logger.warning(f'Could not copy source file: {e}')
            
            return action_file
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            return None


def main():
    """Main entry point for running the watcher."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='File System Watcher for AI Employee',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
    python filesystem_watcher.py /path/to/vault
    python filesystem_watcher.py /path/to/vault /path/to/drop_folder
    python filesystem_watcher.py /path/to/vault --interval 60
        '''
    )
    
    parser.add_argument(
        'vault_path',
        type=str,
        help='Path to the Obsidian vault root directory'
    )
    parser.add_argument(
        'drop_folder',
        type=str,
        nargs='?',
        default=None,
        help='Path to the drop folder to monitor (default: vault/Drop_Folder)'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=30,
        help='Check interval in seconds (default: 30)'
    )
    
    args = parser.parse_args()
    
    # Create and run watcher
    watcher = FileSystemWatcher(
        vault_path=args.vault_path,
        drop_folder=args.drop_folder,
        check_interval=args.interval
    )
    
    try:
        watcher.run()
    except KeyboardInterrupt:
        watcher.stop()
        print('\nWatcher stopped.')


if __name__ == '__main__':
    main()
