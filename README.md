# PySem: Pysen library for handling semantic data in linguistics

[![Build Status](https://github.com/lingpy/pysem/workflows/tests/badge.svg)](https://github.com/lingpy/pysem/actions?query=workflow%3Atests)
[![PyPI](https://img.shields.io/pypi/v/pysem.svg)](https://pypi.org/project/pysem)

Included **Concepticon Version**: [3.4.0](https://doi.org/10.5281/zenodo.14923561)
 
## Usage Examples

Retrieve the sense data assembled by S. A. Starostin in the STARLING software package and search for similar words:

```python
>>> from pysem.sense import Sense
>>> sns = Sense()
>>> sns.similar('arm')
[('arm', 'calf of leg', 's:bone; s:foot; s:hand', 3),
 ('arm', 'hand', 's:bone; s:foot; s:hand', 3),
 ('arm', 'shin-bone', 's:bone; s:foot; s:hand', 3),
 ('arm', 'ankle', 's:bone; s:foot', 2),
 ('arm', 'bone', 's:bone; s:foot', 2)]
```

Map data to the most recent version of the [Concepticon](https://concepticon.clld.org) project:

```python
>>> from pysem import to_concepticon
>>> to_concepticon([{"gloss": "Fuß", "pos": "noun"}], language="de")
{'Fuß': [['1301', 'FOOT', 'noun', 19]]}
```

## How to Cite

> List, Johann-Mattis (2026): PySeM. A Python library for handling semantic data in linguistics [Software, Version 1.3.0]. With contributions by Johannes Englisch and Robert Forkel. URL: https://pypi.org/project/pysem, Passau: MCL Chair at the University of Passau.
