"""
AI Agency Test Suite
===================
Tests for all phases using pytest.

Run all tests:
    pytest tests/ -v

Run specific phase:
    pytest tests/unit/test_agents.py -v
"""

import pytest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))