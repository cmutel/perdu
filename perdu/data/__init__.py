from pathlib import Path
import os
import bz2
import json

data_dir = Path(os.path.dirname(__file__))


def get_gs1_data():
    return json.loads((bz2.BZ2File(data_dir / "gs1.json.bz2").read()).decode("utf-8"))


def get_naics_data():
    return json.loads((bz2.BZ2File(data_dir / "naics.json.bz2").read()).decode("utf-8"))
