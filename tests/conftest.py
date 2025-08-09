# Ensure project root is on sys.path for `import kezan.*` during tests
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Avoid collecting nested legacy/duplicate test suites that conflict by basename
collect_ignore_glob = [
    "unit_tests/*",
    "integration_tests/*",
    "security_tests/*",
]
