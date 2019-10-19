import csv


def ingest_csv_file(filepath):
    assert filepath.is_file()

    data = list(csv.reader(open(filepath)))
    data = [line[:2] for line in data]
    if (data[0][0].lower().strip() == "name") and (
        data[0][1].lower().strip() == "description"
    ):
        data = data[1:]
    return data
