"""Publish a complete result without replacing an existing destination."""
import os
from pathlib import Path
import tempfile


def publish_bytes(path: Path, content: bytes) -> None:
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix="." + path.name + ".", suffix=".tmp", delete=False) as file:
            temporary = Path(file.name)
            file.write(content)
            file.flush()
            os.fsync(file.fileno())
        # Linking is atomic and fails if a competing/existing result has this name.
        os.link(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
