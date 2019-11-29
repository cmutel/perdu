import pandas as pd
import itertools


def ingest_excel_bom_file(filepath, column="Part Name"):
    assert filepath.is_file()

    data = set()

    xl = pd.ExcelFile(filepath)
    for sheet_name in xl.sheet_names:
        df = xl.parse(sheet_name)
        data.update(set(df["Part Name"].unique()))

    return list(
        zip(sorted(filter(lambda x: isinstance(x, str), data)), itertools.repeat(""))
    )
