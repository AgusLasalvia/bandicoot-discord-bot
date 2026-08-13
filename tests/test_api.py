from unittest.mock import AsyncMock, patch

import pytest

import logic.api as api


class FakeResponse:
    """Mimics the aiohttp response async-context-manager protocol."""

    def __init__(self, status, json_data):
        self.status = status
        self._json_data = json_data

    async def json(self):
        return self._json_data

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakeSession:
    """Mimics the aiohttp.ClientSession methods used by logic/api.py."""

    def __init__(self, post_response=None, get_response=None):
        self._post_response = post_response
        self._get_response = get_response
        self.closed = False

    def post(self, url, json=None):
        return self._post_response

    def get(self, url, headers=None):
        return self._get_response


@pytest.fixture(autouse=True)
def reset_api_module_state():
    api.token = None
    api.session = None
    yield
    api.token = None
    api.session = None


async def test_get_token_stores_token_on_success():
    fake_session = FakeSession(post_response=FakeResponse(200, {"token": "abc123"}))
    with patch("logic.api.get_session", AsyncMock(return_value=fake_session)):
        await api.get_token()

    assert api.token == "abc123"


async def test_get_token_leaves_token_none_on_failure():
    fake_session = FakeSession(post_response=FakeResponse(401, {"error": "invalid credentials"}))
    with patch("logic.api.get_session", AsyncMock(return_value=fake_session)):
        await api.get_token()

    assert api.token is None


async def test_get_playlists_returns_data_on_success():
    api.token = "abc123"
    playlists = [{"id": "1", "name": "Chill"}]
    fake_session = FakeSession(get_response=FakeResponse(200, playlists))
    with patch("logic.api.get_session", AsyncMock(return_value=fake_session)):
        result = await api.get_playlists()

    assert result == playlists


async def test_get_playlists_returns_empty_list_on_error_status():
    api.token = "abc123"
    fake_session = FakeSession(get_response=FakeResponse(500, {}))
    with patch("logic.api.get_session", AsyncMock(return_value=fake_session)):
        result = await api.get_playlists()

    assert result == []


async def test_get_playlist_songs_extracts_ids_from_plain_list():
    api.token = "abc123"
    songs = [{"youtube_id": "aaa"}, {"youtubeId": "bbb"}, {"id": "ccc"}, {"title": "no id here"}]
    fake_session = FakeSession(get_response=FakeResponse(200, songs))
    with patch("logic.api.get_session", AsyncMock(return_value=fake_session)):
        result = await api.get_playlist_songs("playlist-1")

    assert result == ["aaa", "bbb", "ccc"]


async def test_get_playlist_songs_extracts_ids_from_wrapped_playlist_object():
    api.token = "abc123"
    payload = {"songs": [{"youtube_id": "zzz"}]}
    fake_session = FakeSession(get_response=FakeResponse(200, payload))
    with patch("logic.api.get_session", AsyncMock(return_value=fake_session)):
        result = await api.get_playlist_songs("playlist-1")

    assert result == ["zzz"]


async def test_get_playlist_songs_returns_empty_list_on_error_status():
    api.token = "abc123"
    fake_session = FakeSession(get_response=FakeResponse(404, {}))
    with patch("logic.api.get_session", AsyncMock(return_value=fake_session)):
        result = await api.get_playlist_songs("missing-playlist")

    assert result == []
