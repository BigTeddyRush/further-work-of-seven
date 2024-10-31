cd src/
call python -m unittest -v tests.test_parser -b
call python -m unittest -v tests.test_optimiser -b
call python -m unittest -v tests.test_similarity -b
cd ..