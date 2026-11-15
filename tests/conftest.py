import os
import shutil
from pathlib import Path

import pytest

from server.blender import run_job_checked
from server.paths import LIBRARY, NODE, blender_bin

HAS_BLENDER = Path(blender_bin()).exists()
HAS_LIBRARY = (LIBRARY / "skeleton.blend").exists() and (LIBRARY / "animations.blend").exists()
HAS_NODE = shutil.which("node") is not None and (NODE / "node_modules").exists()

needs_blender = pytest.mark.skipif(not (HAS_BLENDER and HAS_LIBRARY),
                                   reason="needs Blender (BLENDER_BIN) and a built library/ (python -m server.build_library)")
needs_node = pytest.mark.skipif(not HAS_NODE, reason="needs node + `npm install --prefix node`")


@pytest.fixture(scope="session")
def fixtures_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("fixtures")


@pytest.fixture(scope="session")
def mannequin(fixtures_dir):
    """A clean mannequin character (.blend) on the standard skeleton, with all clips."""
    out = fixtures_dir / "mannequin.blend"
    run_job_checked("make_mannequin", {"out": str(out)})
    return out


@pytest.fixture()
def workspace(tmp_path, monkeypatch):
    ws = tmp_path / "workspace"
    monkeypatch.setenv("GPG_WORKSPACE", str(ws))
    return ws


@pytest.fixture()
def clean_env(monkeypatch):
    monkeypatch.delenv("GPG_PIN_BLENDER_OVERRIDE", raising=False)
    return os.environ
