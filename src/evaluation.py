import json, glob, random, torch, argparse

from operator import countOf
from seven import *
from eprover import *

import time

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

    def __init__(self, path, model) -> None:
        with open(path, 'r') as f:
            self.candidates = json.load(f)

        self.encoder = Encoder()
        model = f"./{model}.pt"
        print(model)
        self.tensors = torch.load(model)
        self.ontology = read_tstp("./adimen.sumo.tstp")


def test_union(data: TestData, b: float, k: int, addedAxiom: str = None, **kwargs) -> dict[str, ProverResult]:
    # write filter to file
    filter_path = "./filter.txt"
    print(b, k)
    with open(filter_path, 'w') as file:
        file.write(f"filter = {create_sine_filter(1, 1)}")
        
    path_A12 = union_select("predefinitionsA12.tstp", data.encoder, data.tensors, data.ontology, filter=filter_path, n=10)
    path_A15 = union_select("predefinitionsA15.tstp", data.encoder, data.tensors, data.ontology, filter=filter_path, n=10)
    path_A8 = union_select("predefinitionsA8.tstp", data.encoder, data.tensors, data.ontology, filter=filter_path, n=10)
    mergeA176 = union_select("mergeA176.tstp", data.encoder, data.tensors, data.ontology, filter=filter_path, n=10)
    mergeA178 = union_select("mergeA178.tstp", data.encoder, data.tensors, data.ontology, filter=filter_path, n=10)
    mergeA181 = union_select("mergeA181.tstp", data.encoder, data.tensors, data.ontology, filter=filter_path, n=10)
    mergeA594 = union_select("mergeA594.tstp", data.encoder, data.tensors, data.ontology, filter=filter_path, n=10)
    typeA3 = union_select("typeA3.tstp", data.encoder, data.tensors, data.ontology, filter=filter_path, n=10)
    mergeA2239 = union_select("mergeA2239.tstp", data.encoder, data.tensors, data.ontology, filter=filter_path, n=10)
    mergeA2244 = union_select("mergeA2244.tstp", data.encoder, data.tensors, data.ontology, filter=filter_path, n=10)
    typeA5 = union_select("typeA5.tstp", data.encoder, data.tensors, data.ontology, filter=filter_path, n=10)
    path_A7 = union_select("predefinitionsA7.tstp", data.encoder, data.tensors, data.ontology, filter=filter_path, n=10)
    miloA4176 = union_select("miloA4176.tstp", data.encoder, data.tensors, data.ontology, filter=filter_path, n=10)
    typeA28 = union_select("typeA28.tstp", data.encoder, data.tensors, data.ontology, filter=filter_path, n=10)
    mergeA331 = union_select("mergeA331.tstp", data.encoder, data.tensors, data.ontology, filter=filter_path, n=10)
    mergeA324 = union_select("mergeA324.tstp", data.encoder, data.tensors, data.ontology, filter=filter_path, n=10)
    mergeA3134 = union_select("mergeA3134.tstp", data.encoder, data.tensors, data.ontology, filter=filter_path, n=10)
    mergeA251 = union_select("mergeA251.tstp", data.encoder, data.tensors, data.ontology, filter=filter_path, n=10)
    mergeA599 = union_select("mergeA599.tstp", data.encoder, data.tensors, data.ontology, filter=filter_path, n=10)
    mergeA226 = union_select("mergeA226.tstp", data.encoder, data.tensors, data.ontology, filter=filter_path, n=10)
    mergeA330 = union_select("mergeA330.tstp", data.encoder, data.tensors, data.ontology, filter=filter_path, n=10)
    typeA68 = union_select("typeA68.tstp", data.encoder, data.tensors, data.ontology, filter=filter_path, n=10)
    mergeA3229 = union_select("mergeA3229.tstp", data.encoder, data.tensors, data.ontology, filter=filter_path, n=10)
    mergeA257 = union_select("mergeA257.tstp", data.encoder, data.tensors, data.ontology, filter=filter_path, n=10)
    predefinitionsA24 = union_select("predefinitionsA24.tstp", data.encoder, data.tensors, data.ontology, filter=filter_path, n=10)

    with open(filter_path, 'w') as file:
        file.write(f"filter = {create_sine_filter(b, k)}")

    results = dict()
    for i, c in enumerate(data.candidates):       
        selection_path = union_select(c, data.encoder, data.tensors, data.ontology, filter=filter_path, **kwargs)
        if addedAxiom == "addedAxiom8000":
            print("run with added axiom")
            merge_tstp_files(path_A12, selection_path, selection_path)
            merge_tstp_files(path_A15, selection_path, selection_path)
            merge_tstp_files(mergeA3229, selection_path, selection_path)
            merge_tstp_files(mergeA257, selection_path, selection_path)
            merge_tstp_files(predefinitionsA24, selection_path, selection_path)
            merge_tstp_files(path_A8, selection_path, selection_path)
            merge_tstp_files(mergeA176, selection_path, selection_path)
            merge_tstp_files(mergeA178, selection_path, selection_path)
            merge_tstp_files(mergeA181, selection_path, selection_path)
            merge_tstp_files(mergeA594, selection_path, selection_path)
            merge_tstp_files(typeA3, selection_path, selection_path)
            merge_tstp_files(mergeA2239, selection_path, selection_path)
            merge_tstp_files(mergeA2244, selection_path, selection_path)
            merge_tstp_files(typeA5, selection_path, selection_path)
            merge_tstp_files(path_A7, selection_path, selection_path)
            merge_tstp_files(miloA4176, selection_path, selection_path)
            merge_tstp_files(typeA28, selection_path, selection_path)
            merge_tstp_files(mergeA331, selection_path, selection_path)
            merge_tstp_files(mergeA324, selection_path, selection_path)
            merge_tstp_files(mergeA3134, selection_path, selection_path)
            merge_tstp_files(mergeA251, selection_path, selection_path)
            merge_tstp_files(mergeA599, selection_path, selection_path)
            merge_tstp_files(mergeA226, selection_path, selection_path)
            merge_tstp_files(mergeA330, selection_path, selection_path)
            merge_tstp_files(typeA68, selection_path, selection_path)
        
        print(f"Test {i}: {c}")
        
        start_time = time.time()  # Start timer
        result = run_eprover(selection_path, c)
        end_time = time.time()  # End timer
        
        execution_time = end_time - start_time  # Calculate elapsed time
        print("    ->", result, f"(Time taken: {execution_time:.4f} seconds)")
        result += tuple([execution_time])
        
        results[c] = result

    return results

def merge_tstp_files(file1_path, file2_path, output_path):
    """
    Merge two .tstp files into one.
    
    Args:
    - file1_path: path to the first .tstp file
    - file2_path: path to the second .tstp file
    - output_path: path where the merged file will be saved
    """
    try:
        # Use a set to store unique lines
        lines_set = set()
        
        # Read content from the first file
        with open(file1_path, 'r') as file1:
            lines_set.update(file1.readlines())
        
        # Read content from the second file
        with open(file2_path, 'r') as file2:
            lines_set.update(file2.readlines())
        
        # Write unique lines to the output file
        with open(output_path, 'w') as output_file:
            for line in sorted(lines_set):
                output_file.write(line)
        
    except Exception as e:
        print(f"An error occurred: {e}")

tests_union = {
    
    'union_n160_b20_k3': {
        'type': 'union',
        'args': { 'n': 160, 'b': 2.0, 'k': 3 }
    }
}

def evaluate(src: str, count: int = None, modelName: str = None, addedAxiom: str = None, **kwargs):
    if count:
        select_candidates(src, count)

    data = TestData(f"./{src}_candidates.json", model=modelName)

    tests = dict()
    tests |= tests_union

    for name, test in tests.items():
        print(f"Testing {name}")

        match test['type']:
            case 'union':
                results = test_union(data=data, addedAxiom=addedAxiom, **test['args'])

        write_results(results, f"./results/noauto_{src}_{name}_timer_union_{modelName}_{addedAxiom}.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', default="whitebox")
    parser.add_argument('--select')
    args = parser.parse_args()

    #evaluate(args.src, args.select, modelName="axioms_multi-qa-MiniLM-L6-cos-v1", addedAxiom=None)
    #evaluate(args.src, args.select, modelName="axioms_multi-qa-MiniLM-L6-cos-v1", addedAxiom="addedAxiom8000")
    evaluate(args.src, args.select, modelName="axioms_all-MiniLM-L6-v2", addedAxiom=None)
    evaluate(args.src, args.select, modelName="axioms_all-MiniLM-L6-v2", addedAxiom="addedAxiom8000")
    evaluate(args.src, args.select, modelName="axioms_paraphrase-MiniLM-L3-v2", addedAxiom=None)
    evaluate(args.src, args.select, modelName="axioms_paraphrase-MiniLM-L3-v2", addedAxiom="addedAxiom8000")
    