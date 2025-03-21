import os
from pathlib import Path

from src.particle.particle_generator import generate_particle
from src.particle.particle_support import logger
from src.helpers.gitignore_parser import load_gitignore

def process_directory(root_dir: str, rich: bool = True) -> dict:
    """
    Process all JavaScript/JSX files in a directory recursively.
    
    Args:
        root_dir: Root directory to process
        rich: If True, include detailed metadata
        
    Returns:
        dict: Summary of operation
    """
    logger.info(f"Processing directory: {root_dir}")
    
    root_path = Path(root_dir)
    
    # If the given path is a file, not a directory, process just that file
    if root_path.is_file():
        logger.info(f"Processing single file: {root_path}")
        try:
            result = generate_particle(str(root_path), rich)
            if result.get("isError", True):
                return {
                    "summary": f"Error processing file: {result.get('error', 'Unknown error')}",
                    "status": "ERROR",
                    "modified_count": 0,
                    "errors": [f"{root_path}: {result.get('error', 'Unknown error')}"],
                    "js_files_found": 1
                }
            else:
                return {
                    "summary": f"Successfully processed file {root_path.name}",
                    "status": "OK", 
                    "modified_count": 1,
                    "errors": [],
                    "js_files_found": 1
                }
        except Exception as e:
            return {
                "summary": f"Error processing file: {str(e)}",
                "status": "ERROR",
                "modified_count": 0,
                "errors": [f"{root_path}: {str(e)}"],
                "js_files_found": 1
            }
    
    # Process as a directory
    gitignore = load_gitignore(root_dir)
    modified_count = 0
    errors = []
    js_files_found = 0

    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith((".jsx", ".js")):
                js_files_found += 1
                file_path = Path(root) / file
                rel_path = file_path.relative_to(root_path)
                logger.debug(f"Found JS/JSX file: {rel_path}")
                
                if gitignore.match_file(rel_path):
                    logger.debug(f"Skipped (gitignore): {rel_path}")
                else:
                    try:
                        result = generate_particle(str(file_path), rich)
                        if result.get("isError", True):
                            errors.append(f"{rel_path}: {result.get('error', 'Unknown error')}")
                        else:
                            modified_count += 1
                            logger.info(f"Particled: {rel_path}")
                    except Exception as e:
                        errors.append(f"{rel_path}: {e}")

    if js_files_found == 0:
        logger.warning(f"No JS/JSX files found in {root_dir}")
    
    status = "OK" if not errors else "PARTIAL"
    summary = f"Modified {modified_count} files"
    if errors:
        summary += f", {len(errors)} errors: {', '.join(errors[:3])}" + (len(errors) > 3 and "..." or "")
    logger.info(f"Directory processing summary: {summary}")
    
    return {
        "modified_count": modified_count,
        "errors": errors,
        "js_files_found": js_files_found,
        "status": status,
        "summary": summary
    }
