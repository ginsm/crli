# Responsible for requesting and parsing feed data from crunchyroll:

import requests
import timeit

from bs4 import BeautifulSoup
from dotmap import DotMap

from .utility import Utility
from .store import Store


# Scraping & Parsing of Crunchy's RSS Feeds
# -----------
def _rss_feed(show="", lang="en"):
  return f"https://www.crunchyroll.com/{show}.rss"


def _scrape(feed=""):
  try:
    response = requests.get(feed)
    return BeautifulSoup(response.content, features='xml')
  except Exception as e:
    print("RSS scraping has failed. See exception:")
    return print(e)


def _episode_props(episode):
  def get_prop(name, _default="None"):
    value = episode.find(name)
    return value.text if value else _default

  return {
      'title': get_prop('crunchyroll:episodeTitle'),
      'episode': get_prop('crunchyroll:episodeNumber', "1"),
      'season': get_prop('crunchyroll:season', "1"),
      'link': get_prop("link"),
      'date': get_prop("crunchyroll:premiumPubDate")
  }


def _parse(xml=[]):
  episodes = xml.findAll('item')
  try:
    parsed_episodes = map(_episode_props, episodes)
    return list(parsed_episodes)
  except Exception as e:
    print("XML parsing has failed. See exception:")
    return print(e)


# Exposed methods
# -----------
@Utility.memoize
def _scrape_episodes(show=''):
  feed = _rss_feed(show)
  xml = _scrape(feed)
  episodes = list(_parse(xml))
  return sorted(episodes, key=lambda e: float(e['episode']))


def _get_episodes(show=""):
  show_data = Store.fetch.show(show=show)

  if Utility.update_needed(show_data):
    print("[crli] Retrieving show data...")
    episodes = _scrape_episodes(show)

    # If no episodes could be found
    if not bool(episodes):
      return False

    if show_data is not False:
      stored_episodes = show_data.get("episodes")
    else:
      stored_episodes = False

    # Check if there was any new episodes added
    if not stored_episodes or len(episodes) > len(stored_episodes):
      last_updated = episodes[-1].get("date")
      next_update = Utility.gen_next_update(last_updated)
      return {'episodes': episodes, 'next_update': next_update.timestamp()}
    # If not, check again in a week
    else:
      return {'next_update': show_data.get("next_update") + 604800}

  return {
      'episodes': show_data.get("episodes"),
  }


# Expose via DotMap
Feed = DotMap({
    'scrape_episodes': _scrape_episodes,
    'get_episodes': _get_episodes
})