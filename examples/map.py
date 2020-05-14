from pysen.glosses import to_concepticon
from pyconcepticon import Concepticon
from cldfcatalog import Config
from statistics import mean

repos = Config.from_file().get_clone('concepticon')
concepticon = Concepticon(repos)

results = []
for lst in concepticon.conceptlists.values():
    concepts = []
    if 'chinese' in lst.source_language:

        for concept in lst.concepts.values():
            concepts += [{'concept': concept.attributes['chinese'], 'concepticon_id':
                concept.concepticon_id}]
        
        mappings = to_concepticon(concepts, gloss_ref='concept', language='zh')
        hits, total = 0, 0
        for concept in concepts:
            cid = concept['concepticon_id']
            tids = mappings[concept['concept']]
            scores = []
            for tid in tids:
                if tid[0] == cid:
                    scores += [1]
                else:
                    scores += [0]
            if scores:
                scores = mean(scores)
            else:
                scores = 0
            hits += scores
            total += 1
        print('{0:40} {1:.2f}'.format(lst.id, hits/total))
        results += [[lst.id, hits/total]]

print('total', '{0:.2f}'.format(mean([x[1] for x in results])))

