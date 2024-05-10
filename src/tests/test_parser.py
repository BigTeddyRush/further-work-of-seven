import unittest

from fof_parser import TreeNodeType, TreeNode, parse_axiom

def compare_trees(left: TreeNode, right: TreeNode) -> bool:
    if left.type != right.type or left.value != right.value:
        return False

    if len(left.children) != len(right.children):
        return False

    for i in range(len(left.children)):
        if not compare_trees(left.children[i], right.children[i]):
            return False

    return True


class TestParser(unittest.TestCase):
    def test_assoc(self):
        """ Test if multiple associative operators ('&' and '|') used in a row are parsed correctly. """
        axiom0 = "(a() & b() & c())"
        axiom1 = "(a() | b() | c())"
        axiom2 = "(a() & b() | c())"

        ast0 = TreeNode(TreeNodeType.BINARY_ASSOC, '&')
        ast0.append(TreeNode(TreeNodeType.PREDICATE, 'a'))
        ast0.append(TreeNode(TreeNodeType.PREDICATE, 'b'))
        ast0.append(TreeNode(TreeNodeType.PREDICATE, 'c'))

        ast1 = TreeNode(TreeNodeType.BINARY_ASSOC, '|')
        ast1.append(TreeNode(TreeNodeType.PREDICATE, 'a'))
        ast1.append(TreeNode(TreeNodeType.PREDICATE, 'b'))
        ast1.append(TreeNode(TreeNodeType.PREDICATE, 'c'))

        self.assertTrue(compare_trees(parse_axiom(axiom0), ast0))
        self.assertTrue(compare_trees(parse_axiom(axiom1), ast1))

        with self.assertRaises(SyntaxError):
            parse_axiom(axiom2)

    def test_nonassoc(self):
        """ Test if multiple non-associative operators ('=>' and '<=>') used in a row throw an error. """
        axiom0 = "(a() => b() => c())"
        axiom1 = "(a() <=> b() <=> c())"

        with self.assertRaises(SyntaxError):
            parse_axiom(axiom0)

        with self.assertRaises(SyntaxError):
            parse_axiom(axiom1)

    def test_nonassoc_parentheses(self):
        """ Test if multiple non-associative operators ('=>' and '<=>') used with parentheses are parsed correctly. """
        axiom0 = "((a() => b()) => c())"
        axiom1 = "(a() <=> (b() <=> c()))"

        ast0 = TreeNode(TreeNodeType.BINARY, '=>')
        ast0.append(TreeNode(TreeNodeType.BINARY, '=>')
                    .append(TreeNode(TreeNodeType.PREDICATE, 'a'))
                    .append(TreeNode(TreeNodeType.PREDICATE, 'b')))
        ast0.append(TreeNode(TreeNodeType.PREDICATE, 'c'))

        ast1 = TreeNode(TreeNodeType.BINARY, '<=>')
        ast1.append(TreeNode(TreeNodeType.PREDICATE, 'a'))
        ast1.append(TreeNode(TreeNodeType.BINARY, '<=>')
                    .append(TreeNode(TreeNodeType.PREDICATE, 'b'))
                    .append(TreeNode(TreeNodeType.PREDICATE, 'c')))

        self.assertTrue(compare_trees(parse_axiom(axiom0), ast0))
        self.assertTrue(compare_trees(parse_axiom(axiom1), ast1))

    def test_predicate_args(self):
        """ Test if an error is thrown if anything other than a term are used as arguments for predicates. """
        axiom = "(p(A, A & B))"

        with self.assertRaises(SyntaxError):
            parse_axiom(axiom)

    def test_predicate_args_infix(self):
        """ Test if an error is thrown if anything other than variables are used as arguments for infix predicates. """
        axiom0 = "(A = A & B)"
        axiom1 = "(A & B = A)"

        with self.assertRaises(SyntaxError):
            parse_axiom(axiom0)

        with self.assertRaises(SyntaxError):
            parse_axiom(axiom1)

    def test_parentheses(self):
        """ Test if parentheses are parsed correctly. """
        axiom0 = "((((((((A = B))))))))"
        axiom1 = "(((A = B))))"

        ast = TreeNode(TreeNodeType.PREDICATE, '=')
        ast.append(TreeNode(TreeNodeType.VARIABLE, 'A'))
        ast.append(TreeNode(TreeNodeType.VARIABLE, 'B'))

        self.assertTrue(compare_trees(parse_axiom(axiom0), ast))

        with self.assertRaises(SyntaxError):
            parse_axiom(axiom1)

    def test_negation(self):
        """ Test if negation are parsed correctly. """
        axiom0 = "~(A = B)"
        axiom1 = "~~(A = B)"

        ast0 = TreeNode(TreeNodeType.UNARY, '~')
        ast0.append(TreeNode(TreeNodeType.PREDICATE, '=')
                   .append(TreeNode(TreeNodeType.VARIABLE, 'A'))
                   .append(TreeNode(TreeNodeType.VARIABLE, 'B')))

        ast1 = TreeNode(TreeNodeType.UNARY, '~')
        ast1.append(TreeNode(TreeNodeType.UNARY, '~')
            .append(TreeNode(TreeNodeType.PREDICATE, '=')
                   .append(TreeNode(TreeNodeType.VARIABLE, 'A'))
                   .append(TreeNode(TreeNodeType.VARIABLE, 'B'))))

        self.assertTrue(compare_trees(parse_axiom(axiom0), ast0))
        self.assertTrue(compare_trees(parse_axiom(axiom1), ast1))

    def test_quantified(self):
        """ Test if quantifiers are parsed correctly. """
        axiom = "(![X,Y]: ((X=Y) <=> (Y=X)))"

        ast = TreeNode(TreeNodeType.QUANTIFIER, '!')
        ast.append(TreeNode(TreeNodeType.VARIABLE, 'X'))
        ast.append(TreeNode(TreeNodeType.VARIABLE, 'Y'))

        ast.append(TreeNode(TreeNodeType.BINARY, '<=>')
                    .append(TreeNode(TreeNodeType.PREDICATE, '=')
                            .append(TreeNode(TreeNodeType.VARIABLE, 'X'))
                            .append(TreeNode(TreeNodeType.VARIABLE, 'Y')))
                    .append(TreeNode(TreeNodeType.PREDICATE, '=')
                            .append(TreeNode(TreeNodeType.VARIABLE, 'Y'))
                            .append(TreeNode(TreeNodeType.VARIABLE, 'X'))))
        
        self.assertTrue(compare_trees(parse_axiom(axiom), ast))

    def test_incomplete(self):
        """ Test if an error is thrown if the formula is incomplete. """
        axiom0 = "(X=Y) <=>"
        axiom1 = "(X=Y) &"
        axiom2 = "(X=Y"
        axiom3 = "X="
        axiom4 = "![X,Y]:"
        
        with self.assertRaises(SyntaxError):
            parse_axiom(axiom0)
        with self.assertRaises(SyntaxError):
            parse_axiom(axiom1)
        with self.assertRaises(SyntaxError):
            parse_axiom(axiom2)
        with self.assertRaises(SyntaxError):
            parse_axiom(axiom3)
        with self.assertRaises(SyntaxError):
            parse_axiom(axiom4)


if __name__ == '__main__':
    unittest.main()