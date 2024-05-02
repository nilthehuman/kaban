"""Test basic kaban commands and business logic."""


from pathlib import Path

from pytest import fixture

from kaban.control import KabanControl
from kaban.defaults import *


def test_always_pass():
    assert True


@fixture(scope="session")
def mock_kaban_dir(tmp_path_factory):
    KABAN_DIR = tmp_path_factory


def test_init(mock_kaban_dir):
    kc = KabanControl()
    kc.init()
    assert kc._init_done()
    assert Path(KABAN_DIR / TOML_FILE_PATH).exists()


# TODO: more tests to come...
