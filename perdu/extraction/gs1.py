from lxml import objectify
from pathlib import Path
import bz2
import json
import os
import unicodedata


_ = lambda s: unicodedata.normalize("NFKD", s).strip()


def drop_excludes(s):
    """Drop sentences that have the word 'excludes' in them"""
    return ".".join(frag for frag in s.split(".") if 'excludes' not in frag.lower())


def get_dict_for_element(o):
    dct = {
        key: (_(o.get(key)) or None)
        for key in ['text', 'code']
    }
    dct['original definition'] = _(o.get('definition')) or None
    dct['definition'] = drop_excludes(dct['original definition'] or '')
    return dct


def extract_gs1_data(filepath):
    """Filepath is absolute filepath to the file "GPC Schema 2018-12 EN.xml"

    It can be downloaded from https://www.gs1.org/sites/default/files/docs/gpc/en_2018-12.zip.

    """
    root = objectify.parse(open(filepath, encoding="utf-8")).getroot()
    schema = root['{urn:ean.ucc:2}message']['{urn:ean.ucc:gpc:2}gs1Schema']['{}schema']

    data = []

    for segment in schema.iterchildren():

        if segment.tag != "segment":
            continue

        segment_data = get_dict_for_element(segment)
        segment_data['level'] = 'segment'
        data.append(segment_data)

        for family in segment.iterchildren():
            family_data = get_dict_for_element(family)
            family_data['segment'] = segment_data['text']
            family_data['level'] = 'family'
            data.append(family_data)

            for class_ in family.iterchildren():
                class_data = get_dict_for_element(family)
                class_data['segment'] = segment_data['text']
                class_data['family'] = family_data['text']
                class_data['level'] = 'class'
                data.append(class_data)

                for brick in class_.iterchildren():
                    brick_data = get_dict_for_element(brick)
                    brick_data['brick'] = brick_data.pop("text")
                    brick_data['segment'] = segment_data['text']
                    brick_data['family'] = family_data['text']
                    brick_data['klass'] = class_data['text']
                    brick_data['level'] = 'brick'
                    data.append(brick_data)

    return data


def save_gs1_data(data):
    data_dir = Path(os.path.dirname(__file__)) / ".." / "data"
    filepath = data_dir / "gs1.json.bz2"

    with open(filepath, "wb") as f:
        with bz2.BZ2File(f.name, "wb") as b:
            b.write(json.dumps(data).encode("utf-8"))
