# About This Repository

This repository builds upon the work of Prof. Claudia Schon and the SeVEn project, which can be found at [https://gitlab.rlp.net](https://gitlab.rlp.net).

The base repository by Prof. Schon is located on the main page of the GitLab project. This repository extends that work with several modifications, organized across different branches.

Please note that legacy branches have been preserved with the prefix `old_` to indicate earlier development stages or experimental directions.

Feel free to explore the various branches for specific features, experiments, or configurations.


---------------

# SeVEn (Sentence-Based Vector Encoding)

## Translating Axioms

To translate the Axioms provided in './adimen.sumo.tstp' run the translator script with:
    > python ./src/translator.py

The resulting translation of Adimen-SUMO is placed in './translations.json'.
The mapping of predicate and function symbols used in the translation is provided in './src/symbols.py'.

## Encoding Axioms

To translate the Axioms provided in './adimen.sumo.tstp' run:
    > python ./src/seven.py

The encoded axioms are placed in './axioms.pt'.

## Example Problem

A small example to illustrate how SeVEn works can be seen by running: 
    > python ./src/example.py

## Evaluation

To evalute SeVEn as discussed in the paper, execute:
    > python ./src/translator.py [--select=<?>]

The results of this evaluation are placed in the './results/' directory. Additionally 

When evaluating for the first time we need to select some problems on which we can test the selection strategy. To select these candidates use the optional argument '--select=?' and specify the number of problems when running the script. 
This may take a while so only do this once.

To run this script the [E Theorem Prover](http://wwwlehre.dhbw-stuttgart.de/~sschulz/E/E.html) needs to be installed.
