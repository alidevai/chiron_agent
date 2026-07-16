"""Test altyapisi: her test icin izole gecici platform koku kurar."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.paths import Paths  # noqa: E402
from core.policy import PolicyEngine  # noqa: E402


@pytest.fixture
def platform(tmp_path: Path) -> Paths:
    """Gercek politika dosyalarini gecici koke kopyalar ve muhurler."""
    paths = Paths(tmp_path)
    paths.ensure()
    # gercek politikalari kopyala
    for f in (ROOT / "policies").glob("*.yaml"):
        shutil.copy(f, paths.policies / f.name)
    PolicyEngine(paths).seal()
    return paths
