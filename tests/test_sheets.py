import splitter_app.services.sheets as sheets_module


def test_load_transactions(monkeypatch):
    fake_id = "SHEETID"
    fake_range = "Sheet1!A:H"
    fake_cred = "CREDPATH"
    sample = [
        ["A001", "Lunch", "Adrian", "2024-01-01", "general", "Food & Drinks", "0.5", "10.0"],
        ["B002", "Taxi", "Vic", "2024-01-02", "general", "Travel", "1.0", "20.0"],
    ]
    monkeypatch.setattr(sheets_module.config, "SHEETS_SPREADSHEET_ID", fake_id)
    monkeypatch.setattr(sheets_module.config, "SHEETS_RANGE", fake_range)
    monkeypatch.setattr(sheets_module.config, "CREDENTIALS_FILE", fake_cred)

    called = {}

    def fake_read(sheet_id, rng, cred):
        called["args"] = (sheet_id, rng, cred)
        return sample

    monkeypatch.setattr(sheets_module, "_read_sheet", fake_read)
    txns = sheets_module.load_transactions()

    assert called["args"] == (fake_id, fake_range, fake_cred)
    assert [t.serial_number for t in txns] == ["A001", "B002"]
