import re, json
from fof_parser import parse_axiom, TreeNode, TreeNodeType
from optimiser import optimise_ast
from symbols import functions, predicates

def camel_case_split(name):
    return re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', name)).split()

def translate_constant(node: TreeNode) -> str:
    value = node.value.removeprefix('c__')

    if value.endswith('Fn'):
        return f"the function {value}"

    if value[0].islower():
        return f"the predicate {value}"

    splitted = camel_case_split(value)
    return ' '.join([s.lower() for s in splitted])

def translate_term(node: TreeNode) -> str:
    if node.type == TreeNodeType.VARIABLE:
        return node.value

    if node.type == TreeNodeType.CONSTANT:
        return translate_constant(node)

    value = node.value.removeprefix('f__')
    args = [translate_term(c) for c in node.children]

    if value in functions:
        return functions[value].format(*args)

    return f"{value}({','.join(args)})"

negations = {
    ' is ': ' is not ',
    ' are ': ' are not ',
    ' has ': ' does not have ',
    ' have ': ' do not have '
}

def translate_prediacte_symbol(name, negated) -> str:
    if not name in predicates:
        return None

    translation = predicates[name]
    if '(' in translation:
        return re.sub(r'\(([A-Za-z ]*)\|([A-Za-z ]*)\)', r'\2' if negated else r'\1', translation)

    if not negated:
        return translation

    for pattern, negation in negations.items():
        if pattern in translation:
            return translation.replace(pattern, negation, 1)

def translate_predicate(node: TreeNode, negated: bool = False) -> str:
    value = node.value.removeprefix('p__').removeprefix('d__')
    translation = translate_prediacte_symbol(value, negated)

    if not translation:
        translation = "NOT " if negated else "" + f"{value}({','.join(['{}'] * len(node.children))})"

    return translation.format(*[translate_term(c) for c in node.children])

def get_variables(nodes: list[TreeNode]) -> str:
    if len(nodes) == 1:
        return nodes[0].value

    return f"{', '.join([n.value for n in nodes[:-1]])} and {nodes[-1].value}"

def translate_quantifier(node: TreeNode) -> str:
    vars = get_variables(node.children[:-1])
    right = translate_node(node.children[-1])

    match node.value:
        case '!':
            return f"{right} for every {vars}"
        case '?':
            return f"there is at least one {vars} for which {right}"
        case _:
            return ""

def translate_unary(node: TreeNode) -> str:
    if node.value == '~':
        return translate_predicate(node.children[0], True)
    return ""

def translate_binary_assoc(node: TreeNode) -> str:
    children = [translate_node(c) for c in node.children]

    match node.value:
        case '&':
            return " and ".join(children)
        case '|':
            return " or ".join(children)
        case _:
            return ""

def translate_binary(node: TreeNode) -> str:
    left = translate_node(node.children[0])
    right = translate_node(node.children[1])

    match node.value:
        case '=>':
            return f"if {left}, then {right}"
        case '<=>':
            return f"{right} if and only if {left}"
        case '<~>':
            return f"either {left} or {right}"
        case _:
            return ""

def translate_node(node: TreeNode) -> str:
    match node.type:
        case TreeNodeType.BINARY:
            return translate_binary(node)
        case TreeNodeType.BINARY_ASSOC:
            return translate_binary_assoc(node)
        case TreeNodeType.UNARY:
            return translate_unary(node)
        case TreeNodeType.QUANTIFIER:
            return translate_quantifier(node)
        case TreeNodeType.PREDICATE:
            return translate_predicate(node)

def translate_ast(ast: TreeNode) -> str:
    translation = translate_node(ast)
    return translation[:1].upper() + translation[1:] + '.'

def translate_axiom(axiom: str) -> str:
    ast = parse_axiom(axiom)
    ast = optimise_ast(ast)
    return translate_ast(ast)

def translate_ontology(ontology: dict[str,str]) -> dict[str,str]:
    return {name: translate_axiom(axiom) for name, axiom in ontology.items()}

if __name__ == "__main__":
    from tstp_util import read_tstp
    import time

    print("Translation Adimen-SUMO (./adimen.sumo.tstp)")
    start = time.perf_counter()

    ontology = read_tstp("./adimen.sumo.tstp")

    translation = translate_ontology(ontology)

    with open("./translations.json", 'w') as file:
        json.dump(translation, file, indent=2)
        
    end = time.perf_counter()
    print(f"Done in {end - start:0.2f} seconds")
    print("Translated axioms in './translations.json'")
