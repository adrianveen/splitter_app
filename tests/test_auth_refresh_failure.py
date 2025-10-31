import os
from unittest import mock

from google.auth.exceptions import RefreshError

from splitter_app.services import auth


def test_refresh_token_failure_fallback_to_oauth(tmp_path, monkeypatch):
    """Test that when refresh token fails, we fall back to full OAuth flow."""
    token_path = tmp_path / "token.json"
    monkeypatch.setenv(auth.ENV_CREDENTIALS_VAR, str(token_path))
    # Create a dummy token file so it exists
    token_path.write_text('{"token": "existing_but_expired"}')

    # Mock credentials that appear expired but have a refresh token
    mock_expired_creds = mock.Mock()
    mock_expired_creds.valid = False
    mock_expired_creds.expired = True
    mock_expired_creds.refresh_token = "some_refresh_token"
    # Make refresh() raise a RefreshError (like invalid_grant)
    mock_expired_creds.refresh.side_effect = RefreshError("invalid_grant: Bad Request")

    # Mock fresh credentials from OAuth flow
    mock_fresh_creds = mock.Mock()
    mock_fresh_creds.valid = True
    mock_fresh_creds.to_json = mock.Mock(return_value='{"token": "fresh_token"}')

    def fake_from_file(path, scopes):
        return mock_expired_creds

    def fake_flow_from_client_secrets_file(client_secrets_file, scopes):
        flow = mock.Mock()
        flow.run_local_server.return_value = mock_fresh_creds
        return flow

    monkeypatch.setattr(
        auth.Credentials,
        "from_authorized_user_file",
        staticmethod(fake_from_file),
    )
    monkeypatch.setattr(
        auth.InstalledAppFlow,
        "from_client_secrets_file",
        staticmethod(fake_flow_from_client_secrets_file),
    )

    # Call ensure_credentials - should not raise an exception
    result_path = auth.ensure_credentials()

    # Verify that refresh was attempted but failed, then OAuth flow was used
    mock_expired_creds.refresh.assert_called_once()
    assert os.path.exists(result_path)

    # Verify the fresh token was saved
    with open(result_path) as f:
        content = f.read()
        assert '"token": "fresh_token"' in content


def test_refresh_token_success_no_oauth_needed(tmp_path, monkeypatch):
    """Test that when refresh succeeds, no new OAuth flow is triggered."""
    token_path = tmp_path / "token.json"
    monkeypatch.setenv(auth.ENV_CREDENTIALS_VAR, str(token_path))
    # Create a dummy token file so it exists
    token_path.write_text('{"token": "existing_but_expired"}')

    # Mock credentials that appear expired but refresh successfully
    mock_creds = mock.Mock()
    mock_creds.valid = False
    mock_creds.expired = True
    mock_creds.refresh_token = "valid_refresh_token"

    def mock_refresh(request):
        # Simulate successful refresh by making credentials valid
        mock_creds.valid = True

    mock_creds.refresh.side_effect = mock_refresh
    mock_creds.to_json = mock.Mock(return_value='{"token": "refreshed_token"}')

    def fake_from_file(path, scopes):
        return mock_creds

    # Mock the OAuth flow but it shouldn't be called
    mock_flow = mock.Mock()

    def fake_flow_from_client_secrets_file(client_secrets_file, scopes):
        return mock_flow

    monkeypatch.setattr(
        auth.Credentials,
        "from_authorized_user_file",
        staticmethod(fake_from_file),
    )
    monkeypatch.setattr(
        auth.InstalledAppFlow,
        "from_client_secrets_file",
        staticmethod(fake_flow_from_client_secrets_file),
    )

    # Call ensure_credentials
    result_path = auth.ensure_credentials()

    # Verify that refresh was called and OAuth flow was NOT used
    mock_creds.refresh.assert_called_once()
    mock_flow.run_local_server.assert_not_called()

    # Verify the refreshed token was saved
    assert os.path.exists(result_path)
    with open(result_path) as f:
        content = f.read()
        assert '"token": "refreshed_token"' in content
