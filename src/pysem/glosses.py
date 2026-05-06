"""
Mapping algorithms for linking elicitation glosses to Concepticon.
"""
import re
import enum
import functools
import dataclasses
from typing import Optional
from collections.abc import Iterable

from pysem.data import get_concepticon, MappingType

__all__ = ["parse_gloss", "Gloss", "to_concepticon"]

SPLITTER = [",", ";", ":", "/", " or ", " OR "]
MARKER = '?!"¨:;,»«´“”*+-'
BRACKETS = {'(': ')', '[': ']', '{': '}', '（': '）', '<': '>'}
POS_MARKERS_BY_LANGUAGE = {
    'en': {
        'the': 'noun', 'a': 'noun', 'to': 'verb'},
    'de': {
        'der': 'noun', 'die': 'noun', 'das': 'noun', "ein": "noun", "eine": "noun"},
    'fr': {
        'le': 'noun',
        'la': 'noun',
        'les': 'noun',
        'du': 'noun',
        'des': 'noun',
        'de': 'noun',
        'un': 'noun',
        'une': 'noun',
    },
    'es': {
        "el": "noun",
        "la": "noun",
        "los": "noun",
        "mi": "noun",
        "un": "noun",
        "una": "noun",
        "unos": "noun",
        "las": "noun",
        "su": "noun",
    }
}
PREFIXES_BY_LANGUAGE = {
    'en': ['be', 'in', 'at'],
    'fr': ['il', 'est'],
    'es': ["lo", "les", "le"],
}
POS_ABBREVIATIONS = sorted(
    [
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
    ],
    key=lambda x: len(x[0]), reverse=True)


@dataclasses.dataclass(repr=False)
class Gloss:
    """
    Basic object for handling elicitation glosses.

    Notes
    -----
    The gloss is usually parsed, not instantiated. When parsing a gloss with
    `Gloss.from_string`, the parsing process will cut the gloss automatically
    into its constituents:

    - `main`: the main part of the gloss, in which brackets are excluded, but
      space-segmented multi-word expressions are preserved
    - `pos`: the part-of-speech information can be provided when instantiating
      a gloss, but if it is not (yet) available, the information will be
      inferred from the gloss itself, by checking for the presence of articles,
      or infinitive markers (depending on the language under question)
    - `parts`: a gloss like "body hair" will be split into two parts, "body"
      and "hair" (but its main part will remain "body hair").
    - `gloss`: the gloss refers not to the original string passed to the
      `Gloss.from_string` command, but to the largest part in glosses with
      ambiguous meaning, such as the very common "arm/hand". In these cases,
      the `parse_gloss` command will yield two glosses, one with "arm" as
      gloss, and one with "hand" as gloss, but both with the same `text`
      attribute.
    - `text`: the original string from which a gloss was parsed.

    """

    main: str = ""
    # the comment (everything occurring in brackets in the input string:
    comment: str = ""
    # the part of speech, in case this was specificied by a preceding "the" or a
    # preceding "to" in the mainpart of the string:
    pos: str = ""
    # the prefix, that is, words, like, eg. "be", "in", which may precede the main
    # gloss in concept lists, as in "be quiet":
    prefix: str = ""
    # the longest constituent, which is identical with the main part if there's no
    # whitespace in the main part, otherwise the longest part part of the main gloss
    # split by whitespace:
    parts: set = dataclasses.field(default_factory=set)
    # the original gloss (for the purpose of testing):
    gloss: str = ""
    text: str = ""

    def similarity(self, other: 'Gloss') -> int:  # pylint: disable=R0911
        """
        Compute similarity between glosses.

        Notes
        -----
        Similarity is provided on a scale from 20 to 0. The highest similarity
        is achieved, if the `text`, the original string, is identical, and
        part-of-speech information is provided. A similarity of 10 indicates
        that the `main` part of the gloss is similar and the part-of-speech as
        well, and 9 indicates that part-of-speech information is missing or
        different.
        """
        same_pos = self.pos == other.pos
        if self.text == other.text:
            return 20 if same_pos else 19
        if self.text.lower() == other.text.lower():
            return 18 if same_pos else 17
        if self.gloss == other.gloss:
            return 16 if same_pos else 15
        if self.gloss.lower() == other.gloss.lower():
            return 14 if same_pos else 13
        if self.main == other.main:
            return 12 if same_pos else 11
        if self.main.lower() == other.main.lower():
            return 10 if same_pos else 9
        if self.parts == other.parts:
            return 8 if same_pos else 7
        if {p.lower() for p in self.parts} == {p.lower() for p in other.parts}:
            return 6 if same_pos else 5
        if self.parts.intersection(other.parts):
            return 4 if same_pos else 3
        if {p.lower() for p in self.parts}.intersection({p.lower() for p in other.parts}):
            return 2 if same_pos else 1
        return 0

    @classmethod
    def from_string(  # pylint: disable=R0917,R0913
        cls,
        s: str,
        pos: str = "",
        language: str = "en",
        splitter: str = "|".join(SPLITTER),
        marker: str = MARKER,
    ) -> 'Gloss':
        """Instantiate a Gloss from a string."""
        return parse_gloss(
            s,
            pos=pos,
            language=language,
            splitter=splitter,
            marker=marker,
        )[0]


class Pos(enum.Enum):
    """Recognized parts of speech in glosses."""
    noun = enum.auto()  # pylint: disable=C0103
    verb = enum.auto()  # pylint: disable=C0103
    adjective = enum.auto()  # pylint: disable=C0103
    adverb = enum.auto()  # pylint: disable=C0103
    classifier = enum.auto()  # pylint: disable=C0103

    @classmethod
    def from_string(cls, s: str) -> 'Pos':
        """Get the enum symbol from its name."""
        return getattr(cls, s.lower())


@dataclasses.dataclass
class ParseSpec:
    """Specification (and implementation) for the parsing of glosses for comparison."""
    pos_markers: dict[str, Pos]
    prefixes: list[str]
    pos_abbreviations: list[tuple[str, Pos]]
    punctuation: str = MARKER
    split_pattern: re.Pattern = re.compile('|'.join(re.escape(s) for s in SPLITTER))
    comment_marker: dict[str, str] = dataclasses.field(default_factory=lambda: BRACKETS)

    @classmethod
    def for_language(
            cls,
            language: str = 'en',
            punctuation: Optional[str] = None,
            separator: Optional[str] = None,
    ) -> 'ParseSpec':
        """Get a ParseSpec, optionally tuned to a particular gloss language."""
        pos_markers = POS_MARKERS_BY_LANGUAGE.get(language, {})
        pos_markers = {k: Pos.from_string(v) for k, v in pos_markers.items()}
        abbreviations = [(k, Pos.from_string(v)) for k, v in POS_ABBREVIATIONS]
        kw = {}
        if punctuation:
            kw['punctuation'] = punctuation
        if separator:
            kw['split_pattern'] = re.compile('|'.join(re.escape(s) for s in separator.split('|')))
        return cls(
            pos_markers,
            PREFIXES_BY_LANGUAGE.get(language, []),
            # Sort abbreviations by descending length.
            sorted(abbreviations, key=lambda x: len(x[0]), reverse=True),
            **kw)

    def split_constituents(self, gloss: str) -> list[str]:
        """
        >>> spec = ParseSpec.for_language('en')
        >>> spec.split_constituents('arm OR hand')
        ['arm', 'hand', 'arm / hand']
        """
        constituents = [x.strip() for x in self.split_pattern.split(gloss) if x.strip()]
        if len(constituents) > 1:
            constituents.append(' / '.join(sorted([c.strip() for c in constituents])))
        return constituents

    def get_mainpart(self, constituent: str, res: Gloss) -> list[str]:
        """Find the mainpart of a gloss (and assign other parts to the corresponding attributes.)"""
        mainpart = ""
        in_comment = False
        for char in constituent:
            if char in self.comment_marker:
                in_comment = True
            elif char in self.comment_marker.values():
                in_comment = False
            else:
                if in_comment:
                    res.comment += char
                else:
                    mainpart += char
        return ''.join(c for c in mainpart if c not in self.punctuation).strip().split()

    def get_pos(self, mainpart: list[str], cparts: list[str]) -> str:
        """Try to find a part-of-speech specification somewhere in the gloss parts."""
        for abbr, pos in self.pos_abbreviations:
            p = pos.name
            if  abbr in cparts or abbr in mainpart or p in cparts or p in mainpart:
                return p
        return ''


def parse_gloss(
    gloss,
    pos="",
    language="en",
    splitter: str = '|'.join(SPLITTER),
    marker: str = MARKER,
) -> list[Gloss]:
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
    spec = ParseSpec.for_language(language, punctuation=marker, separator=splitter)

    G: list[Gloss] = []  # pylint: disable=C0103

    for constituent in spec.split_constituents(gloss):
        res = Gloss(gloss=constituent, text=gloss)
        mainpart = spec.get_mainpart(constituent, res)

        # search for pos-markers
        if len(mainpart) > 1 and mainpart[0] in spec.pos_markers:
            new_pos = spec.pos_markers[mainpart.pop(0)].name
            res.pos = new_pos
        if pos:
            res.pos = pos

        # search for strip-off-prefixes
        if len(mainpart) > 1 and mainpart[0] in spec.prefixes:
            res.prefix = mainpart.pop(0)

        if mainpart:
            # check for a "first part" in case we encounter white space in the
            # data (and return only the largest string of them)
            res.parts = set(mainpart)

            # search for pos in comment
            if not res.pos:
                res.pos = spec.get_pos(mainpart, res.comment.split())

            res.main = " ".join(mainpart)
        G.append(res)

    return G


@functools.total_ordering
@dataclasses.dataclass
class Match:
    """
    A Concepticon conceptset matching a gloss. Matches can be ordered from best to worst and hashed
    for de-duplication.
    """
    concepticon_id: str
    concepticon_gloss: str
    frequency: int
    pos: str
    similarity: int

    @classmethod
    def from_row(cls, row: tuple[str, str, int, str], g: Gloss, text: str) -> 'Match':
        """Instantiate a match from data in a mapping row."""
        return cls(
            row[0],  # concepticon_id
            row[1],  # concepticon_gloss
            row[2],  # some sort of frequency
            row[3],  # pos
            g.similarity(Gloss.from_string(text, pos=row[3])),  # similarity
        )

    def __hash__(self):
        return hash(dataclasses.astuple(self))

    def __eq__(self, other):
        return dataclasses.astuple(self) == dataclasses.astuple(other)

    def __lt__(self, other):
        # higher similarity is better, having a pos is better, higher frequency is better.
        return ((self.similarity, bool(self.pos), self.frequency) >
                (other.similarity, bool(other.pos), other.frequency))


@dataclasses.dataclass
class Matcher:
    """
    A Matcher finds matches with Concepticon conceptsets for a given gloss.
    """
    marker: str = MARKER
    splitter: str = '|'.join(SPLITTER)
    language: str = 'en'
    all_mappings: dict[str, MappingType] = dataclasses.field(default_factory=get_concepticon)

    @property
    def mappings(self) -> MappingType:
        """Language-specific mappings from gloss to matching Concepticon concept sets."""
        return self.all_mappings[self.language]

    def _iter_match_candidates(self, gloss, pos):
        if gloss in self.mappings:
            yield gloss, Gloss.from_string(gloss, language=self.language, pos=pos)
        elif gloss.lower() in self.mappings:
            yield gloss.lower(), Gloss.from_string(gloss, language=self.language, pos=pos)

        for g in parse_gloss(
            gloss,
            pos=pos,
            marker=self.marker,
            splitter=self.splitter,
            language=self.language,
        ):
            for variant in (g.gloss, g.gloss.lower(), g.main, g.main.lower()):
                if variant in self.mappings:
                    yield variant, g

    def match(self, gloss, pos, max_matches: int = 1) -> list[Match]:
        """Find matches for gloss."""
        results = set()
        for text, g in self._iter_match_candidates(gloss, pos):
            for row in self.mappings[text]:
                results.add(Match.from_row(row, g, text))
        return sorted(results)[:max_matches]


def to_concepticon(  # pylint: disable=R0917,R0913
    concepts: Iterable[dict[str, str]],
    max_matches: int = 1,
    language: str = "en",
    gloss_ref: str = "gloss",
    pos_ref: str = "",
    splitter: str = "|".join(SPLITTER),
    marker: str = MARKER,
    mappings: dict = None,
) -> dict[str, list[tuple[str, str, str, int]]]:
    """
    Map a given concept list to Concepticon (Version 3.4.0).
    """
    matcher = Matcher(marker, splitter, language, mappings or get_concepticon())
    matches = {}
    for concept in concepts:
        gloss, pos = concept.get(gloss_ref), concept.get(pos_ref, "")
        if gloss:
            matches[gloss] = [
                (match.concepticon_id, match.concepticon_gloss, match.pos, match.similarity)
                for match in matcher.match(gloss, pos, max_matches)]
        else:
            raise ValueError("no glosses could be found")
    return matches
