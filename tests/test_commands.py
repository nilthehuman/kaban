"""Test basic kaban commands and business logic."""


from pathlib import Path

import pytest

from kaban.control import KabanControl
from kaban.defaults import Paths


def test_always_pass():
    assert True


@pytest.fixture(scope="session", autouse=True)
def kaban_control(tmp_path_factory):
    kc = KabanControl()
    # mock default paths for the sake of an isolated test environment
    tmp_path = tmp_path_factory.mktemp(".kaban")
    kc.paths = Paths( tmp_path
                    , tmp_path / 'my_kaban_tasks.toml'
                    , tmp_path / 'my_kaban_tasks.yaml'
                    , tmp_path / 'config.toml'
                    )
    yield kc


def test_init(kaban_control):
    kaban_control.init()
    assert kaban_control._init_done()
    assert Path(kaban_control.paths.toml_file_path).exists()
    assert Path(kaban_control.paths.config_file_path).exists()


@pytest.fixture(scope="session")
def setup_init(kaban_control):
    kaban_control.init()


def test_user(kaban_control, setup_init):
    kaban_control.args.object = "mreynolds"
    kaban_control.user()
    assert True # ?


def test_add(setup_init):
    kaban_control = KabanControl()
    kaban_control.args.object = "Feed dragon"
    kaban_control.add()
    assert True # ?


# TODO: more tests to come...
