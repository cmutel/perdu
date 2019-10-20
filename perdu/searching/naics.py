from .utils import prepare_query, add_score
from whoosh.fields import TEXT, ID, Schema
from whoosh import index
from whoosh.qparser import MultifieldParser, OrGroup
import os


naics_schema = Schema(
    description=TEXT(stored=True),
    code=ID(stored=True),
    name=TEXT(stored=True, sortable=True),
)


def get_index(dirpath):
    try:
        return index.open_dir(dirpath)
    except index.EmptyIndexError:
        if not os.path.exists(dirpath):
            os.mkdir(dirpath)
        return index.create_in(dirpath, naics_schema)


def create_naics_search_index(dirpath, data):
    FIELDS = ("description", "code", "name")

    indx = get_index(dirpath)
    writer = indx.writer()
    for record in data:
        if len(record["code"]) != 6:
            continue
        writer.add_document(**{k: v for k, v in record.items() if k in FIELDS})
    writer.commit()


def search_naics(string, dirpath, limit=5):
    indx = get_index(dirpath)
    string = prepare_query(string)

    boosts = {"name": 5, "description": 2}

    qp = MultifieldParser(list(boosts), indx.schema, fieldboosts=boosts, group=OrGroup)

    with indx.searcher() as searcher:
        return [add_score(obj) for obj in searcher.search(qp.parse(string))]


def search_naics_disjoint(string, dirpath, limit=5):
    indx = get_index(dirpath)
    string = prepare_query(string)

    boosts = {"name": 5, "description": 2}

    qp = DisMaxParser(boosts, indx.schema)

    with indx.searcher() as searcher:
        return [add_score(obj) for obj in searcher.search(qp.parse(string))]


def search_corrector_naics(string, dirpath, limit=3):
    indx = get_index(dirpath)

    with indx.searcher() as s:
        corrector = s.corrector("description")
        possibilities = [
            corrector.suggest(term, limit=limit)
            for term in string.split(" ")
            if term.lower() not in {"and", "or"}
        ]

    return possibilities
