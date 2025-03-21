from pathlib import Path
import os
from src.particle.particle_support import app_path, logger
from src.helpers.gitignore_parser import load_gitignore

def list_dir(path: str) -> dict:
    logger.info(f"Received list_dir request with path: {path}")
    dir_path = Path(app_path) / path
    if not dir_path.exists():
        return {"error": f"Path {path} does not exist at {dir_path}"}
    if not dir_path.is_dir():
        return {"error": f"Path {path} is not a directory at {dir_path}"}
    entries = []
    for entry in dir_path.iterdir():
        rel_path = os.path.relpath(entry, app_path)
        if entry.name.startswith("."):
            logger.debug(f"Skipping {rel_path} (hidden)")
            continue
        child_count = len(list(entry.iterdir())) if entry.is_dir() else 0
        entries.append({
            "name": entry.name,
            "is_dir": entry.is_dir(),
            "children": child_count if entry.is_dir() else None
        })
    logger.debug(f"Entries in {path}: {entries}")
    return {"entries": entries, "source": "server"}

def scan_directory(root: Path, extensions: tuple = (".js", ".jsx")) -> list:
    """Scan directory for JS files, respecting .gitignore."""
    gitignore = load_gitignore(str(root))
    files = []
    for path in root.rglob("*"):
        rel_path = path.relative_to(root)
        if gitignore.match_file(rel_path):
            logger.debug(f"Skipping {rel_path} (gitignore)")
            continue
        if path.is_file() and path.suffix in extensions:
            files.append(str(rel_path))
    logger.info(f"Scanned {root}: found {len(files)} JS files")
    return files