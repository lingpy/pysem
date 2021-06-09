import pytest
from pysem.glosses import Gloss, to_concepticon

def test_Gloss():
    gl1 = Gloss.from_string('the bag shower', language='en')
    gl2 = Gloss.from_string('bag shower (noun)', language='en')
    gl3 = Gloss.from_string('bag shower (verb)', language='en')
    gl4 = Gloss.from_string('the BAG SHOWER?', pos='noun', language='en')
    gl5 = Gloss.from_string('BAG SHOWER', pos='verb', language='it')
    gl6 = Gloss.from_string('in shower bag', pos='noun', language='en')
    gl7 = Gloss.from_string('shower bag (verb)', language='en')
    gl8 = Gloss.from_string('shower BAG (noun)', language='en')
    gl9 = Gloss.from_string('shower Bag (verb)', language='en')
    gl10 = Gloss.from_string('the bag', language='en')
    gl11 = Gloss.from_string('to bag', language='en')
    gl12 = Gloss.from_string('le BaG', language='fr')
    gl13 = Gloss.from_string('to baG', language='en')
    gl14 = Gloss.from_string('der something', language='de')
    gl14 = Gloss.from_string('arm or hand')


    assert gl1.similarity(gl2) == 12
    assert gl1.similarity(gl3) == 11
    assert gl1.similarity(gl4) == 10
    assert gl1.similarity(gl5) == 9
    assert gl1.similarity(gl6) == 8
    assert gl1.similarity(gl7) == 7
    assert gl1.similarity(gl8) == 6
    assert gl1.similarity(gl9) == 5
    assert gl1.similarity(gl10) == 4
    assert gl1.similarity(gl11) == 3
    assert gl1.similarity(gl12) == 2
    assert gl1.similarity(gl13) == 1
    assert gl1.similarity(gl14) == 0
    with pytest.raises(ValueError):
        gl = Gloss.from_string('')
    gl = Gloss.from_string('hand or arm', pos='noun')
    assert gl.similarity(gl) == 20
    
    for gloss in [
            ('hand or arm', 'verb', 19),
            ('HAND or ARM', 'noun', 18),
            ('HAND or arm', 'verb', 17),
            ('hand', 'noun', 16),
            ('hand', 'verb', 15),
            ('HAND', 'noun', 14),
            ('HAND', 'verb', 13),
            ]:
        assert gl.similarity(Gloss.from_string(gloss[0], pos=gloss[1])) == gloss[2]

    to_concepticon([
        {'gloss': 'hand'},
        {'gloss': 'HAND'}], language='de')
    with pytest.raises(ValueError):
        to_concepticon([{'gls': 'Hand'}])

    mappings = to_concepticon([
        {"gloss": "arm or hand", "pos": "noun"}], pos_ref="pos")
    assert mappings["arm or hand"][0][-1] == 20

    mappings = to_concepticon([
        {"gloss": "brother-in-law", "pos": "noun"}], pos_ref="noun")
    assert mappings["brother-in-law"][0][-1] == 19




