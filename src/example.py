from translator import translate_axiom
from seven import Encoder, cosine_sim

encoder = Encoder()

goal = {
    'axiom':  "![A]: (p__d__subclass(A, c__Canine) => ~(p__d__subclass(A, c__Feline)))"
}
goal['vector'] = encoder.encode_axiom(goal['axiom'])

axioms = [
    "p__d__subclass(c__Canine,c__Carnivore)",
    "p__d__subclass(c__Rodent,c__Mammal)",
    "(![X,Y,Z]: ((((p__d__subclass(X,Y))&(p__d__subclass(Y,Z))))=>(p__d__subclass(X,Z))))",
    "p__subrelation(c__immediateInstance,c__instance)",
]

print("Goal")
print(" - Sentence:", translate_axiom(goal['axiom']))
print(" - Vector:  ", goal['vector'].tolist()[:5])
print(" - Distance:", cosine_sim(goal['vector'], goal['vector']))

for i, axiom in enumerate(axioms):
    vector = encoder.encode_axiom(axiom)

    print("Axiom", i)
    print(" - Sentence:", translate_axiom(axiom))
    print(" - Vector:  ", vector.tolist()[:5])
    print(" - Size:    ", vector.size())
    print(" - Distance:", cosine_sim(goal['vector'], vector))