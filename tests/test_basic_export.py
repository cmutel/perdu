from fixtures.match_fixture import test_data
from pathlib import Path
from perdu.semantic_web import write_matching_to_rdf
import tempfile


def test_ttl_export(monkeypatch):
    with tempfile.TemporaryDirectory() as td:
        monkeypatch.setattr("perdu.semantic_web.export_dir", Path(td))
        write_matching_to_rdf(test_data)


def test_jsonld_export(monkeypatch):
    with tempfile.TemporaryDirectory() as td:
        monkeypatch.setattr("perdu.semantic_web.export_dir", Path(td))
        write_matching_to_rdf(test_data, "json-ld", "json")
