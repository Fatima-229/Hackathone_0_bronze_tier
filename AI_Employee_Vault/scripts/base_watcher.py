#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Watcher - Abstract base class for all watcher scripts.

All watchers (Gmail, WhatsApp, File System, etc.) inherit from this class
to ensure consistent behavior across the AI Employee system.
"""

import time
import logging
import json
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional


class BaseWatcher(ABC):
    """
    Abstract base class for all watcher implementations.
    
    Watchers monitor external sources and create action files in the vault
    when new items requiring processing are detected.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root directory
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.check_interval = check_interval
        self.running = False
        self.processed_ids: set = set()
        
        # Define folder paths
        self.inbox_folder = self.vault_path / 'Inbox'
        self.needs_action_folder = self.vault_path / 'Needs_Action'
        self.logs_folder = self.vault_path / 'Logs'
        
        # Ensure folders exist
        self.inbox_folder.mkdir(parents=True, exist_ok=True)
        self.needs_action_folder.mkdir(parents=True, exist_ok=True)
        self.logs_folder.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Load previously processed IDs (for deduplication)
        self._load_processed_ids()
        
    def _setup_logging(self):
        """Configure logging for this watcher."""
        log_file = self.logs_folder / f'{self.__class__.__name__}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def _load_processed_ids(self):
        """Load previously processed item IDs from disk."""
        state_file = self.vault_path / 'scripts' / f'{self.__class__.__name__}_state.json'
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    self.processed_ids = set(state.get('processed_ids', []))
                    self.logger.info(f'Loaded {len(self.processed_ids)} previously processed IDs')
            except Exception as e:
                self.logger.warning(f'Could not load state file: {e}')
                self.processed_ids = set()
        else:
            self.processed_ids = set()
            
    def _save_state(self):
        """Save current state to disk for persistence."""
        state_file = self.vault_path / 'scripts' / f'{self.__class__.__name__}_state.json'
        try:
            state = {
                'processed_ids': list(self.processed_ids),
                'last_updated': datetime.now().isoformat()
            }
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.logger.error(f'Could not save state: {e}')
    
    @abstractmethod
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check the external source for new items.
        
        Returns:
            List of new items to process (each item is a dict)
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item: Dict[str, Any]) -> Optional[Path]:
        """
        Create an action file in the Needs_Action folder.
        
        Args:
            item: The item to create an action file for
            
        Returns:
            Path to the created file, or None if failed
        """
        pass
    
    def _generate_filename(self, prefix: str, identifier: str) -> str:
        """
        Generate a standardized filename.
        
        Args:
            prefix: File type prefix (e.g., EMAIL, WHATSAPP)
            identifier: Unique identifier (e.g., message ID, contact name)
            
        Returns:
            Generated filename with .md extension
        """
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        # Sanitize identifier for filename
        safe_id = ''.join(c if c.isalnum() or c in '-_' else '_' for c in identifier)
        return f'{prefix}_{safe_id}_{timestamp}.md'
    
    def _create_metadata_file(self, action_file: Path, metadata: Dict[str, Any]):
        """
        Create a companion metadata file.
        
        Args:
            action_file: The main action file path
            metadata: Metadata to store
        """
        meta_path = action_file.with_suffix('.meta.json')
        try:
            with open(meta_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            self.logger.warning(f'Could not create metadata file: {e}')
    
    def run(self):
        """
        Main run loop for the watcher.
        
        Continuously checks for updates and creates action files.
        """
        self.running = True
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval} seconds')
        
        try:
            while self.running:
                try:
                    # Check for new items
                    items = self.check_for_updates()
                    
                    if items:
                        self.logger.info(f'Found {len(items)} new item(s) to process')
                        
                        for item in items:
                            try:
                                action_file = self.create_action_file(item)
                                if action_file:
                                    self.logger.info(f'Created action file: {action_file.name}')
                            except Exception as e:
                                self.logger.error(f'Error creating action file: {e}')
                    
                    # Save state periodically
                    self._save_state()
                    
                except Exception as e:
                    self.logger.error(f'Error in check loop: {e}')
                
                # Wait before next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info('Watcher stopped by user')
        finally:
            self.running = False
            self._save_state()
            self.logger.info(f'{self.__class__.__name__} stopped')
    
    def stop(self):
        """Stop the watcher."""
        self.running = False
        self.logger.info('Stop signal received')


if __name__ == '__main__':
    # This is an abstract class - cannot be run directly
    print("BaseWatcher is an abstract class. Use a concrete implementation like FileSystemWatcher.")
