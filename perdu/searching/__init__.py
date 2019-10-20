from ..data import get_gs1_data, get_naics_data, get_useeio_data
from ..filesystem import base_dir
from .gs1 import (
    create_gs1_search_index,
    search_gs1 as _search_gs1,
    search_gs1_disjoint as _search_gs1_disjoint,
    search_corrector_gs1 as _search_corrector_gs1,
)
from .naics import (
    create_naics_search_index,
    search_naics as _search_naics,
    search_naics_disjoint as _search_naics_disjoint,
    search_corrector_naics as _search_corrector_naics,
)
from .useeio import (
    create_useeio_search_index,
    search_useeio as _search_useeio,
    search_useeio_disjoint as _search_useeio_disjoint,
    search_corrector_useeio as _search_corrector_useeio,
)
from functools import partial


gs1_index_dir = base_dir / "gs1"
naics_index_dir = base_dir / "naics"
useeio_index_dir = base_dir / "useeio"

if not gs1_index_dir.exists():
    print("Creating GS1 search index")
    gs1_index_dir.mkdir()
    create_gs1_search_index(gs1_index_dir, get_gs1_data())

if not naics_index_dir.exists():
    print("Creating NAICS search index")
    naics_index_dir.mkdir()
    create_naics_search_index(naics_index_dir, get_naics_data())

if not useeio_index_dir.exists():
    print("Creating USEEIO search index")
    useeio_index_dir.mkdir()
    create_useeio_search_index(useeio_index_dir, get_useeio_data())


search_gs1 = partial(_search_gs1, dirpath=gs1_index_dir)
search_gs1_disjoint = partial(_search_gs1_disjoint, dirpath=gs1_index_dir)
search_corrector_gs1 = partial(_search_corrector_gs1, dirpath=gs1_index_dir)
search_naics = partial(_search_naics, dirpath=naics_index_dir)
search_naics_disjoint = partial(_search_naics_disjoint, dirpath=naics_index_dir)
search_corrector_naics = partial(_search_corrector_naics, dirpath=naics_index_dir)
search_useeio = partial(_search_useeio, dirpath=useeio_index_dir)
search_useeio_disjoint = partial(_search_useeio_disjoint, dirpath=useeio_index_dir)
search_corrector_useeio = partial(_search_corrector_useeio, dirpath=useeio_index_dir)
