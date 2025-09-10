import pytest


def test_request_access_link_opened(monkeypatch):
    import splitter_app.main as main_module

    # Stub out application and UI setup
    class DummyApp:
        def __init__(self, *args, **kwargs):
            pass

        def exec(self):
            return 0

    monkeypatch.setattr(main_module, "QApplication", lambda *a, **k: DummyApp())
    monkeypatch.setattr(main_module, "apply_dark_fusion", lambda app: None)

    # Simulate credential and download behavior
    monkeypatch.setattr(main_module, "ensure_credentials", lambda: "token")

    def fake_download():
        raise FileNotFoundError("not shared")

    monkeypatch.setattr(main_module, "download_csv", fake_download)

    # Avoid running real UI components
    class DummyWin:
        def show(self):
            pass

    monkeypatch.setattr(main_module, "MainWindow", lambda *a, **k: DummyWin())

    class DummyController:
        def __init__(self, *a, **k):
            pass

        def initialize(self):
            pass

    monkeypatch.setattr(main_module, "SplitterController", DummyController)

    # Skip uploads and file existence checks
    monkeypatch.setattr(main_module, "upload_csv", lambda: None)
    monkeypatch.setattr(main_module.os.path, "exists", lambda p: False)

    # Capture URL opening
    opened = {}

    def fake_open(url):
        opened["url"] = url.toString()

    monkeypatch.setattr(main_module.QDesktopServices, "openUrl", fake_open)

    # Auto-accept request prompt
    monkeypatch.setattr(
        main_module.QMessageBox,
        "question",
        lambda *a, **k: main_module.QMessageBox.Yes,
    )

    # Suppress other message boxes
    monkeypatch.setattr(main_module.QMessageBox, "warning", lambda *a, **k: None)
    monkeypatch.setattr(main_module.QMessageBox, "information", lambda *a, **k: None)

    with pytest.raises(SystemExit):
        main_module.main()

    assert opened["url"].startswith("https://drive.google.com/file/d/")
