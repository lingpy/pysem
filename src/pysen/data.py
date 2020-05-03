from pathlib import Path
from csvw.dsv import UnicodeDictReader
import networkx as nx

def data_path(*path):
    return Path(__file__).parent.joinpath('data', *path)

with UnicodeDictReader(data_path('sense.tsv'), delimiter="\t") as reader:
    SENSE = {}
    for row in reader:
        SENSE[row['GLOSS']] = frozenset(row['SENSES'].split(';'))

