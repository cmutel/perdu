from .utils import prepare_query, add_score
from whoosh.fields import TEXT, ID, Schema
from whoosh import index
from whoosh.qparser import MultifieldParser, OrGroup, DisMaxParser
import os


useeio_schema = Schema(
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
        return index.create_in(dirpath, useeio_schema)


def create_useeio_search_index(dirpath, data):
    indx = get_index(dirpath)
    writer = indx.writer()
    for record in data:
        writer.add_document(**record)
    writer.commit()


def search_useeio(string, dirpath, limit=5):
    indx = get_index(dirpath)
    string = prepare_query(string)

    boosts = {"name": 5, "description": 2}

    qp = MultifieldParser(list(boosts), indx.schema, fieldboosts=boosts, group=OrGroup)

    with indx.searcher() as searcher:
        return [add_score(obj) for obj in searcher.search(qp.parse(string))]


def search_useeio_disjoint(string, dirpath, limit=5):
    indx = get_index(dirpath)
    string = prepare_query(string)

    boosts = {"name": 5, "description": 2}

    qp = DisMaxParser(boosts, indx.schema)

    with indx.searcher() as searcher:
        return [add_score(obj) for obj in searcher.search(qp.parse(string))]


def search_corrector_useeio(string, dirpath, limit=3):
    indx = get_index(dirpath)

    with indx.searcher() as s:
        corrector = s.corrector("description")
        possibilities = [
            corrector.suggest(term, limit=limit)
            for term in string.split(" ")
            if term.lower() not in {"and", "or"}
        ]

    return possibilities
