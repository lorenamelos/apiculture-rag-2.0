"""
Folder Watcher Module

Monitors a directory for new PDF files and triggers indexing.
Uses the watchdog library for cross-platform file system events.

Why auto-ingestion?
- User drops file → automatically indexed
- No manual intervention needed
- Production-ready workflow
- Handles the client's "drop and forget" requirement
"""

from pathlib import Path
from typing import Callable, Optional
import logging

logger = logging.getLogger(__name__)


class FolderWatcher:
    """
    Watches a folder for new PDF files and triggers a callback.
    
    Usage:
        def on_new_file(path: Path):
            print(f"New file: {path}")
        
        watcher = FolderWatcher(Path("./documents"), on_new_file)
        watcher.start()  # Blocks until interrupted
    """
    
    def __init__(
        self, 
        watch_directory: Path, 
        on_new_file: Callable[[Path], None],
        file_extensions: Optional[list] = None
    ):
        """
        Initialize the folder watcher.
        
        Args:
            watch_directory: Directory to monitor
            on_new_file: Callback function when new file is detected
            file_extensions: List of extensions to watch (default: ['.pdf'])
        """
        self.watch_directory = watch_directory
        self.on_new_file = on_new_file
        self.file_extensions = file_extensions or ['.pdf']
        self._observer = None
        # TODO: Initialize watchdog observer
    
    def start(self, blocking: bool = True):
        """
        Start watching the directory.
        
        Args:
            blocking: If True, blocks until interrupted. 
                     If False, runs in background thread.
        """
        # TODO: Implement watcher start
        raise NotImplementedError("Watcher not yet implemented")
    
    def stop(self):
        """Stop the folder watcher."""
        # TODO: Implement watcher stop
        raise NotImplementedError("Watcher stop not yet implemented")
    
    def _is_valid_file(self, path: Path) -> bool:
        """Check if file should trigger the callback."""
        return path.suffix.lower() in self.file_extensions
