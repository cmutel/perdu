from ..data import get_gs1_data, get_naics_data
from ..filesystem import base_dir
from .gs1 import (
    create_gs1_search_index,
    search_gs1 as _search_gs1,
    search_corrector_gs1 as _search_corrector_gs1,
)
from .naics import (
    create_naics_search_index,
    search_naics as _search_naics,
    search_corrector_naics as _search_corrector_naics,
)
from functools import partial
from pathlib import Path
import os


gs1_index_dir = base_dir / "gs1"
naics_index_dir = base_dir / "naics"


if not gs1_index_dir.exists():
    print("Creating GS1 search index")
    gs1_index_dir.mkdir()
    create_gs1_search_index(gs1_index_dir, get_gs1_data())

if not naics_index_dir.exists():
    print("Creating NAICS search index")
    naics_index_dir.mkdir()
    create_naics_search_index(naics_index_dir, get_naics_data())


search_gs1 = partial(_search_gs1, dirpath=gs1_index_dir)
search_corrector_gs1 = partial(_search_corrector_gs1, dirpath=gs1_index_dir)
search_naics = partial(_search_naics, dirpath=naics_index_dir)
search_corrector_naics = partial(_search_corrector_naics, dirpath=naics_index_dir)

