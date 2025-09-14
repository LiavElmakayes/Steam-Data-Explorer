import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from steam_explorer.api.steam_client import SteamClient


def test_get_app_details_batching(steam_client: SteamClient):
    with patch.object(steam_client.session, "get") as mock_get:
        # Mock two batches
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.side_effect = [
            {"570": {"success": True, "data": {"name": "Dota 2"}}},
            {"730": {"success": True, "data": {"name": "CS2"}}},
        ]
        result = steam_client.get_app_details([570, 730], batch_size=1)
        assert "570" in result and "730" in result
        assert mock_get.call_count == 2
