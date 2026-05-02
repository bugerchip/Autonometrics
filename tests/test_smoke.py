"""Smoke tests: verify the package imports and exposes its public API."""

import autonometrics
from autonometrics import Autonometer, AutonomyProfile


def test_package_imports() -> None:
    assert autonometrics.__version__
    assert isinstance(autonometrics.__version__, str)


def test_version_is_pep440_alpha() -> None:
    assert autonometrics.__version__ == "0.5.1a0"


def test_public_api_exported() -> None:
    assert Autonometer is autonometrics.Autonometer
    assert AutonomyProfile is autonometrics.AutonomyProfile
    assert set(autonometrics.__all__) >= {"Autonometer", "AutonomyProfile", "__version__"}
