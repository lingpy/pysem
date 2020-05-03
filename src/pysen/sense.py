"""
Sense manipulations following the framework of the STARLING package.
"""
import networkx as nx
from pysen.data import SENSE
from collections import defaultdict
from tabulate import tabulate

class Sense(object):

    def __init__(self):
        """
        Creates a sense graph upon initialization.
        """
        G = nx.Graph()
        for key, values in SENSE.items():
            G.add_node(key, type=1)
            for value in values:
                if not 'sense-'+value in G:
                    G.add_node('sense-'+value, type=2)
                G.add_edge(key, 'sense-'+value)
                
        # make a fuzzy lookup
        L = defaultdict(list)
        for key in SENSE:
            L[key] += [key]
            if '(V)' in key:
                L[key[:-4]] += [key]
            if ' ' in key:
                if '(V)' in key:
                    L[key.replace(' ', '')[:-3]] += [key]
                elif key[-1].isdigit():
                    L[key[:-1].strip()] += [key]
                    L[key[:-1].replace(' ', '')] += [key]
                else:
                    L[key.replace(' ', '')] += [key]

        for k, vals in L.items():
            L[k] = sorted(set(vals), key=lambda x: vals.count(x), reverse=True)

        self.G = G
        self.L = L

    def sense(self, word):
        """
        Return the senses of a word.
        """
        out = []
        for key in self.L[word]:
            out += [(key, '; '.join(sorted(SENSE[key])))]
        return out

    def similar(self, word, threshold=2, maxitems=5):
        out = []
        for key in self.L[word]:
            neighbors = defaultdict(list)
            for node in self.G[key]:
                for next_node in self.G[node]:
                    if next_node != key:
                        neighbors[next_node] += [node]
            for k, v in neighbors.items():
                neighbors[k] = sorted(set(v))
            for k, v in sorted(neighbors.items(), key=lambda x: len(x[1]),
                    reverse=True):
                if len(v) >= threshold:
                    out += [[key, k, '; '.join(v), len(v)]]
        return out[:maxitems]


