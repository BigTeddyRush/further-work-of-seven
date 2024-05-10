import re


def read_fof(fof: str) -> tuple[str,str,str]:
    fof = fof.replace('fof(', '').replace(').', '')
    name, type, axiom = fof.split(',', 2)
    return name.strip(), type.strip(), axiom

def read_tstp(filename: str, type: str = None) -> dict[str,str]:
    with open(filename, 'r') as file:
        filetext = file.read()

    axioms = dict()
    for fof in re.findall("fof\(.*?\)\.", filetext, flags=re.DOTALL):
        n, t, a = read_fof(fof)
        if not type or type == t:
            axioms[n] = a
    return axioms

def read_tstp_single(filename: str) -> tuple[str,str]:
    with open(filename, 'r') as file:
        filetext = file.read()

    match = re.search("fof\(.*?\)\.", filetext, flags=re.DOTALL)
    name, _, axiom = read_fof(match.group(0))
    return name, axiom

def write_tstp(filename: str, axioms: dict[str,str], type: str='axiom', mode='w'):
    with open(filename, mode) as file:
        for name in axioms:
            file.write(f"fof({name}, {type}, {axioms[name]}).\n")