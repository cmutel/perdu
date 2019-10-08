import appdirs
from pathlib import Path

base_dir = Path(appdirs.user_data_dir("perdu-search", "perdu"))

if not base_dir.exists():
    base_dir.mkdir()
