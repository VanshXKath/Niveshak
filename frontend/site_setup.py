import sys
from pathlib import Path


def ensure_project_root(caller_file: str) -> None:
    path = Path(caller_file).resolve()
    root = path.parents[2] if path.parent.name == "pages" else path.parents[1]
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
