import os
import sys

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
print(f"CURRENT_PATH: {CURRENT_PATH}")
sys.path.append(os.path.abspath(CURRENT_PATH))
