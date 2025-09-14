from __future__ import annotations
from typing import Any, Dict, Iterable, Mapping, List
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..logging_utils import get_logger


class SteamClient:
    def __init__(self, api_key: str, timeout_seconds: int = 20, requests_per_second: float = 2.0) -> None:
        self.api_key = api_key
        self.base_url = "https://api.steampowered.com"
        self.timeout_seconds = timeout_seconds
        self.logger = get_logger(self.__class__.__name__)
        self.session = self._build_session()
        self.min_interval = 1.0 / max(0.1, requests_per_second)
        self._last_request_ts = 0.0

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        retry = Retry(
            total=5,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _respect_rate_limit(self) -> None:
        now = time.time()
        elapsed = now - self._last_request_ts
        if elapsed < self.min_interval:
            sleep_for = self.min_interval - elapsed
            time.sleep(sleep_for)
        self._last_request_ts = time.time()

    def _get(self, path: str, params: Mapping[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/{path}"
        self._respect_rate_limit()
        self.logger.debug(f"GET {url} params={dict(params)}")
        response = self.session.get(url, params=params, timeout=self.timeout_seconds)
        self.logger.debug(f"Response status={response.status_code}")
        response.raise_for_status()
        return response.json()

    def get_owned_games(self, steamid: str, include_appinfo: bool = True, include_played_free_games: bool = True) -> Dict[str, Any]:
        params = {
            "key": self.api_key,
            "steamid": steamid,
            "include_appinfo": 1 if include_appinfo else 0,
            "include_played_free_games": 1 if include_played_free_games else 0,
            "format": "json",
        }
        self.logger.info(f"Fetching owned games for steamid={steamid}")
        return self._get("IPlayerService/GetOwnedGames/v1/", params)

    def get_global_achievements_for_app(self, appid: int) -> Dict[str, Any]:
        params = {"gameid": appid, "format": "json"}
        url = f"{self.base_url}/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v2/"
        self._respect_rate_limit()
        self.logger.info(f"Fetching global achievements for appid={appid}")
        response = self.session.get(url, params=params, timeout=self.timeout_seconds)
        self.logger.debug(f"Response status={response.status_code}")
        response.raise_for_status()
        return response.json()

    def get_app_details(self, appids: Iterable[int], batch_size: int = 50) -> Dict[str, Any]:
        # Store API supports many IDs but we batch for stability
        results: Dict[str, Any] = {}
        appid_list: List[int] = list(appids)
        for i in range(0, len(appid_list), batch_size):
            chunk = appid_list[i:i+batch_size]
            id_list = ",".join(str(a) for a in chunk)
            self._respect_rate_limit()
            self.logger.info(f"Fetching appdetails batch size={len(chunk)} range={i}-{i+len(chunk)-1}")
            response = self.session.get(
                "https://store.steampowered.com/api/appdetails",
                params={"appids": id_list},
                timeout=self.timeout_seconds,
            )
            self.logger.debug(f"Response status={response.status_code}")
            response.raise_for_status()
            batch_json = response.json()
            results.update(batch_json)
        return results
