import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture(autouse=True)
def mock_google_sheets():
    """Intercept all Google Sheets calls so tests never need credentials."""
    mock_ws = MagicMock()
    mock_ws.get_all_records.return_value = []
    mock_spreadsheet = MagicMock()
    mock_spreadsheet.worksheet.return_value = mock_ws
    mock_spreadsheet.get_worksheet_by_id.return_value = mock_ws
    mock_client = MagicMock()
    mock_client.open_by_key.return_value = mock_spreadsheet

    with (
        patch(
            "oauth2client.service_account.ServiceAccountCredentials.from_json_keyfile_name",
            return_value=MagicMock(),
        ),
        patch(
            "oauth2client.service_account.ServiceAccountCredentials.from_json_keyfile_dict",
            return_value=MagicMock(),
        ),
        patch("gspread.authorize", return_value=mock_client),
    ):
        yield
