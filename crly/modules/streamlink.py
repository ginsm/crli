import os
import subprocess

from dotmap import DotMap
from colorama import Fore, Style

from .store import Store


# ANCHOR - Streamlink.<fn>
# -----------
def _play(show=""):
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
  out_color = Fore.YELLOW
  output = [
      f"{Fore.WHITE}{Style.DIM}[crly] Launching media player...{Style.RESET_ALL}",
      f"[crly] Show: {out_color}{show}{Fore.RESET}",
      f"[crly] Title: {out_color}{title}{Fore.RESET}",
      f"[crly] Episode: {out_color}{ep} (Season {season}){Fore.RESET}",
  ]

  print("\n".join(output))

  # Update the episode watched status
  Store.update_episode(index=index, data={'watched': True})

  # Start streamlink
  Store.update_state({'playing': os.getpid()})

  subprocess.call(
      ["streamlink", link],
      stdout=open(os.devnull, 'wb'),  # shh, be quiet
  )


# ANCHOR - Expose methods
# -----------
Streamlink = DotMap({'play': _play})
