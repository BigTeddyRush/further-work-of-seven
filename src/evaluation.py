import json, glob, random, torch, argparse

from operator import countOf
from seven import *
from eprover import *

#=========================================================================================
# candidates
#=========================================================================================
def select_candidates(src: str, n: int):
    candidates = list()

    files = glob.glob(f"./goals/{src}/*.tstp")
    random.shuffle(files)

    for i, file in enumerate(files):
        print(f"Test {i}: {file}")
        result, _ = run_eprover("./adimen.sumo.tstp", file)
        print("    ->", result)

        if result == ProverResult.TIME_OUT:
            candidates.append(file)

        if len(candidates) >= n:
            break

    with open(f"./{src}_candidates.json", 'w') as file:
        json.dump(candidates, file, indent=2)


#=========================================================================================
# evaluation
#=========================================================================================
def write_results(results: dict[str,ProverResult], path: str):
    with open(path, 'w') as file:
        json.dump(results, file, indent=2, default=str)

    print(f"Solved {countOf(results.values(), ProverResult.PROOF_FOUND)} out of {len(results)} tests.")

class TestData():
    candidates: list[str]
    encoder: Encoder
    tensors: EncOntology
    ontology: Ontology

    def __init__(self, path) -> None:
        with open(path, 'r') as f:
            self.candidates = json.load(f)

        self.encoder = Encoder()
        self.tensors = torch.load("./axioms.pt")
        self.ontology = read_tstp("./adimen.sumo.tstp")

def test_union(data: TestData, b: float, k: int, **kwargs) -> dict[str, ProverResult]:
    # write filter to file
    filter_path = "./filter.txt"
    with open(filter_path, 'w') as file:
        file.write(f"filter = {create_sine_filter(b, k)}")

    results = dict()
    for i, c in enumerate(data.candidates):
        #selection_path = union_select(c, data.encoder, data.tensors, data.ontology, filter=filter_path, **kwargs)

        print(f"Test {i}: {c}")
        result = run_eprover('adimen.sumo.tstp', c)
        print("    ->", result)

        results[c] = result

    return results

tests_union = {
    'auto': {
        'type': 'union',
        'args': { 'n': 160, 'b': 2.0, 'k': 3 }
    }
}

def evaluate(src: str, count: int = None):
    if count:
        select_candidates(src, count)

    data = TestData(f"./{src}_candidates.json")

    tests = dict()
    tests |= tests_union

    for name, test in tests.items():
        print(f"Testing {name}")

        match test['type']:
            case 'union':
                results = test_union(data, **test['args'])

        write_results(results, f"./results/just_proofed_without_auto_without_union_{src}_{name}.json")

def count_selected(src: str, name: str, b: float, k: int):
    data = TestData(f"./{src}_candidates.json")

    tests = [160]

    # write filter to file
    filter_path = "./filter.txt"
    with open(filter_path, 'w') as file:
        file.write(f"filter = {create_sine_filter(b, k)}")

    results = dict()
    for n in tests:
        print(f"Counting for n={n}")

        counts = []
        for i, c in enumerate(data.candidates):
            c_name, conjecture = read_tstp_single(c)
            path = f"./selection/{c_name}_{name}.tstp"
            
            encoded_conjecture = data.encoder.encode_axiom(conjecture)

            selection = select(encoded_conjecture, data.tensors, n=n)

            write_tstp(path, {s: data.ontology[s] for s in selection}, type='conjecture')

            # sine selection
            run_e_axfilter(["./adimen.sumo.tstp", c, path], filter_path, path)

            # remove conjectures from selection
            axioms = read_tstp(path, type='axiom')
            write_tstp(path, axioms)


            counts.append(len(axioms))
            print(f"(n{n}|{i}) {c}: {len(axioms)}")

        results[n] = counts
    write_results(results, f"./results/counts/{src}_{name}.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', default="whitebox")
    parser.add_argument('--select')
    args = parser.parse_args()

    evaluate(args.src, args.select)

    #count_selected(args.src, "b20_k03", b=2.0, k=3)
    #count_selected(args.src, "b20_kUU", b=2.0, k=2147483647)
    #count_selected(args.src, "b30_kUU", b=3.0, k=2147483647)