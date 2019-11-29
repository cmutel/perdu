from zipfile import ZipFile
import json


def extract_activities(zf):
    activities = [
        json.load(zf.open(o.filename))
        for o in zf.infolist()
        if o.filename.startswith("processes/") and o.filename != "processes/"
    ]
    return [(o["name"], o["description"]) for o in activities]


def extract_flows(zf):
    flows = [
        json.load(zf.open(o.filename))
        for o in zf.infolist()
        if o.filename.startswith("flows/") and o.filename != "flows/"
    ]
    return [(o["name"], "") for o in flows]


def ingest_compressed_jsonld_file(filepath):
    assert filepath.is_file()

    with ZipFile(filepath) as zf:
        results = extract_activities(zf) + extract_flows(zf)
    return sorted(results)
