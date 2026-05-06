"""
Functionality to access the data distributed with the package.
"""
import csv
import json
import zipfile
import pathlib
import functools

LanguageType = str
MappingType = dict[str, list[list]]  # Maps gloss to list of (cid, cgloss, freq, gloss, freq) lists.
DATA_DIR = pathlib.Path(__file__).parent / 'data'


@functools.lru_cache(maxsize=1)
def get_sense() -> dict[str, frozenset[str]]:
    """Get the STARLING sense data."""
    res = {}
    with DATA_DIR.joinpath("sense.csv").open(newline='') as csvfile:
        for row in csv.DictReader(csvfile):
            res[row["HEADWORD"]] = frozenset(row["ITEMS"].split(";")[:-1])
    return res


@functools.lru_cache(maxsize=1)
def get_concepticon() -> dict[LanguageType, MappingType]:
    """Get the Concepticon mapping data."""
    with zipfile.ZipFile(DATA_DIR.joinpath("concepticon.zip"), "r") as zf:
        concepticon = json.loads(zf.read("concepticon.json"))
    return concepticon
