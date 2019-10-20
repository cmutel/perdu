from pathlib import Path
from tika import parser
import bz2
import json
import os
import re


header = re.compile(r"^\s*(?P<code>\d{3,6})\s+\w+")
excepts = re.compile(r" \([Ee]xcept([^(]|\(.?\))*\)")


def clean_line(line):
    # Invalid character - bullet points
    line = line.replace("\uf0b7", "")
    line = line.strip()
    if line and line[-1] == "T":
        line = line[:-1]
    return line


def subtract_excepts(string, existing=None):
    """Remove statesments with ``(except ...)``.

    Can handle one level of recursive parentheses.

    For example, given:

        'This industry group comprises establishments primarily engaged in (1) growing crops (except oilseedand/or grain; vegetable and/or melon; fruit and tree nut; and greenhouse, nursery, and/or floricultureproducts), such as tobacco, cotton, sugarcane, hay, sugar beets, peanuts, agave, herbs and spices, and hayand grass seeds, or (2) growing a combination of crops (except a combination of oilseed(s) and grain(s) anda combination of fruit(s) and tree nut(s)).'

    Returns:

        (
            'This industry group comprises establishments primarily engaged in (1) growing crops , such as tobacco, cotton, sugarcane, hay, sugar beets, peanuts, agave, herbs and spices, and hayand grass seeds, or (2) growing a combination of crops .',
            [
                'except oilseedand/or grain; vegetable and/or melon; fruit and tree nut; and greenhouse, nursery, and/or floricultureproducts',
                'except a combination of oilseed(s) and grain(s) anda combination of fruit(s) and tree nut(s)'
            ]
        )

    """
    if existing is None:
        existing = []
    for match in excepts.finditer(string):
        except_string = match.group()
        string = string.replace(except_string, "")
        existing.append(except_string.strip()[1:-1])
    return string, existing


def split_cross_references(obj):
    for i, line in enumerate(obj):
        if obj[i].lower().startswith("cross-references"):
            return " ".join(obj[:i]).strip(), [o.strip() for o in obj[i + 1 :]]
    else:
        return " ".join(obj).strip(), []


def process_section(section):
    data = {}
    # First line is code -- name
    first_line = section.pop(0)
    match = header.match(first_line)
    assert match
    data["code"] = match["code"]
    data["name"] = first_line.replace(data["code"], "").strip()

    i = 0
    while i < len(section) - 1:
        # Add together sentences split by PDF
        if not section[i].startswith("Cross-References") and not section[
            i
        ].strip().endswith("."):
            section[i] += " " + section.pop(i + 1)
        # Restore paragraph breaks
        elif not section[i].startswith("Cross-References") and section[
            i
        ].strip().endswith("."):
            section[i] = section[i].strip() + "\n"
            i += 1
        else:
            i += 1

    data["description"], data["cross references"] = split_cross_references(section)

    data["excepts"] = []
    data["name"], _ = subtract_excepts(data["name"], data["excepts"])
    data["description"], _ = subtract_excepts(data["description"], data["excepts"])

    return data


def sector_heading(section):
    return any("the sector as a whole" in line.lower() for line in section)


def extract_naics_data(filepath):
    """Filepath is absolute filepath to the file "2017_Definition_File.pdf"

    It can be downloaded from https://www.census.gov/eos/www/naics/downloadables/downloadables.html

    """
    sections = []
    this_section = []

    for i, line in enumerate(parser.from_file(filepath)["content"].split("\n")):
        line = clean_line(line)

        # Skip initial blank lines
        if not line:
            continue

        if this_section and header.match(line):
            # Start of new section
            sections.append(this_section)
            this_section = [line]
        else:
            this_section.append(line)

    # Last section not in loop
    sections.append(this_section)

    return [
        process_section(section) for section in sections if not sector_heading(section)
    ]


def save_naics_data(data):
    data_dir = Path(os.path.dirname(__file__)) / ".." / "data"
    filepath = data_dir / "naics.json.bz2"

    with open(filepath, "wb") as f:
        with bz2.BZ2File(f.name, "wb") as b:
            b.write(json.dumps(data).encode("utf-8"))
