"""
Sense manipulations following the framework of the STARLING package.
"""
import collections

from pysem.data import get_sense


class Sense:
    """
    Provides methods operating on the graph of senses from the STARLING package.
    """
    def __init__(self):
        """
        Creates a sense graph upon initialization.
        """
        sense = get_sense()
        self.G: dict[str, set[str]] = {key: set() for key in sense}  # pylint: disable=C0103

        for key, values in sense.items():
            for value in values:
                val = "s:" + value
                if val not in self.G:
                    self.G[val] = set()
                self.G[key].add(val)
                self.G[val].add(key)

        L = collections.defaultdict(collections.Counter)  # pylint: disable=C0103
        for key in sense:
            L[key].update([key])
            if "(V)" in key:
                L[key[:-4]].update([key])
            if " " in key:
                if "(V)" in key:
                    L[key.replace(" ", "")[:-3]].update([key])
                elif key[-1].isdigit():
                    L[key[:-1].strip()].update([key])
                    L[key[:-1].replace(" ", "")].update([key])
                else:
                    L[key.replace(" ", "")].update([key])

        self.L: dict[str, list[str]] = {  # pylint: disable=C0103
            k: [key for key, _ in sorted(v.most_common(), key=lambda x: (x[1], x[0]))]
            for k, v in L.items()}


    def sense(self, word: str) -> list[tuple[str, str]]:
        """
        Return the senses of a word.

        >>> Sense().sense('arm')
        [('arm', 'bone; foot; hand')]
        """
        out = []
        for key in self.L[word]:
            out.append((key, "; ".join(sorted(get_sense()[key]))))
        return out

    def similar(
            self,
            word: str,
            threshold: int = 2,
            maxitems: int = 5
    ) -> list[tuple[str, str, str, int]]:
        """
        Search for similar items in the dataset.

        >>> Sense().similar('arm')[0]
        ('arm', 'shin-bone', 's:bone; s:foot; s:hand', 3)
        """
        out = []
        for key in self.L[word]:
            neighbors = collections.defaultdict(list)
            for node in self.G[key]:
                for next_node in self.G[node]:
                    if next_node != key:
                        neighbors[next_node].append(node)
            for k, v in neighbors.items():
                neighbors[k] = sorted(set(v))
            for k, v in sorted(
                neighbors.items(), key=lambda x: (-len(x[1]), x[0])):
                if len(v) >= threshold:
                    out.append((key, k, "; ".join(v), len(v)))
        return out[:maxitems]
