# tests/conftest.py
import os
import sys

# assuming conftest.py lives in <repo_root>/tests
SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, SRC)
