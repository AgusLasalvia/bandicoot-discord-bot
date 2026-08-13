from logic.player import MusicPlayer, SongInfo


def test_song_info_defaults_title_to_url():
    song = SongInfo(url="https://youtu.be/abc")
    assert song.title == "https://youtu.be/abc"


def test_song_info_format_duration_minutes_seconds():
    song = SongInfo(url="u", duration=125)
    assert song.format_duration() == "2:05"


def test_song_info_format_duration_hours():
    song = SongInfo(url="u", duration=3725)
    assert song.format_duration() == "1:02:05"


def test_song_info_format_duration_unknown():
    song = SongInfo(url="u")
    assert song.format_duration() == "Unknown"


def test_add_to_queue_and_queue_length():
    player = MusicPlayer()
    player.add_to_queue(SongInfo(url="a"))
    player.add_to_queue(SongInfo(url="b"))

    assert player.get_queue_length() == 2


def test_clear_queue_resets_playback_state():
    player = MusicPlayer()
    player.add_to_queue(SongInfo(url="a"))
    player.current_song = SongInfo(url="a")
    player.is_playing = True

    player.clear_queue()

    assert player.get_queue_length() == 0
    assert player.current_song is None
    assert player.is_playing is False


def test_toggle_loop():
    player = MusicPlayer()

    assert player.toggle_loop() is True
    assert player.loop is True
    assert player.toggle_loop() is False
    assert player.loop is False


def test_toggle_shuffle_preserves_queue_contents():
    player = MusicPlayer()
    for i in range(10):
        player.add_to_queue(SongInfo(url=f"song-{i}"))
    original_urls = {song.url for song in player.queue}

    result = player.toggle_shuffle()

    assert result is True
    assert player.shuffle is True
    assert player.get_queue_length() == 10
    assert {song.url for song in player.queue} == original_urls
