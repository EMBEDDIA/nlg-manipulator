#! /bin/bash
python -m cProfile -o run1.cprof src/benchmark.py; pyprof2calltree -k -i run1.cprof
