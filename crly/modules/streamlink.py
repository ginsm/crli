import os
import subprocess

from dotmap import DotMap

from .store import Store


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
      f"[crly] Launching media player...\n[crly] Show: {show}\n[crly] Title: {title}\n[crly] Episode: {ep} (Season {season})"
  )

  # Update the episode watched status
  Store.update_episode(index=index, data={'watched': True})

  # Start streamlink
  Store.update_state({'playing': os.getpid()})
  subprocess.call(["streamlink", link, quality])


Streamlink = DotMap({'play': _play})
