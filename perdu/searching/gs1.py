from .utils import prepare_query, add_score
from whoosh.fields import TEXT, ID, Schema
from whoosh import index
from whoosh.qparser import MultifieldParser, DisMaxParser, OrGroup
import os

gs1_schema = Schema(
    segment=TEXT(stored=True, sortable=True),
    family=TEXT(stored=True, sortable=True),
    klass=TEXT(stored=True, sortable=True),
    brick=TEXT(stored=True, sortable=True),
    code=ID(stored=True),
    definition=TEXT(stored=True),
)


def get_index(dirpath):
    try:
        return index.open_dir(dirpath)
    except index.EmptyIndexError:
        if not os.path.exists(dirpath):
            os.mkdir(dirpath)
        return index.create_in(dirpath, gs1_schema)


def create_gs1_search_index(dirpath, data):
    FIELDS = ("segment", "family", "klass", "brick", "code", "definition")

    indx = get_index(dirpath)
    writer = indx.writer()
    for record in data:
        if record["level"] != "brick":
            continue
        writer.add_document(**{k: v for k, v in record.items() if k in FIELDS})
    writer.commit()


def search_gs1(string, dirpath, limit=5):
    indx = get_index(dirpath)
    string = prepare_query(string)

    boosts = {"brick": 5, "klass": 3, "family": 2, "segment": 1, "definition": 2}

    qp = MultifieldParser(list(boosts), indx.schema, fieldboosts=boosts, group=OrGroup)

    with indx.searcher() as searcher:
        return [add_score(obj) for obj in searcher.search(qp.parse(string))]


def search_gs1_disjoint(string, dirpath, limit=5):
    indx = get_index(dirpath)
    string = prepare_query(string)

    boosts = {"brick": 5, "klass": 3, "family": 2, "segment": 1, "definition": 2}

    qp = DisMaxParser(boosts, indx.schema)

    with indx.searcher() as searcher:
        return [add_score(obj) for obj in searcher.search(qp.parse(string))]


def search_corrector_gs1(string, dirpath, limit=3):
    indx = get_index(dirpath)

    with indx.searcher() as s:
        corrector = s.corrector("definition")
        possibilities = [
            corrector.suggest(term, limit=limit) for term in string.split(" ")
        ]

    return possibilities
