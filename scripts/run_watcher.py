"""
Folder Watcher Script

Monitors the documents directory for new PDF files and
automatically indexes them.

Usage:
    python scripts/run_watcher.py
    python scripts/run_watcher.py --directory /path/to/watch

This script runs continuously until interrupted (Ctrl+C).
When a new PDF is detected, it triggers the indexing pipeline.

Workflow:
1. User drops PDF into watched folder
2. Watcher detects new file
3. Indexing pipeline runs automatically
4. File is searchable within seconds
"""

import argparse
import sys
import signal
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import DOCUMENTS_DIR, validate_config


# Global flag for graceful shutdown
running = True


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global running
    print("\n\nShutting down watcher...")
    running = False


def on_new_file(file_path: Path):
    """
    Callback when a new PDF is detected.
    
    Args:
        file_path: Path to the new PDF file
    """
    print(f"\n[NEW FILE] {file_path.name}")
    
    try:
        # TODO: Import and use indexing function
        # from scripts.index_documents import index_single_file
        # chunks = index_single_file(file_path)
        # print(f"  ✓ Indexed {chunks} chunks")
        
        print("  → Indexing not yet implemented")
        
    except Exception as e:
        print(f"  ✗ Error indexing: {e}")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Watch a folder for new PDFs and auto-index them"
    )
    parser.add_argument(
        "--directory",
        type=Path,
        default=DOCUMENTS_DIR,
        help=f"Directory to watch (default: {DOCUMENTS_DIR})"
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    # Validate configuration
    config_status = validate_config()
    if not config_status["valid"]:
        print("Configuration error. Missing environment variables:")
        for key in config_status["missing"]:
            print(f"  - {key}")
        print("\nCopy .env.example to .env and fill in your API keys.")
        sys.exit(1)
    
    # Ensure directory exists
    if not args.directory.exists():
        print(f"Creating watch directory: {args.directory}")
        args.directory.mkdir(parents=True, exist_ok=True)
    
    print("=" * 50)
    print("Apicultura RAG - Folder Watcher")
    print("=" * 50)
    print(f"\nWatching: {args.directory}")
    print("Drop PDF files here to auto-index them.")
    print("Press Ctrl+C to stop.\n")
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # TODO: Initialize and start FolderWatcher
        # from src.ingestion import FolderWatcher
        # watcher = FolderWatcher(args.directory, on_new_file)
        # watcher.start(blocking=True)
        
        print("[Not Yet Implemented] FolderWatcher not available")
        print("Implement src/ingestion/watcher.py first.\n")
        
        # Placeholder: keep running until interrupted
        import time
        while running:
            time.sleep(1)
            
    except NotImplementedError as e:
        print(f"\n[Not Yet Implemented] {e}")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
    
    print("Watcher stopped.")


if __name__ == "__main__":
    main()
