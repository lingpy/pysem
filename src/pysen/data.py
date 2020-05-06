from pathlib import Path
from csvw.dsv import UnicodeDictReader
import networkx as nx

def data_path(*path):
    return Path(__file__).parent.joinpath('data', *path)

with UnicodeDictReader(data_path('sense.csv'), delimiter=",") as reader:
    SENSE = {}
    for row in reader:
        SENSE[row['HEADWORD']] = frozenset(row['ITEMS'].split(';')[:-1])

