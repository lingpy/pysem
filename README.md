# PySem: Pysen library for handling semantic data in linguistics

* **Current Version**: 0.8
* **Concepticon Version**: [3.2.0](https://doi.org/10.5281/zenodo.7298022)
 
## Usage Examples

Retrieve the sense data assembled by S. A. Starostin in the STARLING software package and search for similar words:

```python
>>> from pysem.sense import Sense
>>> sns = Sense()
>>> sns.similar('arm')
[['arm', 'calf of leg', 'sense-bone; sense-foot; sense-hand', 3],
 ['arm', 'hand', 'sense-bone; sense-foot; sense-hand', 3],
 ['arm', 'shin-bone', 'sense-bone; sense-foot; sense-hand', 3],
 ['arm', 'ankle', 'sense-bone; sense-foot', 2],
 ['arm', 'bone', 'sense-bone; sense-foot', 2]]
```

Map data to the most recent version of the [Concepticon](https://concepticon.clld.org) project:

```python
>>> from pysem import to_concepticon
>>> to_concepticon([{"gloss": "Fuß", pos: "noun"}], language="de"}])
{'Fuß': [['1301', 'FOOT', 'noun', 19]]}
```

## How to Cite

> List, Johann-Mattis (2024): PySeM. A Python library for handling semantic data in linguistics [Software, Version 0.8]. With contributions by Johannes Englisch. URL: https://pypi.org/project/pysem, Passau: MCL Chair at the University of Passau.
