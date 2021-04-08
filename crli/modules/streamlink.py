import subprocess

from dotmap import DotMap

from .store import Store


def _play(link="", quality="best"):
  Store.update_state({'playing': os.getpid()})
  subprocess.call("streamlink", link, quality)


Streamlink = DotMap({'play': _play})
