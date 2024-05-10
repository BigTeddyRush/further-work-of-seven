import subprocess, re, os
from enum import Enum

"""
gf500_gu_R04_F100_L20000 = GSinE(CountFormulas, nohypos, 5.000000, 9223372036854775807, 4, 20000, 1.000000)
gf120_gu_RUU_F100_L00500 = GSinE(CountFormulas, nohypos, 1.200000, 9223372036854775807, 2147483647, 500, 1.000000)
gf120_gu_R02_F100_L20000 = GSinE(CountFormulas, nohypos, 1.200000, 9223372036854775807, 2, 20000, 1.000000)
gf150_gu_RUU_F100_L20000 = GSinE(CountFormulas, nohypos, 1.500000, 9223372036854775807, 2147483647, 20000, 1.000000)
gf120_gu_RUU_F100_L00100 = GSinE(CountFormulas, nohypos, 1.200000, 9223372036854775807, 2147483647, 100, 1.000000)
gf200_gu_R03_F100_L20000 = GSinE(CountFormulas, nohypos, 2.000000, 9223372036854775807, 3, 20000, 1.000000)
gf600_gu_R05_F100_L20000 = GSinE(CountFormulas, nohypos, 6.000000, 9223372036854775807, 5, 20000, 1.000000)
gf200_gu_RUU_F100_L20000 = GSinE(CountFormulas, nohypos, 2.000000, 9223372036854775807, 2147483647, 20000, 1.000000)
gf120_gu_RUU_F100_L01000 = GSinE(CountFormulas, nohypos, 1.200000, 9223372036854775807, 2147483647, 1000, 1.000000)
gf500_h_gu_R04_F100_L20000 = GSinE(CountFormulas, hypos, 5.000000, 9223372036854775807, 4, 20000, 1.000000)
gf120_h_gu_RUU_F100_L00500 = GSinE(CountFormulas, hypos, 1.200000, 9223372036854775807, 2147483647, 500, 1.000000)
gf120_h_gu_R02_F100_L20000 = GSinE(CountFormulas, hypos, 1.200000, 9223372036854775807, 2, 20000, 1.000000)
gf150_h_gu_RUU_F100_L20000 = GSinE(CountFormulas, hypos, 1.500000, 9223372036854775807, 2147483647, 20000, 1.000000)
gf120_h_gu_RUU_F100_L00100 = GSinE(CountFormulas, hypos, 1.200000, 9223372036854775807, 2147483647, 100, 1.000000)
gf200_h_gu_R03_F100_L20000 = GSinE(CountFormulas, hypos, 2.000000, 9223372036854775807, 3, 20000, 1.000000)
gf600_h_gu_R05_F100_L20000 = GSinE(CountFormulas, hypos, 6.000000, 9223372036854775807, 5, 20000, 1.000000)
gf200_h_gu_RUU_F100_L20000 = GSinE(CountFormulas, hypos, 2.000000, 9223372036854775807, 2147483647, 20000, 1.000000)
gf120_h_gu_RUU_F100_L01000 = GSinE(CountFormulas, hypos, 1.200000, 9223372036854775807, 2147483647, 1000, 1.000000)

GSinE(<g-measure>, hypos|nohypos, <benvolvence>, <generosity>, <rec-depth>, <set-size>, <set-fraction> [,addnosymb|ignorenosymb])

benevolence: is a floating point value that determines how much more general a function symbol in a clause or formula is allowed to be relative to the least general one to be still considered for the D-relation.

rec-depth: determines the maximal number of iterations of the selection algorithm.

set-size: gives an absolute upper bound for the number of clauses and formulas selected.

gf500_gu_R04_F100_L20000 = GSinE(CountFormulas, nohypos, 5.000000, 9223372036854775807, 4, 20000, 1.000000)
gf120_gu_R02_F100_L20000 = GSinE(CountFormulas, nohypos, 1.200000, 9223372036854775807, 2, 20000, 1.000000)
gf150_gu_RUU_F100_L20000 = GSinE(CountFormulas, nohypos, 1.500000, 9223372036854775807, 2147483647, 20000, 1.000000)
gf200_gu_R03_F100_L20000 = GSinE(CountFormulas, nohypos, 2.000000, 9223372036854775807, 3, 20000, 1.000000)
gf600_gu_R05_F100_L20000 = GSinE(CountFormulas, nohypos, 6.000000, 9223372036854775807, 5, 20000, 1.000000)
gf200_gu_RUU_F100_L20000 = GSinE(CountFormulas, nohypos, 2.000000, 9223372036854775807, 2147483647, 20000, 1.000000)
"""

def create_sine_filter(benevolence: float, rec_depth: int) -> str:
    return f"GSinE(CountFormulas,nohypos,{benevolence},9223372036854775807,{rec_depth},20000,1.0)"

class ProverResult(Enum):
    ERROR = 0
    COUNTER_SATISFIABLE = 1
    GAVE_UP = 2
    TIME_OUT = 3
    PROOF_FOUND = 4

def run_eprover(base: str|list[str], problem: str, args: list[str] = []) -> tuple[ProverResult, str]:
    cmd = [
        'eprover',
        '-s',
        '--tstp-format',
        '--soft-cpu-limit=15'
    ]
    cmd.extend(args)

    if type(base) is str:
        cmd.append(base)
    else:
        cmd.extend(base)

    cmd.append(problem)

    with subprocess.Popen(cmd, stdout=subprocess.PIPE) as process:
        output = process.stdout.read()

    if b"status Theorem" in output:
        return ProverResult.PROOF_FOUND, output

    if b"status ResourceOut" in output:
        return ProverResult.TIME_OUT, output

    if b"status CounterSatisfiable" in output:
        return ProverResult.COUNTER_SATISFIABLE, output

    if b"status GaveUp" in output:
        return ProverResult.GAVE_UP, output

    return ProverResult.ERROR, output

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