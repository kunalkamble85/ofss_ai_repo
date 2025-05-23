set PYTHONPATH=%PYTHONPATH%;./tests;./src/utils;
python -m unittest discover -s ./tests -p "test_oci_*.py"