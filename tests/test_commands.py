"""Test basic kaban commands and business logic."""


import git

from pathlib import Path

import pytest

from kaban.control import KabanControl
from kaban.defaults import Paths


def test_always_pass():
    assert True


@pytest.fixture(scope="session")
def kaban_control(tmp_path_factory):
    kc = KabanControl()
    # mock default paths for the sake of an isolated test environment
    tmp_path = tmp_path_factory.mktemp('.kaban')
    kc.paths = Paths( tmp_path
                    , tmp_path / 'my_kaban_tasks.toml'
                    , tmp_path / 'my_kaban_tasks.yaml'
                    , tmp_path / 'config.toml'
                    )
    yield kc


def test_init(kaban_control, capsys):
    assert not kaban_control._init_done()
    try:
        assert git.Repo(kaban_control.paths.kaban_dir) is None
    except git.exc.InvalidGitRepositoryError:
        pass  # good
    except Exception:
        assert False  # bad
    assert not Path(kaban_control.paths.toml_file_path).exists()
    assert not Path(kaban_control.paths.config_file_path).exists()
    kaban_control.init()
    assert kaban_control._init_done()
    assert git.Repo(kaban_control.paths.kaban_dir) is not None
    assert Path(kaban_control.paths.toml_file_path).exists()
    assert Path(kaban_control.paths.config_file_path).exists()


@pytest.fixture(scope="session")
def setup_init(kaban_control):
    kaban_control.init()


def test_remote(kaban_control, setup_init):
    git_repo = git.Repo(kaban_control.paths.kaban_dir)
    assert git_repo is not None
    assert kaban_control._get_creds() == None
    kaban_control.args.object = "https://github.com"
    kaban_control.remote()
    assert git_repo.config_reader().get_value('remote "origin"', 'url') == "https://github.com"


def test_user(kaban_control, setup_init):
    assert kaban_control._get_creds() is None
    git_repo = git.Repo(kaban_control.paths.kaban_dir)
    assert git_repo is not None
    assert git_repo.config_reader().get_value('remote "origin"', 'url') == "https://github.com"
    kaban_control.args.object = "mreynolds"
    kaban_control.user()
    assert kaban_control._get_creds() == ("mreynolds")
    assert git_repo.config_reader().get_value('remote "origin"', 'url') == "https://mreynolds@github.com"


def test_token(kaban_control, setup_init):
    assert kaban_control._get_creds() == ("mreynolds")
    git_repo = git.Repo(kaban_control.paths.kaban_dir)
    assert git_repo.config_reader().get_value('remote "origin"', 'url') == "https://mreynolds@github.com"
    kaban_control.args.object = "ghp_03K64Firefly"
    kaban_control.token()
    assert kaban_control._get_creds() == ("mreynolds", "ghp_03K64Firefly")
    assert git_repo.config_reader().get_value('remote "origin"', 'url') == "https://mreynolds:ghp_03K64Firefly@github.com"


def test_add(setup_init):
    kaban_control = KabanControl()
    kaban_control.args.object = "Feed dragon"
    kaban_control.add()
    assert True # ?


# TODO: more tests to come...
