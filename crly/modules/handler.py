import subprocess
import os

from dotmap import DotMap
from colorama import Fore, Style

from .store import Store
from .feed import Feed
from .error import Error
from .streamlink import Streamlink
from .utility import Utility


# ANCHOR Handler.<fn>
# -----------
def _show(show="", options={}):
  # Disable command issuing while playing
  Error.check.is_playing('--show')

  # Store the old show in case the new one doesn't exist
  [previous_show] = Store.fetch.state("show")

  # Save the show (needed by Feed.get_episodes)
  Store.update_state({'show': show})
  episodes = Feed.get_episodes(show)

  # Episodes couldn't be found; save previous show to state & exit
  Error.check.no_episodes(episodes, show, previous_show)

  # Show already exists
  if bool(Store.fetch.show(show=show)):
    Store.update_show(data=episodes)

    # Alert the user
    print(f"[crly] Show is now set to {Fore.YELLOW}{show}{Style.RESET_ALL}.")

  # Show does not exist
  else:
    # Build the show data
    episode = episodes.get("episodes")[0]
    episode['index'] = 0
    data = {'show': show, 'episode': episode}
    data.update(episodes)

    # Store the show with its data
    Store.update_show(new_data=data)

    # Alert the user
    ep_num = episode.get("episode")
    print(
        f"[crly] Show is now set to {Fore.YELLOW}{show}{Style.RESET_ALL}, episode {Fore.YELLOW}{ep_num}{Style.RESET_ALL}."
    )


def _episode(ep_num="1", options={}):
  # Disable command issuing while playing
  Error.check.is_playing('--episode')

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
  Error.check.episode_not_found(show, ep_num, data)

  # Otherwise, save that data to the show object
  episodes.update({'episode': data})
  Store.update_show(data=episodes)
  print(
      f"[crly] Episode is now set to {Fore.YELLOW}{ep_num}{Fore.RESET} for {Fore.YELLOW}{show}{Fore.RESET}."
  )


def _play(value=None, options={}, check_playing=True, nextEp=False):
  # Disable command issuing while playing
  if check_playing:
    Error.check.is_playing('--play')

  # Get the show name and show data
  [show, autoplay] = Store.fetch.state("show", "autoplay")
  Error.check.must_select_show(show)

  # Check if autoplay is enabled and alert
  if autoplay:
    print(
        f"{Fore.BLUE}{Style.BRIGHT}[crly] Autoplay is enabled.{Style.RESET_ALL}"
    )
    if nextEp:
      _next(check_playing=False)

  Streamlink.play(show)

  # Check if autoplay is still enabled & play next episode
  [autoplay] = Store.fetch.state("autoplay")
  if autoplay:
    _play(check_playing=False, nextEp=True)


def _next(value=None, options={}, check_playing=True):
  # Disable command issuing while playing
  if check_playing:
    Error.check.is_playing('--next')

  # Fetch the show and episode index
  [show] = Store.fetch.state("show")
  Error.check.must_select_show(show)
  [index] = Store.fetch.episode("index")

  # Get episodes from the feed
  episodes_data = Feed.get_episodes(show)
  episodes = episodes_data.get("episodes")

  # Ensure there is a next episode
  Error.check.on_last_episode(show, episodes, index)

  # Get the new episode and assign an index
  new_episode = episodes[index + 1]
  new_episode['index'] = index + 1
  ep_num = new_episode.get("episode")

  # Merge the two
  episodes_data.update({'episode': new_episode})

  # Store the new episode & episodes_data
  Store.update_show(data=episodes_data)
  print(
      f"[crly] Episode is now set to {Fore.YELLOW}{ep_num}{Style.RESET_ALL} for {Fore.YELLOW}{show}{Style.RESET_ALL}."
  )


def _info(value=None, options={}):
  # Get the show name
  [show] = Store.fetch.state("show")
  Error.check.must_select_show(show)

  # Get the current episode
  [episode] = Store.fetch.episode("episode")

  # Get the episodes for the selected show
  episodes = Feed.get_episodes(show, silent=True).get("episodes")

  # List episodes
  print(f"{Fore.MAGENTA}[ Episodes for '{show}' ]{Style.RESET_ALL}")
  for ep in episodes:
    info = f"{ep['episode']}. {ep['title']}"
    if ep['episode'] == episode:
      info = info + f" {Fore.YELLOW}[selected]{Style.RESET_ALL}"
    print(info)


def _autoplay(value=None, options={}):
  [autoplay] = Store.fetch.state("autoplay")
  Store.update_state({'autoplay': (not autoplay)})
  on = f"{Fore.GREEN}on{Style.RESET_ALL}"
  off = f"{Fore.RED}{Style.BRIGHT}off{Style.RESET_ALL}"
  print(f"[crly] Autoplay has been turned {off if autoplay else on}.")


def _track(value=None, options={}):
  [show, tracked] = Store.fetch.state("show", "tracked")

  # Inserts or removes the given show from the tracked array
  if show in tracked:
    tracked.remove(show)
    print(f"[crly] No longer tracking {Fore.YELLOW}{show}{Style.RESET_ALL}.")
  else:
    tracked.append(show)
    print(f"[crly] Now tracking {Fore.YELLOW}{show}{Style.RESET_ALL}.")

  Store.update_state({'tracked': tracked})


def _updates(value=None, options={}):
  [selected_show, tracked] = Store.fetch.state("show", "tracked")
  updated = []
  not_updated = []

  print(
      f"{Fore.WHITE}{Style.DIM}[crly] Checking for updates...{Style.RESET_ALL}"
  )

  for show in tracked:
    # Get the latest episode
    episodes = Feed.get_episodes(show, silent=True).get("episodes")
    latest = episodes[-1]

    # Check if it was recently released and add it to updated arr
    recently_updated = Utility.date.within_n_days(latest.get("date"), 7)

    if show == selected_show:
      show = f"{show} {Fore.YELLOW}[selected]{Style.RESET_ALL}"
    if recently_updated and not latest.get("watched"):
      updated.append(f"{show} {Fore.GREEN}[updated]{Style.RESET_ALL}")
    else:
      not_updated.append(f"{show}")

  # Alert the user
  print(f"{Fore.BLUE}{Style.BRIGHT}[ Tracked Shows ]{Style.RESET_ALL}")
  print("\n".join(updated + not_updated))


def _debug(value={}, options={}):
  print("<Debug Information>", options)
  print("<State>", Store.fetch.state())
  print("<Episode>", Store.fetch.episode())


# ANCHOR - Exit Handler
# -----------
def _finish_playing():
  pid = os.getpid()
  [playing] = Store.fetch.state("playing")
  if pid == playing:
    Store.update_state({'playing': False})


# ANCHOR - Expose methods
# -----------
Handler = DotMap({
    'show': _show,
    'episode': _episode,
    'debug': _debug,
    'play': _play,
    'autoplay': _autoplay,
    'info': _info,
    'next': _next,
    'track': _track,
    'finish_playing': _finish_playing,
    'updates': _updates
})
