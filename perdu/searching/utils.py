import unicodedata


REPLACEMENTS = [
    ("market for ", ""),
    ("Market for ", ""),
    (", at regional storehouse", ""),
    (", at plant", ""),
    (", AP-42", ""),
    (", m3", ""),
]
REPLACEMENTS.extend([(", {}".format(x), "") for x in range(1990, 2030)])


def prepare_query(string):
    string = unicodedata.normalize("NFKD", string).strip()
    for x, y in REPLACEMENTS:
        string = string.replace(x, y)
    return string


def add_score(obj):
    new = dict(obj.items())
    new["score"] = obj.score
    return new
