# PySen: Pysen library for handling semantic data in linguistics
 
## Example

Retrieve the sense data assembled by S. A. Starostin in the STARLING software package and search for similar words:

```python
>>> from pysen.sense import Sense
>>> sns = Sense()
>>> sns.similar('arm')
[['arm', 'calf of leg', 'sense-bone; sense-foot; sense-hand', 3],
 ['arm', 'hand', 'sense-bone; sense-foot; sense-hand', 3],
 ['arm', 'shin-bone', 'sense-bone; sense-foot; sense-hand', 3],
 ['arm', 'ankle', 'sense-bone; sense-foot', 2],
 ['arm', 'bone', 'sense-bone; sense-foot', 2]]
```


