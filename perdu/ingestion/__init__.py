from .bom_excel import ingest_excel_bom_file
from .compressed_jsonld import ingest_compressed_jsonld_file
from .csv import ingest_csv_file

mapping = {
    "bom": ingest_excel_bom_file,
    "csv": ingest_csv_file,
    "jsonld": ingest_compressed_jsonld_file,
}
