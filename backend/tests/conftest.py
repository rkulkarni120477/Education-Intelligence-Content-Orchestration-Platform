"""
Pytest configuration for workforce alignment workflow tests.

Sets up Python path and pytest fixtures.
"""

import sys
from pathlib import Path

# Add backend directory to Python path so imports work
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))
