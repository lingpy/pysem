import pytest
from pysem.sense import Sense


def test_sense():

    sense = Sense()
    assert len([node for node in sense.G if not node.startswith("s:")]) == 7048
    assert len([node for node in sense.G if node.startswith("s:")]) == 424

    assert len(sense.sense("arm")[0][1].split(";")) == 3

    assert sense.similar("arm", maxitems=5)[0][3] == 3
    assert len(sense.similar("arm", threshold=20)) == 0
