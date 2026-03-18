"""
Folder Watcher Module

Monitors a directory for new PDF files and triggers indexing.
Uses the watchdog library for cross-platform file system events.
"""

import time
from pathlib import Path
from typing import Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
import logging

logger = logging.getLogger(__name__)


class PDFHandler(FileSystemEventHandler):
    """Handles file system events for PDF files."""
    
    def __init__(self, callback: Callable[[Path], None], extensions: list):
        self.callback = callback
        self.extensions = extensions
        self._processed = set()  # Avoid processing same file twice
    
    def on_created(self, event: FileCreatedEvent):
        if event.is_directory:
            return
        
        path = Path(event.src_path)
        
        # Check if it's a PDF
        if path.suffix.lower() not in self.extensions:
            return
        
        # Avoid duplicates (some systems fire multiple events)
        if path in self._processed:
            return
        
        self._processed.add(path)
        
        # Wait a moment for file to finish writing
        time.sleep(1)
        
        logger.info(f"New file detected: {path.name}")
        self.callback(path)


class FolderWatcher:
    """
    Watches a folder for new PDF files and triggers a callback.
    
    Usage:
        def on_new_file(path: Path):
            print(f"New file: {path}")
        
        watcher = FolderWatcher(Path("./documents"), on_new_file)
        watcher.start()  # Blocks until Ctrl+C
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
        self.watch_directory = Path(watch_directory)
        self.on_new_file = on_new_file
        self.file_extensions = file_extensions or ['.pdf']
        self._observer = None
    
    def start(self, blocking: bool = True):
        """
        Start watching the directory.
        
        Args:
            blocking: If True, blocks until interrupted. 
                     If False, runs in background thread.
        """
        if not self.watch_directory.exists():
            self.watch_directory.mkdir(parents=True, exist_ok=True)
        
        handler = PDFHandler(self.on_new_file, self.file_extensions)
        self._observer = Observer()
        self._observer.schedule(handler, str(self.watch_directory), recursive=False)
        self._observer.start()
        
        logger.info(f"Watching {self.watch_directory} for new PDFs...")
        
        if blocking:
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop()
    
    def stop(self):
        """Stop the folder watcher."""
        if self._observer:
            self._observer.stop()
            self._observer.join()
            logger.info("Watcher stopped")