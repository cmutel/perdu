from pathlib import Path
import bz2
import json

# Get data from https://www.lcacommons.gov/lca-collaboration/search/page=1&repositoryId=US_Environmental_Protection_Agency%2FUSEEIO
# Click on "download repository as JSON-LD"
# Then extract and use that extracted directory as "source_data_dir"

data_dir = Path(__file__, "..").resolve().parent / "data"


def save_useeio_data(source_data_dir):
    results = []

    # Check correct directory
    assert any("dq_systems" in str(fn) for fn in source_data_dir.iterdir())

    for fn in (source_data_dir / "processes").iterdir():
        data = json.load(open(fn))
        results.append(
            {
                "description": data["description"],
                "code": data["@id"],
                "name": data["name"],
            }
        )

    filepath = data_dir / "useeio.json.bz2"

    with open(filepath, "wb") as f:
        with bz2.BZ2File(f.name, "wb") as b:
            b.write(json.dumps(results).encode("utf-8"))
