"""Shared test fixtures for Yomeru backend tests."""

from __future__ import annotations

import pytest


@pytest.fixture
def sample_japanese_text() -> str:
    """Sample Japanese text for testing."""
    return "私は学生です"


@pytest.fixture
def sample_empty_text() -> str:
    """Empty text for testing."""
    return ""


@pytest.fixture
def sample_whitespace_text() -> str:
    """Whitespace-only text for testing."""
    return "   "
