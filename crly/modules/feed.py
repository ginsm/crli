import requests

from bs4 import BeautifulSoup
from dotmap import DotMap

from .utility import Utility
from .store import Store


# ANCHOR - Utility Function
# -----------
def _episode_props(episode):
  def get_prop(name, _default="None"):
    value = episode.find(name)
    return value.text if value else _default

  return {
      'title': get_prop('crunchyroll:episodeTitle'),
      'episode': get_prop('crunchyroll:episodeNumber', "1"),
      'season': get_prop('crunchyroll:season', "1"),
      'link': get_prop("link"),
      'date': get_prop("crunchyroll:premiumPubDate"),
      'watched': False
  }


# ANCHOR - Scraping & Parsing of Crunchy's RSS Feeds
# -----------
def _rss_feed(show=""):
  return f"https://www.crunchyroll.com/{show}.rss"


def _scrape(feed=""):
  try:
    response = requests.get(feed)
    return BeautifulSoup(response.content, features='xml')
  except Exception as e:
    print("RSS scraping has failed. See exception:")
    return print(e)


def _parse(xml=[], old_amount=0):
  episodes = xml.findAll('item')
  try:
    new_episodes_amount = len(episodes) - old_amount
    parsed_episodes = map(_episode_props, episodes[0:new_episodes_amount])
    return list(parsed_episodes)
  except Exception as e:
    print("XML parsing has failed. See exception:")
    return print(e)


@Utility.decorator.memoize
def _scrape_episodes(show='', old_amount=0):
  feed = _rss_feed(show)
  xml = _scrape(feed)
  episodes = _parse(xml, old_amount)
  return sorted(episodes, key=lambda e: float(e['episode']))


# ANCHOR - Feed.<fn>
# -----------
def _get_episodes(show="", silent=False):
  show_data = (Store.fetch.show(show=show) or {})

  if Utility.feed.update_needed(show_data):
    if not silent:
      print("[crly] Retrieving show data...")
    old_episodes = (show_data.get("episodes") or [])
    episodes = old_episodes + _scrape_episodes(show, len(old_episodes))

    if not bool(episodes):
      return False

    if len(episodes) > len(old_episodes):
      last_updated = episodes[-1].get("date")
      next_update = Utility.date.gen_next_update(last_updated)
      return {'episodes': episodes, 'next_update': next_update.timestamp()}
    else:
      return {
          'episodes': episodes,
          'next_update': show_data.get("next_update") + 604800
      }

  return show_data


# ANCHOR - Expose methods
# -----------
Feed = DotMap({'get_episodes': _get_episodes})
