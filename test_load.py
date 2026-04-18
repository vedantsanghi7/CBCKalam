import sys
import os
sys.path.append(os.path.abspath('api'))
from server import _load_all_schemes
schemes = _load_all_schemes()
print(f"Loaded {len(schemes)}")
