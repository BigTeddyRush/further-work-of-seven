import re, json, torch

from eprover import ProverResult, run_eprover
from seven import read_tstp_single, Encoder, select, cosine_sim

def get_proof_axioms(base: str, problem: str) -> set[str]:
    result, output = run_eprover(base, problem, ['--proof-object=1'])

    if result != ProverResult.PROOF_FOUND:
        print("ERROR: Failed to find proof")

    return set(re.findall(r"fof\((\w+), axiom,", output))

def find_intersections(in_path: str, out_path: str, limit: int, n: int):
    with open(in_path, 'r') as f:
        problems = [k for k,v in json.load(f).items() if v == str(ProverResult.COUNTER_SATISFIABLE)]

    encoder = Encoder()
    ontology = torch.load("./axioms.pt")

    results = dict()
    for p in problems[:limit]:
        print("Finding intersection for", p)
        path = f"./whitebox/{p}.adimen.tstp"
        proof = get_proof_axioms("./adimen.sumo.tstp", path)

        _, conjugate = read_tstp_single(path)
        encoded_conjugate = encoder.encode_axiom(conjugate)
        selection = select(encoded_conjugate, ontology, n=n)
        selected_names = set(selection.keys())

        weigthed_proof = {n: cosine_sim(encoded_conjugate, ontology[n]) for n in proof}

        results[p] = {
            'proof': dict(sorted(weigthed_proof.items(), key=lambda kv: kv[1])),
            'count': len(weigthed_proof),
            'selection': selected_names,
            'range': [min(selection.values()), max(selection.values())],
            'intersection': selected_names.intersection(proof)
        }

    with open(out_path, 'w') as file:
        json.dump(results, file, indent=2, default=str)

if __name__ == "__main__":
    #find_intersections("./whitebox_success_results.json", "./whitebox_intersection_100.json", limit=10, n=100)
    #find_intersections("./whitebox_success_results.json", "./whitebox_intersection_200.json", limit=10, n=200)
    #find_intersections("./whitebox_success_results.json", "./whitebox_intersection_300.json", limit=10, n=300)
    find_intersections("./hyponym_success_results.json", "./hyponym_intersection_100.json", limit=10, n=100)
    find_intersections("./hyponym_success_results.json", "./hyponym_intersection_200.json", limit=10, n=200)
    find_intersections("./hyponym_success_results.json", "./hyponym_intersection_300.json", limit=10, n=300)
