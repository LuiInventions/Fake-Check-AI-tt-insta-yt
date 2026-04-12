import os
import logging

logger = logging.getLogger(__name__)

def cleanup_files(*file_paths: str):
    """
    Safely cleanup files with path traversal protection
    """
    # Define allowed base directories
    allowed_dirs = [
        '/app/data/videos',
        '/app/data/frames',
        '/tmp'
    ]

    for path in file_paths:
        if not path:
            continue

        try:
            # Resolve to absolute path and check for path traversal
            abs_path = os.path.abspath(path)

            # Check if path is within allowed directories
            is_allowed = any(abs_path.startswith(allowed_dir) for allowed_dir in allowed_dirs)

            if not is_allowed:
                logger.warning(f"Attempted to delete file outside allowed directories: {abs_path}")
                continue

            # Additional safety check: no parent directory references
            if '..' in path:
                logger.warning(f"Path traversal attempt detected: {path}")
                continue

            if os.path.exists(abs_path) and os.path.isfile(abs_path):
                os.remove(abs_path)
                logger.info(f"Cleaned up file: {abs_path}")
        except OSError as e:
            logger.error(f"Failed to cleanup file {path}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error cleaning up {path}: {e}")
