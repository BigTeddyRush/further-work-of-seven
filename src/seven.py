import torch
import numpy as np
from heapq import nlargest

from sentence_transformers import SentenceTransformer
from eprover import run_e_axfilter

from tstp_util import read_tstp, read_tstp_single, write_tstp
from translator import translate_axiom

#=========================================================================================
# encoding
#=========================================================================================
Ontology = dict[str,str]
EncOntology = dict[str, torch.tensor]

class Encoder():
    # math-similarity/Bert-MLM_arXiv-MP-class_zbMath MATHMODEL 768 dimensions max seq length 256
    # best model: sentence-transformers/all-mpnet-base-v2 768 dimensions max seq length 384
    # sentence-transformers/paraphrase-albert-small-v2 768 dimensions max seq length 256
    def __init__(self, model: str = 'all-mpnet-base-v2') -> None:
        self.model = SentenceTransformer(model)

    def encode_axiom(self, axiom: str) -> torch.Tensor:
        sentence = translate_axiom(axiom)
        return self.model.encode(sentence, convert_to_tensor=True)
    
    def encode_ontology(self, ontology: Ontology) -> EncOntology:
        return {name: self.encode_axiom(axiom) for name, axiom in ontology.items()}


#=========================================================================================
# SeVEn selection
#=========================================================================================
def cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def select(conjecture: torch.Tensor, tensors: EncOntology, n: int) -> dict[str,float]:
    distances = {name: cosine_sim(conjecture, axiom) for name, axiom in tensors.items()}
    return dict(nlargest(n, distances.items(), key=lambda kv: kv[1]))

def select_t(conjecture: torch.Tensor, tensors: EncOntology, t: float) -> dict[str,float]:
    distances = {name: cosine_sim(conjecture, axiom) for name, axiom in tensors.items()}
    return {n: d for n, d in distances.items() if d >= t}


def seven_select(goal: str, encoder: Encoder, tensors: EncOntology, ontology: Ontology, **kwargs) -> str:
    name, conjecture = read_tstp_single(goal)
    path = f"./selection/{name}.tstp"
    
    encoded_conjecture = encoder.encode_axiom(conjecture)

    # selection
    n = kwargs.pop('n', 100)
    t = kwargs.pop('t', None)

    if t:
        selection = select_t(encoded_conjecture, tensors, t=t)
    else:
        selection = select(encoded_conjecture, tensors, n=n)
    
    write_tstp(path, {name: ontology[name] for name in selection})
    return path

def seven_select_t(path: str, conjecture: torch.Tensor, tensors: EncOntology, ontology: Ontology, t: float):
    selection = select_t(conjecture, tensors, t=t)
    write_tstp(path, {name: ontology[name] for name in selection})

#=========================================================================================
# SeVEn union SInE selection
#=========================================================================================
def union_select(goal: str, encoder: Encoder, tensors: EncOntology, ontology: Ontology, filter: str, **kwargs) -> str:
    name, conjecture = read_tstp_single(goal)
    path = f"./selection/{name}.tstp"
    
    encoded_conjecture = encoder.encode_axiom(conjecture)

    # seven selection
    n = kwargs.pop('n', 20)
    t = kwargs.pop('t', None)

    if t:
        selection = select_t(encoded_conjecture, tensors, t=t)
    else:
        selection = select(encoded_conjecture, tensors, n=n)

    write_tstp(path, {name: ontology[name] for name in selection}, type='conjecture')

    # sine selection
    run_e_axfilter(["./adimen.sumo.tstp", goal, path], filter, path)

    # remove conjectures from selection
    axioms = read_tstp(path, type='axiom')
    write_tstp(path, axioms)

    return path

def prepare_ontology(src_path: str, dst_path: str):
    ontology = read_tstp(src_path)

    encoder = Encoder()
    tensors = encoder.encode_ontology(ontology)

    torch.save(tensors, dst_path)

if __name__ == "__main__":
    import time
    print("Encoding Adimen-SUMO (./adimen.sumo.tstp)")
    start = time.perf_counter()
    prepare_ontology("./adimen.sumo.tstp", "./axioms.pt")
    end = time.perf_counter()
    print(f"Done in {end - start:0.2f} seconds")
    print("Encoded axioms in './adimen.sumo.tstp'")



