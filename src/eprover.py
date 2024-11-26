import subprocess, re, os
from enum import Enum

"""
GSinE(<g-measure>, hypos|nohypos, <benvolvence>, <generosity>, <rec-depth>, <set-size>, <set-fraction> [,addnosymb|ignorenosymb])

benevolence: is a floating point value that determines how much more general a function symbol in a clause or formula is allowed to be relative to the least general one to be still considered for the D-relation.

rec-depth: determines the maximal number of iterations of the selection algorithm.

set-size: gives an absolute upper bound for the number of clauses and formulas selected.
"""

def create_sine_filter(benevolence: float, rec_depth: int) -> str:
    return f"GSinE(CountFormulas,nohypos,{benevolence},9223372036854775807,{rec_depth},20000,1.0)"

class ProverResult(Enum):
    ERROR = 0
    COUNTER_SATISFIABLE = 1
    GAVE_UP = 2
    TIME_OUT = 3
    PROOF_FOUND = 4

def run_eprover(base: str|list[str], args: list[str] = []) -> tuple[ProverResult, str]:
    cmd = [
        'vampire',
        '--time_limit', '15s',
        '--input_syntax', 'tptp'
    ]
    cmd.extend(args)

    if type(base) is str:
        cmd.append(base)
    else:
        cmd.extend(base)

    with subprocess.Popen(cmd, stdout=subprocess.PIPE) as process:
        output = process.stdout.read()

    return output

def run_e_axfilter(files: str|list[str], filter_path: str, out_path: str):
    cmd = [
        'e_axfilter',
        '-s',
        '--tstp-format',
        f'--filter={filter_path}'
    ]
    if type(files) is str:
        cmd.append(files)
    else:
        cmd.extend(files)

    with subprocess.Popen(cmd, stdout=subprocess.PIPE) as process:
        output = process.stdout.read()

    #print(output)

    path = re.search(r"filter goes into file ((\w+\.)+p)", str(output)).group(1)
    os.replace(path, out_path)