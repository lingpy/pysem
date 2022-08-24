"""
John E. Miller
June 1, 2021

Functions to work with embeddings -- perform vector operations and search.

Develop as a class for easier use.


"""
import numpy
import numpy as np
from dataclasses import dataclass, field

from sklearn.neighbors import NearestNeighbors


def load_embeddings(filename):
    # read segments and embeddings from tab delimited file.
    embeddings = {}
    with open(filename, 'r') as in_emb:
        for line in in_emb:
            items = line.strip().split(sep='\t')
            segment = items[0]
            vec = np.array(items[1:], dtype=np.float64)
            embeddings[segment] = vec

    return embeddings


@dataclass
class EmbeddingSemantics:
    """
    Class for performing embedding arithmetic.
    Embeddings are loaded from embeddings file into a dictionary, and
    the dictionary of embeddings is used to create the object.
    Embedding assumed to be in format: [segment, vector_wts+]+
    """
    embeddings: dict
    n_neighbors: int = field(default=3)

    vocab: dict = field(init=False)
    # vectors: list = field(init=False)  # temporary
    neighbors: NearestNeighbors = field(init=False)

    def __post_init__(self):
        self.vocab = {idx: seg for idx, seg in enumerate(embeddings.keys())}
        # self.vectors = list(embeddings.values())
        self.neighbors = NearestNeighbors(n_neighbors=self.n_neighbors)
        # self.knn.fit(self.vectors, list(self.vocab.values()))
        self.neighbors.fit(list(self.embeddings.values()))

        np.set_printoptions(precision=4, suppress=True)

    def resolve_(self, seg):
        if isinstance(seg, numpy.ndarray):
            # nothing to resolve or calculate
            return seg
        if isinstance(seg, list):
            # average over list of segment or index references
            return self.average_(seg)
        # use standard segment reference
        seg_ = seg if isinstance(seg, str) else self.vocab[seg]
        return self.embeddings[seg_]

    def average_(self, seg_lst):
        # embeddings are indexed by segments
        # vectors = [self.embeddings[self.resolve(seg)] for seg in seg_lst]
        vectors = [self.resolve_(seg) for seg in seg_lst]
        return np.mean(vectors, axis=0)

    # All segment references can be made lists.
    # Then all embeddings indexing would become average of list.
    def get_emb(self, seg):
        # seg_ = self.resolve(seg)
        # return self.embeddings[seg_]
        return self.resolve_(seg)

    def add_emb(self, segL, segR):
        # segL_ = self.resolve(segL)
        # segR_ = self.resolve(segR)
        # return self.embeddings[segL_] + embeddings[segR_]
        return self.resolve_(segL) + self.resolve_(segR)

    def sub_emb(self, segL, segR):
        # segL_ = self.resolve(segL)
        # segR_ = self.resolve(segR)
        # return self.embeddings[segL_] - embeddings[segR_]
        return self.resolve_(segL) - self.resolve_(segR)

    def analogy(self, segL, segM, segR):
        # right segment typically a segment reference
        # left and middle can be any reference.
        # this mimics the analogies problem.
        print(f"{segL} is {segM} as {segR} is to ...")
        return self.resolve_(segL) - self.resolve_(segM) + self.resolve_(segR)

    def nearest_analogy(self, segL, segM, segR):
        # Reports the nearest neighbors for the analogy.
        print(f"Nearest to:")
        self.nearest(self.analogy(segL, segM, segR))

    # def init_knn(self, k=5):
    #     self.knn = KNeighborsClassifier(k)
    #     # self.knn.fit(self.vectors, list(self.vocab.values()))
    #     self.knn.fit(list(self.embeddings.values()), list(self.vocab.values()))
    #     return self.knn

    def nearest(self, seg, n=None):
        n_ = n if n is not None else self.n_neighbors
        dst_lst, idx_lst = self.neighbors.kneighbors([self.resolve_(seg)], n_neighbors=n_)
        dst_lst = [dst for dst in dst_lst[0]]
        fmt = ', '.join(["{:.4f}"]*len(dst_lst))
        print(f"distance list: [{fmt.format(*dst_lst)}]")
        seg_lst = [es.vocab[idx] for idx in idx_lst[0]]
        print(f"segment list: {seg_lst}")


# def avg_emb_list(token, embeddings):
#     # embeddings are indexed by segments
#     vectors = [embeddings[seg] for seg in token]
#     return np.mean(vectors, axis=0)
#
#
# def add_emb(tokenL, tokenR, embeddings):
#     return embeddings[tokenL] + embeddings[tokenR]
#
#
# def sub_emb(tokenL, tokenR, embeddings):
#     return embeddings[tokenL] - embeddings[tokenR]
#
#
# def init_knn(vectors, targets, k=5):
#     knn = KNeighborsClassifier(k)
#     knn.fit(vectors, targets)
#     return knn
#

if __name__ == "__main__":
    embeddings = load_embeddings("SK_fullvowels_emb.tsv")

    # vocab = {idx: seg for idx, seg in enumerate(embeddings.keys())}
    # vectors = list(embeddings.values())
    # print(vocab)

    # for key, vec in embeddings.items():
    #     print(f'{key}: {vec}')
    # vocab = list(embeddings.keys())
    # print(vocab)
    # knn = init_knn(vectors, list(vocab.values()))

    # print("vector[5]", vectors[5])
    # print("Nearest neighbors to 5 and 7", knn.kneighbors([vectors[5], vectors[7]]))
    # print("KNN to vector[5]", knn.kneighbors([vectors[5]]))

    # print(knn.predict([vectors[5], vectors[7]]))
    # print(f"nearest neighbors to {vocab[12]}")
    # d_lst, n_lst = knn.kneighbors([vectors[12]])
    # print("distance list:", d_lst)
    # print("index list:", n_lst)

    # seg_lst = [vocab[n] for n in n_lst[0]]
    # print(f'segment list {vocab[12]}: {seg_lst}')

    # print("vector[0], unk", vectors[0])
    # print("vector[12], +", vectors[12])
    #
    # print("Vowel average:", avg_emb_list(["a", "o", "i"], embeddings))
    #
    # print("vector a", embeddings['a'])
    # print("vector i", embeddings['i'])
    # print("vectors a + i", add_emb('a', 'i', embeddings))

    # repeat with the class definition.
    es = EmbeddingSemantics(embeddings)
    print(type(es))
    # print(dir(es))
    print(es.vocab)
    #knn = es.neighbors  # es.init_knn()
    # print("vector[5]", es.vectors[5])
    print("w", es.get_emb("w"))
    print("type of emb", type(x := es.get_emb("w")), x.shape)
    # print("Nearest neighbors to 5 and 7", knn.kneighbors([vectors[5], vectors[7]]))
    # print("KNN to vector[5]", knn.kneighbors([es.vectors[5]]))
    # print("KNN to 'w'", knn.kneighbors([es.get_emb("w")]))
    print(f"nearest neighbors to {'w'}")
    es.nearest('w')

    # print(f"nearest neighbors to {es.vocab[12]}")
    # d_lst, n_lst = knn.kneighbors([es.vectors[12]])
    # print("distance list:", d_lst)
    # print("index list:", n_lst)
    # seg_lst = [es.vocab[n] for n in n_lst[0]]
    # print(f'segment list {es.vocab[12]}: {seg_lst}')

    print(f"nearest neighbors to {'+'}")
    es.nearest('+', 5)
    # d_lst, n_lst = knn.kneighbors([es.get_emb("+")])
    # print("distance list:", d_lst)
    # print("index list:", n_lst)
    # seg_lst = [es.vocab[n] for n in n_lst[0]]
    # print(f"segment list {'+'}: {seg_lst}")

    # print("vector[0], unk", es.vectors[0])
    # print("vector[12], +", es.vectors[12])
    print("<unk>", es.get_emb('<unk>'))
    print("+", es.get_emb('+'))

    print("Vowel average:", es.average_(["a", "o", "i"]))
    print("Vowel average:", es.average_([7, "o", 4]))
    print("type embedding", type(x := es.average_([7, 'w'])), x.shape)

    print("vector a", es.embeddings['a'])
    print("vector i", es.embeddings['i'])
    print("type embedding", type(x := es.embeddings['a']), x.shape)
    print("vectors a + i", es.add_emb('a', 'i'))
    print("type embeddings", type(x := es.add_emb('a', 'i')), x.shape)

    es.nearest_analogy('o', ['i', 'ɨ'], 'a')
