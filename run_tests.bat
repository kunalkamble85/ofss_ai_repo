set PYTHONPATH=%PYTHONPATH%;./src;./tests;
python -m unittest discover -s ./tests -p "test_*.py"