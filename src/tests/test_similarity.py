import unittest

from seven import Encoder, cosine_sim

class TestSimilarity(unittest.TestCase):
    def setUp(self):
        self.encoder = Encoder()

    def test_similar(self):
        """ Test if the distance between similar axioms is close to '1'. """
        axiom = self.encoder.encode_axiom("p__d__subclass(c__TimeInterval,c__TimePosition)")
        similar = self.encoder.encode_axiom("p__d__subclass(c__TimePoint,c__TimePosition)")

        self.assertTrue(cosine_sim(axiom, similar) >= 0.8)

        
    def test_different(self):
        """ Test if the distance between different axioms is close to '0'. """
        axiom = self.encoder.encode_axiom("p__d__subclass(c__TimeInterval,c__TimePosition)")
        different = self.encoder.encode_axiom("(![CHILD,PARENT]: ((((p__d__instance(CHILD,c__Organism)) & (p__parent(CHILD,PARENT)) & (p__d__instance(PARENT,c__Man)))) => (p__father(CHILD,PARENT))))")

        self.assertTrue(cosine_sim(axiom, different) <= 0.2)
        
    def test_equal(self):
        """ Test if the distance between equal axioms is '1'. """
        axiom = self.encoder.encode_axiom("p__d__subclass(c__TimeInterval,c__TimePosition)")

        self.assertTrue(cosine_sim(axiom, axiom) == 1)

if __name__ == '__main__':
    unittest.main()