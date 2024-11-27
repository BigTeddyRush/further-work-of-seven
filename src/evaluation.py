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
        merge_into_file2(c, selection_path)
        print(f"Test {i}: {c}")
        result = run_eprover(selection_path)
        print("    ->", result)

        results[c] = result

    return results

def merge_into_file2(file1_path, file2_path):
    """
    Merge the contents of file1 into file2 and save it back to file2.
    
    Args:
    - file1_path: path to the first .tstp file
    - file2_path: path to the second .tstp file (which will be updated with the merged contents)
    """
    try:
        with open(file1_path, 'r') as file1:
            content1 = file1.readlines()
        
        with open(file2_path, 'r') as file2:
            content2 = file2.readlines()
        
        # Combine the contents
        merged_content = content2 + content1
        
        with open(file2_path, 'w') as output_file:
            output_file.writelines(merged_content)
        
        print(f"File '{file2_path}' has been updated with the merged content.")

    except Exception as e:
        print(f"An error occurred: {e}")


tests_union = {
    'union_n160_b20_k03': {
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

        write_results(results, f"./results/{src}_{name}_vampire_union.json")

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

    evaluate(args.src, args.select)

    count_selected(args.src, "b60_k05", b=6.0, k=5)
    count_selected(args.src, "b20_k03", b=2.0, k=3)
    count_selected(args.src, "b20_kUU", b=2.0, k=2147483647)