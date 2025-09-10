import os
import stat
from unittest import mock

from splitter_app.services import auth


def test_token_saved_with_strict_permissions(tmp_path, monkeypatch):
    token_path = tmp_path / "token.json"
    monkeypatch.setenv(auth.ENV_CREDENTIALS_VAR, str(token_path))

    dummy_creds = mock.Mock()
    dummy_creds.valid = True
    dummy_creds.to_json.return_value = "{}"

    def fake_from_file(path, scopes):
        raise FileNotFoundError

    def fake_flow_from_client_secrets_file(client_secrets_file, scopes):
        flow = mock.Mock()
        flow.run_local_server.return_value = dummy_creds
        return flow

    monkeypatch.setattr(auth.Credentials, "from_authorized_user_file", staticmethod(fake_from_file))
    monkeypatch.setattr(auth.InstalledAppFlow, "from_client_secrets_file", staticmethod(fake_flow_from_client_secrets_file))

    path = auth.ensure_credentials()
    assert os.path.exists(path)
    mode = stat.S_IMODE(os.stat(path).st_mode)
    assert mode == 0o600
