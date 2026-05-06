import pytest

from pysem.glosses import Gloss, to_concepticon, parse_gloss, ParseSpec, Matcher


@pytest.mark.parametrize(
    'string,separator,constituents',
    [
        ('a', None, ['a']),
        ('a;b', None, ['a', 'b', 'a / b']),
        ('a+b', '+', ['a', 'b', 'a / b']),
        ('a+b', '-|+', ['a', 'b', 'a / b']),
    ]
)
def test_ParseSpec_split_constituents(string, separator, constituents):
    spec = ParseSpec.for_language(separator=separator)
    assert spec.split_constituents(string) == constituents


@pytest.mark.parametrize(
    'string,assertion',
    [
        ('word', lambda g: g.main == 'word'),
        ('word; other', lambda g: g.main == 'word'),
        ('(word)', lambda g: g.comment == 'word'),
        ('(word)[other]', lambda g: g.comment == 'wordother'),
        ('(word]', lambda g: g.comment == 'word'),
        ('the town', lambda g: g.pos == 'noun' and g.main == 'town'),
        ('in town', lambda g: g.prefix == 'in' and g.main == 'town'),
    ]
)
def test_gloss_comments(string, assertion):
    g = parse_gloss(string)[0]
    assert assertion(g)


@pytest.mark.parametrize(
    'gloss,kw,similarity',
    [
        ('bag shower (noun)', dict(language='en'), 12),
        ('bag shower (verb)', dict(language='en'), 11),
        ('the BAG SHOWER?', dict(pos='noun', language='en'), 10),
        ('BAG SHOWER', dict(pos='verb', language='it'), 9),
        ('in shower bag', dict(pos='noun', language='en'), 8),
        ('shower bag (verb)', {}, 7),
        ('shower BAG (noun)', {}, 6),
        ('shower Bag (verb)', {}, 5),
        ('the bag', {}, 4),
        ('to bag', dict(language='en'), 3),
        ('le BaG', dict(language='fr'), 2),
        ('to baG', dict(language='en'), 1),
        ('arm or hand', {}, 0),
    ]
)
def test_similarity1(gloss, kw, similarity):
    gl = Gloss.from_string('the bag shower', pos='noun')
    assert gl.similarity(Gloss.from_string(gloss, **kw)) == similarity


def test_invalid_gloss():
    with pytest.raises(ValueError):
        _ = Gloss.from_string('')


@pytest.mark.parametrize(
    'gloss,pos,similarity',
    [
        ('hand or arm', 'noun', 20),
        ('hand or arm', 'verb', 19),
        ('HAND or ARM', 'noun', 18),
        ('HAND or arm', 'verb', 17),
        ('hand', 'noun', 16),
        ('hand', 'verb', 15),
        ('HAND', 'noun', 14),
        ('HAND', 'verb', 13),
    ]
)
def test_similarity2(gloss, pos, similarity):
    gl = Gloss.from_string('hand or arm', pos='noun')
    assert gl.similarity(Gloss.from_string(gloss, pos=pos)) == similarity


def test_to_concepticon():
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


def test_Matcher():
    matcher = Matcher()
    res = matcher.match('foot', '', max_matches=10)
    assert len(res) == 2
    assert res[0].frequency > res[1].frequency
