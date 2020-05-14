"""
Mapping algorithms for linking elicitation glosses to Concepticon.
"""
from pysen.utils import get_Concepticon
import re
from collections import defaultdict
from clldutils.misc import lazyproperty
import attr

__all__ = ['parse_gloss', 'Gloss', 'concept_map']


@attr.s
class Gloss(object):
    main = attr.ib(default='')
    # the start character indicating a potential comment:
    comment_start = attr.ib(default='')
    # the comment (everything occurring in brackets in the input string:
    comment = attr.ib(default='')
    # the end character indicating the end of a potential comment:
    comment_end = attr.ib(default='')
    # the part of speech, in case this was specificied by a preceding "the" or a
    # preceding "to" in the mainpart of the string:
    pos = attr.ib(default='')
    # the prefix, that is, words, like, eg. "be", "in", which may precede the main
    # gloss in concept lists, as in "be quiet":
    prefix = attr.ib(default='')
    # the longest constituent, which is identical with the main part if there's no
    # whitespace in the main part, otherwise the longest part part of the main gloss
    # split by whitespace:
    longest_part = attr.ib(default='')
    # the original gloss (for the purpose of testing):
    gloss = attr.ib(default='', converter=lambda s: s.lower().replace('*', ''))

    frequency = attr.ib(default=0)

    @lazyproperty
    def tokens(self):
        return ' '.join(s for s in self.gloss.split() if s not in ['or'])

    def similarity(self, other):
        # first-order-match: identical glosses
        if self.gloss == other.gloss:
            if self.pos and self.pos == other.pos:
                return 1
            return 2
        # second-order match: identical main-parts
        if self.main == other.gloss or self.gloss == other.main or\
                self.main == other.main:
            # best match if pos matches
            return 3 if self.pos and self.pos == other.pos else 4
        if self.longest_part == other.longest_part:
            return 5 if self.pos and self.pos == other.pos else 6
        if other.longest_part in self.main.split():
            return 7
        if self.longest_part in other.main.split():
            return 8
        return 100

    @classmethod
    def from_string(cls, s, language='en'):
        return parse_gloss(s, language=language)[0]


def parse_gloss(gloss, language='en'):
    """
    Parse a gloss into its constituents by applying some general logic.

    Parameters
    ----------
    gloss : str
        The gloss as found in various sources (we assume that we are dealing
        with English glosses here.

    Returns
    -------
    A list of `Gloss` instances.

    Notes
    -----

    The basic purpose of this function is to provide a means to make it easier
    to compare meanings across different resources. Often, linguists will
    annotate their resources quite differently, and for one and the same
    concept, we may find very different glosses. The concept "kill [verb]", for
    example may be glossed as "to kill", "kill", "kill (v.)", "kill
    (somebody)", etc. In order to guarantee comparability, this function tries
    to use basic knowledge of glossing tendencies to disentangle the variety of
    glossing styles which can be found in the literature. Thus, in the case of
    "kill [verb]", the function will analyze the different strings as follows::

        >>> glosses = ["to kill", "kill", "kill (v.)", "kill (somebody)"]
        >>> for gloss in glosses:
        ...     parsed_gloss = parse_gloss(gloss)[0]
        ...     print(parsed_gloss.main, parsed_gloss.pos)
        kill verb
        kill
        kill verb
        kill

    As can be seen: it seeks to extract the most important part of the gloss
    and may thus help to compare different glosses across different resources.
    """
    if not gloss:
        raise ValueError("Your gloss is empty")
    G = []
    gpos = ''
    if language == 'en':
        pos_markers = {'the': 'noun', 'a': 'noun', 'to': 'verb'}
        prefixes = ['be', 'in', 'at']
    elif language == 'de':
        pos_markers = {'der': 'noun', 'die': 'noun', 'das': 'noun', 'ein':
                'noun', 'eine': 'noun'}
        prefixes = []
    elif language == 'fr':
        pos_markers = {
            'le': 'noun',
            'la': 'noun',
            'les': 'noun',
            'du': 'noun',
            'des': 'noun',
            'de': 'noun',
            'un': 'noun',
            'une': 'noun'}
        prefixes = ['il', 'est']
    else:
        pos_markers = {}
        prefixes = []

    abbreviations = [
        ('vb', 'verb'),
        ('v.', 'verb'),
        ('v', 'verb'),
        ('adj', 'adjective'),
        ('nn', 'noun'),
        ('n.', 'noun'),
        ('adv', 'adverb'),
        ('noun', 'noun'),
        ('verb', 'verb'),
        ('adjective', 'adjective'),
        ('cls', 'classifier')
    ]

    # we use /// as our internal marker for glosses preceded by concepticon
    # gloss information and followed by literal readings
    if '///' in gloss:
        gloss = gloss.split('///')[1]

    # if the gloss consists of multiple parts, we store both the separate part
    # and a normalized form of the full gloss
    constituents = [x.strip() for x in re.split(',|;|:|/| or | OR ', gloss) if x.strip()]
    if len(constituents) > 1:
        constituents += [' / '.join(sorted([c.strip() for c in constituents]))]

    for constituent in constituents:
        if constituent.strip():
            res = Gloss(gloss=gloss)
            mainpart = ''
            in_comment = False
            for char in constituent:
                if char in '([{（<':
                    in_comment = True
                    res.comment_start += char
                elif char in ')]}）>':
                    in_comment = False
                    res.comment_end += char
                else:
                    if in_comment:
                        res.comment += char
                    else:
                        mainpart += char

            mainpart = ''.join(m for m in mainpart if m not in '?!"¨:;,»«´“”*+-')\
                .strip().lower().split()

            # search for pos-markers
            if gpos:
                res.pos = gpos
            else:
                if len(mainpart) > 1 and mainpart[0] in pos_markers:
                    gpos = res.pos = pos_markers[mainpart.pop(0)]

            # search for strip-off-prefixes
            if len(mainpart) > 1 and mainpart[0] in prefixes:
                res.prefix = mainpart.pop(0)

            if mainpart:
                # check for a "first part" in case we encounter white space in the
                # data (and return only the largest string of them)
                res.longest_part = sorted(mainpart, key=lambda x: len(x))[-1]

                # search for pos in comment
                if not res.pos:
                    cparts = res.comment.split()
                    for p, t in sorted(
                            abbreviations, key=lambda x: len(x[0]), reverse=True):
                        if p in cparts or p in mainpart or t in cparts or t in mainpart:
                            res.pos = t
                            break

                res.main = ' '.join(mainpart)
                G.append(res)

    return G

