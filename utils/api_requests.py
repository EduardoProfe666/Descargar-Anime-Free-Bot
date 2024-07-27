import time
from typing import Any, List

from cloudscraper.exceptions import CloudflareChallengeError

from api.animeflv import AnimeInfo, AnimeFLV, EpisodeInfoDownload, EpisodeInfo, DownloadLinkInfo


def wrap_request(func, *args, count: int = 10, expected: Any):
    """
    Wraps a request sent by the module to test if it works correctly, tries `count` times sleeps
    5 seconds if an error is encountered.

    If `CloudflareChallengeError` is encountered, the expected result will be returned
    to make it possible for automated tests to pass

    :param *args: args to call the function with.
    :param count: amount of tries
    :param expected: example for a valid return, this is used when cloudscraper complains
    :rtype: Any
    """
    notes = []

    for _ in range(count):
        try:
            res = func(*args)
            if isinstance(res, list) and len(res) < 1:
                raise ValueError()  # Raise ValueError to retry test when empty array is returned
            return res
        except CloudflareChallengeError:
            return expected
        except Exception as exc:
            notes.append(exc)
            time.sleep(5)
    raise Exception(notes)


def search_animes(search: str):
    with AnimeFLV() as api:
        data = wrap_request(api.search, search, expected=[AnimeInfo(0, "")])
    return data

def latest_animes():
    with AnimeFLV() as api:
        data = wrap_request(api.get_latest_animes, expected=[AnimeInfo(0, "")])
    return data

def get_anime_episodes(id: str) -> List[EpisodeInfo]:
    with AnimeFLV() as api:
        data: List[EpisodeInfo] = wrap_request(api.get_anime_info, id, expected=[AnimeInfo(0, "")]).episodes
    return data

def get_anime_episode_info_download(id: str) -> List[EpisodeInfoDownload]:
    with AnimeFLV() as api:
        data: List[EpisodeInfo] = wrap_request(api.get_anime_info, id, expected=[AnimeInfo(0, "")]).episodes

        r: List[EpisodeInfoDownload] = []

        for e in data:
            download = wrap_request(api.get_links, f'{e.anime}-{e.id}', expected=[List[DownloadLinkInfo('', '')]])
            r.append(EpisodeInfoDownload(id=e.id, anime=e.anime, image_preview=e.image_preview, downloads=download))
    return r

