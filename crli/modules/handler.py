import sys
import subprocess
import os

from dotmap import DotMap

from .store import Store
from .utility import Utility
from .feed import Feed
from .error import Error


# Option Handlers
# -----------
def _show(show="", options={}):
  # Store the old show in case the new one doesn't exist
  [previous_show] = Store.fetch.state("show")

  # Save the show (needed by Feed.get_episodes)
  Store.update_state({'show': show})
  episodes = Feed.get_episodes(show)

  # Episodes couldn't be found; stop execution
  if not bool(episodes):
    Store.update_state(data={'show': previous_show})
    sys.exit(f"[crli] Error: Could not find episodes for show '{show}'.")

  # Show exists
  if bool(Store.fetch.show(show=show)):
    Store.update_show(data=episodes)
    print(f"[crli] Show is now set to '{show}'.")

  # Show does not exist
  else:
    # Build the show data to store it
    episode = episodes.get("episodes")[0]
    ep_num = episode.get("episode")
    data = {'show': show, 'episode': episode}
    data['episode']['index'] = 0
    data.update(episodes)

    # Store the show with its data
    Store.update_show(new_data=data)
    print(f"[crli] Show is now set to '{show}', episode {ep_num}.")


def _episode(ep_num="1", options={}):
  # Get the show name and episodes
  [show] = Store.fetch.state("show")
  Error.check.must_select_show(show)
  episodes = Feed.get_episodes(show)

  # Filter for episode data
  data = {}
  for i, ep in enumerate(episodes.get("episodes")):
    if ep.get("episode") == ep_num:
      data = ep
      data['index'] = i
      break

  # Handle episode not found
  if not bool(data):
    return print(
        f"[crli] Error: Could not find episode {ep_num} for {show}.\n[crli] Tip: Use 'crli --info' for a list of episodes."
    )

  # Otherwise, save that data to the show object
  else:
    episodes.update({'episode': data})
    Store.update_show(data=episodes)
    print(f"[crli] Episode is now set to '{ep_num}' for {show}.")
    return True

  return False


def _play(value=None, options={}):
  # Get the show name and show data
  [show, quality, autoplay] = Store.fetch.state("show", "quality", "autoplay")
  Error.check.must_select_show(show)

  def play_episode(show="", quality="best"):
    [ep, season, title, link] = Store.fetch.episode("episode", "season",
                                                    "title", "link")

    # Alert the user about what content is playing
    print(
        f"[crli] Launching media player...\n[crli] Show: {show}\n[crli] Title: {title}\n[crli] Episode: {ep} (Season {season})"
    )

    # Start streamlink
    Store.update_state({'playing': os.getpid()})
    subprocess.call(["streamlink", link, quality])

  if autoplay:
    while True:
      print("[crli] Autoplay is enabled.")
      play_episode(show, quality)
      _next()
  else:
    play_episode(show, quality)


def _next(value=None, options={}):
  [show] = Store.fetch.state("show")
  Error.check.must_select_show(show)

  [index] = Store.fetch.episode("index")

  # Get episodes from the feed
  episodes_data = Feed.get_episodes(show)
  episodes = episodes_data.get("episodes")

  # Ensure there is a next episode
  if (len(episodes) - 1) == index:
    sys.exit(f"[crli] Error: There are are no more episodes for {show}.")

  # Get the new episode and assign an index
  new_episode = episodes[index + 1]
  new_episode['index'] = index + 1
  ep_num = new_episode.get("episode")

  # Merge the two
  episodes_data.update({'episode': new_episode})

  # Store the new episode & episodes_data
  Store.update_show(data=episodes_data)
  print(f"[crli] Episode is now set to '{ep_num}' for {show}.")
  return


def _info(value=None, options={}):
  # Get the show name
  [show] = Store.fetch.state("show")
  Error.check.must_select_show(show)

  # Get the current episode
  [episode] = Store.fetch.episode("episode")

  # Get the episodes for the selected show
  episodes = Feed.get_episodes(show).get("episodes")

  # List episodes
  print(f"[  '{show}' Episodes  ]")
  for ep in episodes:
    info = f"{ep['episode']}. {ep['title']}"
    if ep['episode'] == episode:
      info = "* " + info
    print(info)


def _quality(value="best", options={}):
  Store.update_state({'quality': value})


def _autoplay(value=None, options={}):
  [autoplay] = Store.fetch.state("autoplay")
  Store.update_state({'autoplay': (not autoplay)})
  print(f"[crli] Autoplay has been turned {'off' if autoplay else 'on'}.")


def _debug(value={}, options={}):
  print("<Debug Information>", options)


# Exit Handler
# -----------
def _playing():
  pid = os.getpid()
  [playing] = Store.fetch.state("playing")
  if pid == playing:
    Store.update_state({'playing': False})


Handler = DotMap({
    'show': _show,
    'episode': _episode,
    'debug': _debug,
    'quality': _quality,
    'play': _play,
    'autoplay': _autoplay,
    'info': _info,
    'next': _next,
    'playing': _playing
})
