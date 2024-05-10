from fof_parser import TreeNode, TreeNodeType

def solve_negated_unary(node: TreeNode) -> TreeNode:
    return node.children[0]

def solve_negated_binary(node: TreeNode) -> TreeNode:
    left = node.children.pop(0)
    right = node.children.pop(0)

    match node.value:
        case '&':
            node.value = '|'
            node.append(TreeNode(TreeNodeType.UNARY, '~').append(left))
            node.append(TreeNode(TreeNodeType.UNARY, '~').append(right))
        case '|':
            node.value = '&'
            node.append(TreeNode(TreeNodeType.UNARY, '~').append(left))
            node.append(TreeNode(TreeNodeType.UNARY, '~').append(right))
        case '=>':
            node.value = '&'
            node.append(left)
            node.append(TreeNode(TreeNodeType.UNARY, '~').append(right))
        case '<=>':
            node.value = '<~>'
            node.append(left)
            node.append(right)

    return node

def solve_negated_quantifier(node: TreeNode) -> TreeNode:
    node.value = '!' if node.value == '?' else '?'
    node.append(TreeNode(TreeNodeType.UNARY, '~').append(node.children.pop()))
    return node

def solve_negation(node: TreeNode) -> TreeNode:
    child = node.children[0]
    match child.type:
        case TreeNodeType.BINARY:     node = solve_negated_binary(child)
        case TreeNodeType.UNARY:      node = solve_negated_unary(child)
        case TreeNodeType.QUANTIFIER: node = solve_negated_quantifier(child)
    
    return node

def optimise_ast(node: TreeNode) -> TreeNode:
    if node.type == TreeNodeType.UNARY and node.value == '~':
        node = solve_negation(node)

    for i in range(len(node.children)):
        node.children[i] = optimise_ast(node.children[i])
    
    return node

if __name__ == "__main__":
    ast = TreeNode(TreeNodeType.UNARY, '~')
    ast.append(TreeNode(TreeNodeType.QUANTIFIER, '!')
                .append(TreeNode(TreeNodeType.VARIABLE, 'X'))
                .append(TreeNode(TreeNodeType.PREDICATE, 'p')
                        .append(TreeNode(TreeNodeType.VARIABLE, 'X'))))
    
    optimise_ast(ast).print()

