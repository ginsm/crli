import os
import subprocess

from dotmap import DotMap
from colorama import Fore, Style

from .store import Store


# ANCHOR - Streamlink.<fn>
# -----------
def _play(show="", quality="best"):
  # Get episode and props
  episode = Store.fetch.episode()
  [ep, season, title, link, index] = [
      episode.get("episode"),
      episode.get("season"),
      episode.get("title"),
      episode.get("link"),
      episode.get("index")
  ]

  # Alert the user about what content is playing
  print(
      f"{Fore.WHITE}{Style.DIM}[crly] Launching media player...{Style.RESET_ALL}\n[crly] Show: {Fore.YELLOW}{show}{Style.RESET_ALL}\n[crly] Title: {Fore.YELLOW}{title}{Style.RESET_ALL}\n[crly] Episode: {Fore.YELLOW}{ep} (Season {season}){Style.RESET_ALL}"
  )

  # Update the episode watched status
  Store.update_episode(index=index, data={'watched': True})

  # Start streamlink
  Store.update_state({'playing': os.getpid()})
  subprocess.call(["streamlink", link, quality])


# ANCHOR - Expose methods
# -----------
Streamlink = DotMap({'play': _play})
