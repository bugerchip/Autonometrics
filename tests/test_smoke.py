"""Smoke tests: verify the package imports and exposes basic metadata."""

import autonometrics


def test_package_imports() -> None:
    assert autonometrics.__version__
    assert isinstance(autonometrics.__version__, str)


def test_version_is_pep440_alpha() -> None:
    assert autonometrics.__version__ == "0.1.0a0"
