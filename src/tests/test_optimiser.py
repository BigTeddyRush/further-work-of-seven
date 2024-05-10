import unittest

from fof_parser import TreeNodeType, TreeNode
from optimiser import optimise_ast
from tests.test_parser import compare_trees

class TestNegationSolver(unittest.TestCase):
    def test_and(self):
        """ Test if a negated '&' is solved correctly. """
        ast = TreeNode(TreeNodeType.UNARY, '~')
        ast.append(TreeNode(TreeNodeType.BINARY, '&')
                   .append(TreeNode(TreeNodeType.PREDICATE, 'p'))
                   .append(TreeNode(TreeNodeType.PREDICATE, 'q')))

        solved = TreeNode(TreeNodeType.BINARY, '|')
        solved.append(TreeNode(TreeNodeType.UNARY, '~')
                      .append(TreeNode(TreeNodeType.PREDICATE, 'p')))
        solved.append(TreeNode(TreeNodeType.UNARY, '~')
                      .append(TreeNode(TreeNodeType.PREDICATE, 'q')))

        self.assertTrue(compare_trees(optimise_ast(ast), solved))

    def test_or(self):
        """ Test if a negated '|' is solved correctly. """
        ast = TreeNode(TreeNodeType.UNARY, '~')
        ast.append(TreeNode(TreeNodeType.BINARY, '|')
                   .append(TreeNode(TreeNodeType.PREDICATE, 'p'))
                   .append(TreeNode(TreeNodeType.PREDICATE, 'q')))

        solved = TreeNode(TreeNodeType.BINARY, '&')
        solved.append(TreeNode(TreeNodeType.UNARY, '~')
                      .append(TreeNode(TreeNodeType.PREDICATE, 'p')))
        solved.append(TreeNode(TreeNodeType.UNARY, '~')
                      .append(TreeNode(TreeNodeType.PREDICATE, 'q')))

        self.assertTrue(compare_trees(optimise_ast(ast), solved))

    def test_implies(self):
        """ Test if a negated '=>' is solved correctly. """
        ast = TreeNode(TreeNodeType.UNARY, '~')
        ast.append(TreeNode(TreeNodeType.BINARY, '=>')
                   .append(TreeNode(TreeNodeType.PREDICATE, 'p'))
                   .append(TreeNode(TreeNodeType.PREDICATE, 'q')))
        
        solved = TreeNode(TreeNodeType.BINARY, '&')
        solved.append(TreeNode(TreeNodeType.PREDICATE, 'p'))
        solved.append(TreeNode(TreeNodeType.UNARY, '~')
                      .append(TreeNode(TreeNodeType.PREDICATE, 'q')))

        self.assertTrue(compare_trees(optimise_ast(ast), solved))

    def test_if(self):
        """ Test if a negated '<=>' is solved correctly. """
        ast = TreeNode(TreeNodeType.UNARY, '~')
        ast.append(TreeNode(TreeNodeType.BINARY, '<=>')
                   .append(TreeNode(TreeNodeType.PREDICATE, 'p'))
                   .append(TreeNode(TreeNodeType.PREDICATE, 'q')))

        solved = TreeNode(TreeNodeType.BINARY, '<~>')
        solved.append(TreeNode(TreeNodeType.PREDICATE, 'p'))
        solved.append(TreeNode(TreeNodeType.PREDICATE, 'q'))
        
        self.assertTrue(compare_trees(optimise_ast(ast), solved))

    def test_forall(self):
        """ Test if a negated '![]:' is solved correctly. """
        ast = TreeNode(TreeNodeType.UNARY, '~')
        ast.append(TreeNode(TreeNodeType.QUANTIFIER, '!')
                   .append(TreeNode(TreeNodeType.VARIABLE, 'X'))
                   .append(TreeNode(TreeNodeType.PREDICATE, 'p')
                           .append(TreeNode(TreeNodeType.VARIABLE, 'X'))))

        solved = TreeNode(TreeNodeType.QUANTIFIER, '?')
        solved.append(TreeNode(TreeNodeType.VARIABLE, 'X'))
        solved.append(TreeNode(TreeNodeType.UNARY, '~')
                      .append(TreeNode(TreeNodeType.PREDICATE, 'p')
                              .append(TreeNode(TreeNodeType.VARIABLE, 'X'))))
        
        self.assertTrue(compare_trees(optimise_ast(ast), solved))

    def test_exists(self):
        """ Test if a negated '![]:' is solved correctly. """
        ast = TreeNode(TreeNodeType.UNARY, '~')
        ast.append(TreeNode(TreeNodeType.QUANTIFIER, '?')
                   .append(TreeNode(TreeNodeType.VARIABLE, 'X'))
                   .append(TreeNode(TreeNodeType.PREDICATE, 'p')
                           .append(TreeNode(TreeNodeType.VARIABLE, 'X'))))

        solved = TreeNode(TreeNodeType.QUANTIFIER, '!')
        solved.append(TreeNode(TreeNodeType.VARIABLE, 'X'))
        solved.append(TreeNode(TreeNodeType.UNARY, '~')
                      .append(TreeNode(TreeNodeType.PREDICATE, 'p')
                              .append(TreeNode(TreeNodeType.VARIABLE, 'X'))))
        
        self.assertTrue(compare_trees(optimise_ast(ast), solved))

    def test_negations(self):
        """ Test if multiple negations are solved correctly. """
        ast0 = TreeNode(TreeNodeType.UNARY, '~')
        ast0.append(TreeNode(TreeNodeType.UNARY, '~')
                    .append(TreeNode(TreeNodeType.PREDICATE, 'p')))

        ast1 = TreeNode(TreeNodeType.UNARY, '~')
        ast1.append(TreeNode(TreeNodeType.UNARY, '~')
                    .append(TreeNode(TreeNodeType.UNARY, '~')
                            .append(TreeNode(TreeNodeType.PREDICATE, 'p'))))

        solved0 = TreeNode(TreeNodeType.PREDICATE, 'p')

        solved1 = TreeNode(TreeNodeType.UNARY, '~').append(TreeNode(TreeNodeType.PREDICATE, 'p'))

        self.assertTrue(compare_trees(optimise_ast(ast0), solved0))
        self.assertTrue(compare_trees(optimise_ast(ast1), solved1))

    def test_multiple(self):
        """ Test if negations are solved correctly down to predicates. """
        ast = TreeNode(TreeNodeType.UNARY, '~')
        ast.append(TreeNode(TreeNodeType.BINARY, '|')
                   .append(TreeNode(TreeNodeType.BINARY, '&')
                           .append(TreeNode(TreeNodeType.PREDICATE, 'a'))
                           .append(TreeNode(TreeNodeType.PREDICATE, 'b')))
                   .append(TreeNode(TreeNodeType.BINARY, '=>')
                           .append(TreeNode(TreeNodeType.PREDICATE, 'c'))
                           .append(TreeNode(TreeNodeType.PREDICATE, 'd'))))

        solved = TreeNode(TreeNodeType.BINARY, '&')
        solved.append(TreeNode(TreeNodeType.BINARY, '|')
                      .append(TreeNode(TreeNodeType.UNARY, '~').append(TreeNode(TreeNodeType.PREDICATE, 'a')))
                      .append(TreeNode(TreeNodeType.UNARY, '~').append(TreeNode(TreeNodeType.PREDICATE, 'b'))))
        solved.append(TreeNode(TreeNodeType.BINARY, '&')
                      .append(TreeNode(TreeNodeType.PREDICATE, 'c'))
                      .append(TreeNode(TreeNodeType.UNARY, '~').append(TreeNode(TreeNodeType.PREDICATE, 'd'))))

        self.assertTrue(compare_trees(optimise_ast(ast), solved))


if __name__ == '__main__':
    unittest.main()