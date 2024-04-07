"""
Mapping algorithms for linking elicitation glosses to Concepticon.
"""
from pysem.data import get_Concepticon
import re
from collections import defaultdict
from clldutils.misc import lazyproperty
import attr

__all__ = ["parse_gloss", "Gloss", "to_concepticon"]

MAPPINGS = get_Concepticon()


@attr.s(repr=False)
class Gloss(object):
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

    main = attr.ib(default="")
    # the start character indicating a potential comment:
    comment_start = attr.ib(default="")
    # the comment (everything occurring in brackets in the input string:
    comment = attr.ib(default="")
    # the end character indicating the end of a potential comment:
    comment_end = attr.ib(default="")
    # the part of speech, in case this was specificied by a preceding "the" or a
    # preceding "to" in the mainpart of the string:
    pos = attr.ib(default="")
    # the prefix, that is, words, like, eg. "be", "in", which may precede the main
    # gloss in concept lists, as in "be quiet":
    prefix = attr.ib(default="")
    # the longest constituent, which is identical with the main part if there's no
    # whitespace in the main part, otherwise the longest part part of the main gloss
    # split by whitespace:
    parts = attr.ib(default=set())
    # the original gloss (for the purpose of testing):
    gloss = attr.ib(default="")
    text = attr.ib(default="")

    def similarity(self, other):
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
        similarities = []
        pos = self.pos == other.pos
        if self.text == other.text:
            return 20 if pos else 19
        if self.text.lower() == other.text.lower():
            return 18 if pos else 17
        if self.gloss == other.gloss:
            return 16 if pos else 15
        if self.gloss.lower() == other.gloss.lower():
            return 14 if pos else 13
        if self.main == other.main:
            return 12 if pos else 11
        if self.main.lower() == other.main.lower():
            return 10 if pos else 9
        if self.parts == other.parts:
            return 8 if pos else 7
        if set([p.lower() for p in self.parts]) == set(
            [p.lower() for p in other.parts]
        ):
            return 6 if pos else 5
        if self.parts.intersection(other.parts):
            return 4 if pos else 3
        if set([p.lower() for p in self.parts]).intersection(
            set([p.lower() for p in other.parts])
        ):
            return 2 if pos else 1
        return 0

    @classmethod
    def from_string(
        cls,
        s,
        pos="",
        language="en",
        splitter=",|;|:|/| or | OR ",
        marker='?!"¨:;,»«´“”*+',
        brackets_open="([{（<",
        brackets_close=")]}）>",
    ):
        return parse_gloss(
            s,
            pos=pos,
            language=language,
            splitter=splitter,
            marker=marker,
            brackets_open=brackets_open,
            brackets_close=brackets_close,
        )[0]


def parse_gloss(
    gloss,
    pos="",
    language="en",
    splitter=",|;|:|/| or | OR ",
    marker='?!"¨:;,»«´“”*+',
    brackets_open="([{（<",
    brackets_close=")]}）>",
):
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
    if language == "en":
        pos_markers = {"the": "noun", "a": "noun", "to": "verb"}
        prefixes = ["be", "in", "at"]
    elif language == "de":
        pos_markers = {
            "der": "noun",
            "die": "noun",
            "das": "noun",
            "ein": "noun",
            "eine": "noun",
        }
        prefixes = []
    elif language == "fr":
        pos_markers = {
            "le": "noun",
            "la": "noun",
            "les": "noun",
            "du": "noun",
            "des": "noun",
            "de": "noun",
            "un": "noun",
            "une": "noun",
        }
        prefixes = ["il", "est"]
    else:
        pos_markers = {}
        prefixes = []

    abbreviations = [
        ("vb", "verb"),
        ("v.", "verb"),
        ("v", "verb"),
        ("adj", "adjective"),
        ("nn", "noun"),
        ("n.", "noun"),
        ("adv", "adverb"),
        ("noun", "noun"),
        ("verb", "verb"),
        ("adjective", "adjective"),
        ("cls", "classifier"),
    ]

    # if the gloss consists of multiple parts, we store both the separate part
    # and a normalized form of the full gloss
    constituents = [x.strip() for x in re.split(splitter, gloss) if x.strip()]
    if len(constituents) > 1:
        constituents += [" / ".join(sorted([c.strip() for c in constituents]))]

    for constituent in constituents:
        if constituent.strip():
            res = Gloss(gloss=constituent, text=gloss)
            mainpart = ""
            in_comment = False
            for char in constituent:
                if char in brackets_open:
                    in_comment = True
                    res.comment_start += char
                elif char in brackets_close:
                    in_comment = False
                    res.comment_end += char
                else:
                    if in_comment:
                        res.comment += char
                    else:
                        mainpart += char

            mainpart = "".join(m for m in mainpart if m not in marker).strip().split()

            # search for pos-markers
            if len(mainpart) > 1 and mainpart[0] in pos_markers:
                new_pos = pos_markers[mainpart.pop(0)]
                res.pos = new_pos
            if pos:
                res.pos = pos

            # search for strip-off-prefixes
            if len(mainpart) > 1 and mainpart[0] in prefixes:
                res.prefix = mainpart.pop(0)

            if mainpart:
                # check for a "first part" in case we encounter white space in the
                # data (and return only the largest string of them)
                res.parts = set(mainpart)

                # search for pos in comment
                if not res.pos:
                    cparts = res.comment.split()
                    for p, t in sorted(
                        abbreviations, key=lambda x: len(x[0]), reverse=True
                    ):
                        if p in cparts or p in mainpart or t in cparts or t in mainpart:
                            res.pos = t
                            break

                res.main = " ".join(mainpart)
            G.append(res)

    return G


def to_concepticon(
    concepts,
    max_matches=1,
    language="en",
    gloss_ref="gloss",
    pos_ref="",
    splitter=",|;|:|/| or | OR ",
    marker='?!"¨:;,»«´“”*+-',
    brackets_open="([{（<",
    brackets_close=")]}）>",
    mappings=MAPPINGS,
):
    """
    Map a given concept list to Concepticon (Version 3.2.0).
    """
    matches = {}
    for concept in concepts:
        gloss, pos = concept.get(gloss_ref), concept.get(pos_ref, "")
        if gloss:
            glosses = parse_gloss(
                gloss,
                pos=pos,
                marker=marker,
                splitter=splitter,
                language=language,
                brackets_open=brackets_open,
                brackets_close=brackets_close,
            )
            candidates = []
            if gloss in mappings[language]:
                candidates += [
                    (gloss, Gloss.from_string(gloss, language=language, pos=pos))
                ]
            elif gloss.lower() in mappings[language]:
                candidates += [
                    (
                        gloss.lower(),
                        Gloss.from_string(gloss, language=language, pos=pos),
                    )
                ]
            for g in glosses:
                if g.gloss in mappings[language]:
                    candidates += [(g.gloss, g)]
                if g.gloss.lower() in mappings[language]:
                    candidates += [(g.gloss.lower(), g)]
                if g.main in mappings[language]:
                    candidates += [(g.main, g)]
                if g.main.lower() in mappings[language]:
                    candidates += [(g.main.lower(), g)]
            results = []
            for text, g in candidates:

                for row in mappings[language][text]:
                    results += [
                        (
                            row[0],
                            row[1],
                            row[2],
                            row[3],
                            g.similarity(Gloss.from_string(text, pos=row[3])),
                        )
                    ]

            # using a dictionary (key -> True) instead of a set because sets
            # don't guarantee a stable element order.
            results = sorted(
                {row: True for row in results},
                key=lambda x: (x[-1], 1 if pos == x[-2] else 0, x[-3]),
                reverse=True,
            )[:max_matches]
            matches[gloss] = []
            for result in results:
                matches[gloss] += [[result[0], result[1], result[3], result[4]]]
        else:
            raise ValueError("no glosses could be found")
    return matches
