from pathlib import Path
from csvw.dsv import UnicodeDictReader
import zipfile
import json


def data_path(*path):
    return Path(__file__).parent.joinpath("data", *path)


with UnicodeDictReader(data_path("sense.csv"), delimiter=",") as reader:
    SENSE = {}
    for row in reader:
        SENSE[row["HEADWORD"]] = frozenset(row["ITEMS"].split(";")[:-1])


def get_Concepticon():
    with zipfile.ZipFile(data_path("concepticon.zip").as_posix(), "r") as zf:
        concepticon = json.loads(zf.read("concepticon.json"))
    return concepticon
