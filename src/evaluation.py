import json, glob, random, torch, argparse

from operator import countOf
from seven import *
from eprover import *

import sys

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

def reformat_tstp_file(input_file_path, output_file_path):
    with open(input_file_path, 'r') as infile:
        # Read and join the lines to form a single line
        single_line_content = ''.join(line.strip() for line in infile if line.strip())

    with open(output_file_path, 'w') as outfile:
        # Write the single line content to the output file
        outfile.write(single_line_content)


def test_union(data: TestData, b: float, k: int, mode:str = None, union: str = None, **kwargs) -> dict[str, ProverResult]:
    # write filter to file
    filter_path = "./filter.txt"
    
    if mode:
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
        selection_path_final = f"./selection/{i}.tstp"
        print(selection_path_final)
        # delete existing content
        with open(selection_path_final, 'w') as f:
            pass
        
        # write conjecture in one line
        reformat_tstp_file(c, selection_path_final)
        
        if union:
            print("union")
            selection_path = union_select(c, data.encoder, data.tensors, data.ontology, filter=filter_path, **kwargs)
        else:
            # add adimen sumo to selection path final if no union
            print("no union")
            print("merge")
            merge_into_file2_nounion("./adimen.sumo.tstp", selection_path_final)
            
        if mode:
            merge_into_file2(path_A12, selection_path)
            merge_into_file2(path_A15, selection_path)
            merge_into_file2(path_A8, selection_path)
            merge_into_file2(mergeA176, selection_path)
            merge_into_file2(mergeA178, selection_path)
            merge_into_file2(mergeA181, selection_path)
            merge_into_file2(mergeA594, selection_path)
            merge_into_file2(typeA3, selection_path)
            merge_into_file2(mergeA2239, selection_path)
            merge_into_file2(mergeA2244, selection_path)
            merge_into_file2(typeA5, selection_path)
            merge_into_file2(path_A7, selection_path)    
            merge_into_file2(miloA4176, selection_path)
            merge_into_file2(typeA28, selection_path)  
            merge_into_file2(mergeA331, selection_path)
            merge_into_file2(mergeA324, selection_path)
            merge_into_file2(mergeA3134, selection_path)
            merge_into_file2(mergeA251, selection_path)
            merge_into_file2(mergeA599, selection_path)
            merge_into_file2(mergeA226, selection_path)
            merge_into_file2(mergeA330, selection_path)
            merge_into_file2(typeA68, selection_path)  
            merge_into_file2(mergeA3229, selection_path)
            merge_into_file2(mergeA257, selection_path)
            merge_into_file2(predefinitionsA24, selection_path)
            
        if union:
            merge_into_file2(selection_path, selection_path_final)
        
        print(f"Test {i}: {c}")
        result = run_eprover(selection_path_final)
        print("    ->", result)

        results[c] = result

    return results

def merge_into_file2(file1_path, file2_path):
    """
    Merge the unique contents of file1 into file2 and save it back to file2.
    
    Args:
    - file1_path: path to the first .tstp file
    - file2_path: path to the second .tstp file (which will be updated with the merged contents)
    """
    try:
        with open(file1_path, 'r') as file1:
            content1 = file1.readlines()
        
        with open(file2_path, 'r') as file2:
            content2 = file2.readlines()
        
        # Combine and get unique lines
        unique_lines = set(content2).union(content1)
        
        # Sort the lines if you want to keep a specific order
        merged_content = (unique_lines)
        
        with open(file2_path, 'w') as output_file:
            output_file.writelines(merged_content)
        
    except Exception as e:
        print(f"An error occurred: {e}")

def merge_into_file2_nounion(source_file_path, target_file_path):
    # Open the source file to read its content
    with open(source_file_path, 'r') as source_file:
        # Read the entire content of the source file
        source_content = source_file.read()
        
    # Open the target file in append mode to add the contents of the source file
    with open(target_file_path, 'a') as target_file:
        # Write the content from the source file into the target file
        target_file.write(source_content)



tests_union = {
    'union_n160_b20_k03': {
        'type': 'union',
        'args': { 'n': 160, 'b': 2.0, 'k': 3 }
    }
}

def evaluate(src: str, count: int = None, mode: str = None, union:str = None):
    if count:
        select_candidates(src, count)

    data = TestData(f"./{src}_candidates.json")

    tests = dict()
    tests |= tests_union

    for name, test in tests.items():
        print(f"Testing {name}")

        match test['type']:
            case 'union':
                results = test_union(data, union=union, mode=mode, **test['args'])

        write_results(results, f"./results/{src}_{name}_vampire_{union}_{mode}.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', default="whitebox")
    parser.add_argument('--select')
    args = parser.parse_args()

    evaluate(args.src, args.select, union="union")
    evaluate(args.src, args.select)
    
    
