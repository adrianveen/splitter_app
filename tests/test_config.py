import os
import importlib
from pathlib import Path

import splitter_app.config as config


def test_credentials_file_defaults_to_config_dir(tmp_path, monkeypatch):
    """When no env var is set, credentials should live in ~/.config/splitter_app."""
    orig_home = os.environ["HOME"]
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("GOOGLE_TOKEN_PATH", raising=False)
    importlib.reload(config)
    expected = tmp_path / ".config" / "splitter_app" / "token.json"
    assert config.CREDENTIALS_FILE == str(expected)
    # restore module to original state
    monkeypatch.setenv("HOME", orig_home)
    importlib.reload(config)


def test_credentials_file_uses_env_path_even_if_missing(tmp_path, monkeypatch):
    """Env var should override default even if the file doesn't exist yet."""
    env_path = tmp_path / "custom" / "token.json"
    monkeypatch.setenv("GOOGLE_TOKEN_PATH", str(env_path))
    importlib.reload(config)
    assert config.CREDENTIALS_FILE == str(env_path)
    # restore module to original state
    monkeypatch.delenv("GOOGLE_TOKEN_PATH", raising=False)
    importlib.reload(config)
