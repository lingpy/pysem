import pytest
from pysen.sense import Sense

def test_sense():
    
    sense = Sense()
    assert len(
            [node for node in sense.G if not node.startswith('sense-')]) == 7093
    assert len(
            [node for node in sense.G if node.startswith('sense-')]) == 427

    assert len(sense.sense('arm')[0][1].split(';')) == 3

    assert sense.similar('arm', maxitems=5)[0][3] == 3
    assert len(sense.similar('arm', threshold=20)) == 0
