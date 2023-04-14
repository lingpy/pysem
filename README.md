# PySem: Pysen library for handling semantic data in linguistics

* **Current Version**: 0.7
* **Concepticon Version**: [3.1.0](https://doi.org/10.5281/zenodo.7777629)
 
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

> List, Johann-Mattis (2023): PySeM. A Python library for handling semantic data in linguistics. Version 0.7 URL: https://github.com/lingpy/pysem/, Leipzig: Max Planck Institute for Evolutionary Anthropology.
