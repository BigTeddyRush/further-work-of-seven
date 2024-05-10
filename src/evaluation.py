import json, glob, random, torch, typing, argparse

from operator import countOf
from seven import *
from eprover import *

from statistics import mean

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


def test_seven(data: TestData, **kwargs) -> dict[str, ProverResult]:
    results = dict()
    for i, c in enumerate(data.candidates):
        selection_path = seven_select(c, data.encoder, data.tensors, data.ontology, **kwargs)

        print(f"Test {i}: {c}")
        result, _ = run_eprover(selection_path, c)
        print("    ->", result)

        results[c] = result

    return results

def test_union(data: TestData, b: float, k: int, **kwargs) -> dict[str, ProverResult]:
    # write filter to file
    filter_path = "./filter.txt"
    with open(filter_path, 'w') as file:
        file.write(f"filter = {create_sine_filter(b, k)}")

    results = dict()
    for i, c in enumerate(data.candidates):
        selection_path = union_select(c, data.encoder, data.tensors, data.ontology, filter=filter_path, **kwargs)

        print(f"Test {i}: {c}")
        result, _ = run_eprover(selection_path, c)
        print("    ->", result)

        results[c] = result

    return results

def test_sine(data: TestData, b: float, k: int) -> dict[str, ProverResult]:
    filter = create_sine_filter(b, k)

    results = dict()
    for i, c in enumerate(data.candidates):

        print(f"Test {i}: {c}")
        result, _ = run_eprover("./adimen.sumo.tstp", c, [f'--sine={filter}'])
        print("    ->", result)

        results[c] = result

    return results

tests_sine = {
    'sine_b50_k04': {
        'type': 'sine',
        'args': { 'b': 5.0, 'k': 4 }
    },
    'sine_b12_k02': {
        'type': 'sine',
        'args': { 'b': 1.2, 'k': 2 }
    },
    'sine_b15_kUU': {
        'type': 'sine',
        'args': { 'b': 1.5, 'k': 2147483647 }
    },
    'sine_b20_k03': {
        'type': 'sine',
        'args': { 'b': 2.0, 'k': 3 }
    },
    'sine_b60_k05': {
        'type': 'sine',
        'args': { 'b': 6.0, 'k': 5 }
    },
    'sine_b20_kUU': {
        'type': 'sine',
        'args': { 'b': 2.0, 'k': 2147483647 }
    },
}

tests_seven = {
    'seven_n50': {
        'type': 'seven',
        'args': { 'n': 50 }
    },
    'seven_n100': {
        'type': 'seven',
        'args': { 'n': 100 }
    },
    'seven_n200': {
        'type': 'seven',
        'args': { 'n': 200 }
    },
    'seven_n300': {
        'type': 'seven',
        'args': { 'n': 300 }
    },
    'seven_n400': {
        'type': 'seven',
        'args': { 'n': 400 }
    },
    'seven_n500': {
        'type': 'seven',
        'args': { 'n': 500 }
    },

    'seven_t08': {
        'type': 'seven',
        'args': { 't': 0.8 }
    },
    'seven_t06': {
        'type': 'seven',
        'args': { 't': 0.6 }
    },
    'seven_t04': {
        'type': 'seven',
        'args': { 't': 0.4 }
    },
}

tests_union = {
    'union_n20_b20_k03': {
        'type': 'union',
        'args': { 'n': 20, 'b': 2.0, 'k': 3 }
    },
    'union_n40_b20_k03': {
        'type': 'union',
        'args': { 'n': 40, 'b': 2.0, 'k': 3 }
    },
    'union_n60_b20_k03': {
        'type': 'union',
        'args': { 'n': 60, 'b': 2.0, 'k': 3 }
    },
    'union_n80_b20_k03': {
        'type': 'union',
        'args': { 'n': 80, 'b': 2.0, 'k': 3 }
    },
    'union_n100_b20_k03': {
        'type': 'union',
        'args': { 'n': 100, 'b': 2.0, 'k': 3 }
    },
    'union_n120_b20_k03': {
        'type': 'union',
        'args': { 'n': 120, 'b': 2.0, 'k': 3 }
    },
    'union_n140_b20_k03': {
        'type': 'union',
        'args': { 'n': 140, 'b': 2.0, 'k': 3 }
    },
    'union_n160_b20_k03': {
        'type': 'union',
        'args': { 'n': 160, 'b': 2.0, 'k': 3 }
    },
    'union_n180_b20_k03': {
        'type': 'union',
        'args': { 'n': 180, 'b': 2.0, 'k': 3 }
    },

    'union_n20_b60_k05': {
        'type': 'union',
        'args': { 'n': 20, 'b': 6.0, 'k': 5 }
    },
    'union_n40_b60_k05': {
        'type': 'union',
        'args': { 'n': 40, 'b': 6.0, 'k': 5 }
    },
    'union_n60_b60_k05': {
        'type': 'union',
        'args': { 'n': 60, 'b': 6.0, 'k': 5 }
    },
    'union_n80_b60_k05': {
        'type': 'union',
        'args': { 'n': 80, 'b': 6.0, 'k': 5 }
    },
    'union_n100_b60_k05': {
        'type': 'union',
        'args': { 'n': 100, 'b': 6.0, 'k': 5 }
    },
    'union_n120_b60_k05': {
        'type': 'union',
        'args': { 'n': 120, 'b': 6.0, 'k': 5 }
    },
    'union_n140_b60_k05': {
        'type': 'union',
        'args': { 'n': 140, 'b': 6.0, 'k': 5 }
    },
    'union_n160_b60_k05': {
        'type': 'union',
        'args': { 'n': 160, 'b': 6.0, 'k': 5 }
    },
    'union_n180_b60_k05': {
        'type': 'union',
        'args': { 'n': 180, 'b': 6.0, 'k': 5 }
    },

    'union_n20_b20_kUU': {
        'type': 'union',
        'args': { 'n': 20, 'b': 2.0, 'k': 2147483647 }
    },
    'union_n40_b20_kUU': {
        'type': 'union',
        'args': { 'n': 40, 'b': 2.0, 'k': 2147483647 }
    },
    'union_n60_b20_kUU': {
        'type': 'union',
        'args': { 'n': 60, 'b': 2.0, 'k': 2147483647 }
    },
    'union_n80_b20_kUU': {
        'type': 'union',
        'args': { 'n': 80, 'b': 2.0, 'k': 2147483647 }
    },
    'union_n100_b20_kUU': {
        'type': 'union',
        'args': { 'n': 100, 'b': 2.0, 'k': 2147483647 }
    },
    'union_n120_b20_kUU': {
        'type': 'union',
        'args': { 'n': 120, 'b': 2.0, 'k': 2147483647 }
    },
    'union_n140_b20_kUU': {
        'type': 'union',
        'args': { 'n': 140, 'b': 2.0, 'k': 2147483647 }
    },
    'union_n160_b20_kUU': {
        'type': 'union',
        'args': { 'n': 160, 'b': 2.0, 'k': 2147483647 }
    },
    'union_n180_b20_kUU': {
        'type': 'union',
        'args': { 'n': 180, 'b': 2.0, 'k': 2147483647 }
    },

    'union_t08_b20_k03': {
       'type': 'union',
       'args': { 't': 0.8, 'b': 2.0, 'k': 3 }
    },
    'union_t06_b20_k03': {
       'type': 'union',
       'args': { 't': 0.6, 'b': 2.0, 'k': 3 }
    },
    'union_t04_b20_k03': {
       'type': 'union',
       'args': { 't': 0.4, 'b': 2.0, 'k': 3 }
    },
    'union_t08_b60_k05': {
        'type': 'union',
        'args': { 't': 0.8, 'b': 6.0, 'k': 5 }
    },
    'union_t06_b60_k05': {
       'type': 'union',
        'args': { 't': 0.6, 'b': 6.0, 'k': 5 }
    },
    'union_t04_b60_k05': {
       'type': 'union',
        'args': { 't': 0.4, 'b': 6.0, 'k': 5 }
    },
    'union_t08_b20_kUU': {
        'type': 'union',
        'args': { 't': 0.8, 'b': 2.0, 'k': 2147483647 }
    },
    'union_t06_b20_kUU': {
        'type': 'union',
        'args': { 't': 0.6, 'b': 2.0, 'k': 2147483647 }
    },
    'union_t04_b20_kUU': {
        'type': 'union',
        'args': { 't': 0.4, 'b': 2.0, 'k': 2147483647 }
    },
}

def evaluate(src: str, count: int = None):
    if count:
        select_candidates(src, count)

    data = TestData(f"./{src}_candidates.json")

    tests = dict()
    tests |= tests_sine
    tests |= tests_seven
    tests |= tests_union

    for name, test in tests.items():
        print(f"Testing {name}")

        match test['type']:
            case 'sine':
                results = test_sine(data, **test['args'])
            case 'seven':
                results = test_seven(data, **test['args'])
            case 'union':
                results = test_union(data, **test['args'])

        write_results(results, f"./results/{src}_{name}.json")

def count_thresholds(src: str, t: float, output_name: str):
    data = TestData(f"./{src}_candidates.json")

    results = dict()
    for c in data.candidates:
        name, conjecture = read_tstp_single(c)

        encoded_conjecture = data.encoder.encode_axiom(conjecture)
        selection = select_t(encoded_conjecture, data.tensors, t)

        results[name] = len(selection)

    print(f"Max: {max(results.values())}")
    print(f"Min: {min(results.values())}")
    print(f"Avg: {mean(results.values())}")

    with open(f"./{output_name}.json", 'w') as file:
        json.dump(results, file, indent=2, default=str)

def count_selected(src: str, name: str, b: float, k: int):
    data = TestData(f"./{src}_candidates.json")

    tests = [ 20, 40, 60, 80, 100, 120, 140, 160, 180 ]

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
            path = f"./selection/{c_name}.tstp"
            
            encoded_conjecture = data.encoder.encode_axiom(conjecture)

            selection = select(encoded_conjecture, data.tensors, n=n)

            write_tstp(path, {s: data.ontology[s] for s in selection}, type='conjecture')

            # sine selection
            run_e_axfilter(["./adimen.sumo.tstp", c, path], filter_path, path)

            # remove conjectures from selection
            axioms = read_tstp(path, type='axiom')

            counts.append(len(axioms))
            print(f"(n{n}|{i}) {c}: {len(axioms)}")

        results[n] = counts
    write_results(results, f"./results/counts/{src}_{name}.json")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', default="whitebox")
    parser.add_argument('--select')
    args = parser.parse_args()

    #evaluate(args.src, args.select)
    #count_thresholds(args.src, 0.4, "thresholds_04")
    #count_thresholds(args.src, 0.6, "thresholds_06")
    #count_thresholds(args.src, 0.8, "thresholds_08")

    #count_selected(args.src, "b60_k05", b=6.0, k=5)
    #count_selected(args.src, "b20_k03", b=2.0, k=3)
    count_selected(args.src, "b20_kUU", b=2.0, k=2147483647)