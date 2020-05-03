import pytest
from pysen.sense import Sense

def test_sense():
    
    sense = Sense()
    assert len(
            [node for node, data in sense.G.nodes(data=True) if data['type'] \
                    == 1]) == 7093
    assert len(
            [node for node, data in sense.G.nodes(data=True) if data['type'] \
                    == 2]) == 427

    assert len(sense.sense('arm')[0][1].split(';')) == 3

    assert sense.similar('arm', maxitems=5)[0][3] == 3
    assert len(sense.similar('arm', threshold=20)) == 0
