"""Pytest fixtures for `strategies/`."""
from pathlib import Path

import pytest


@pytest.fixture(scope="session", autouse=True)
def load_plugins() -> None:
    """Load pip installed plugin strategies."""
    from oteapi.plugins.factories import load_strategies

    load_strategies(test_for_uniqueness=False)


@pytest.fixture(scope="session")
def repo_dir() -> Path:
    """Absolute path to the repository directory."""
    return Path(__file__).parent.parent.resolve()


@pytest.fixture
def tmpdir() -> Path:
    """Create a temporary directory that lasts the runtime of the test."""
    from tempfile import TemporaryDirectory

    res = TemporaryDirectory()  # pylint: disable=consider-using-with

    yield Path(res.name)
    res.cleanup()
