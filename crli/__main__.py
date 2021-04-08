"""Usage:
  crly [--show <name>] [--info] [--episode <number>]
       [--quality <quality>] [--play] [--next]
       [--autoplay] [--debug] [--help | --version]

Options:
  -s, --show <name>        Select a show
  -i, --info               Print information about the show
  -e, --episode <number>   Select an episode
  -q, --quality <quality>  Set the video quality (default: "best")
  -p, --play               Play the selected episode
  -n, --next               Select the next episode
  -a, --autoplay           Autoplay episodes (default: false)
  -d, --debug              Print debug information
  -h, --help               Print this help screen
  -v, --version            Print the current version"""

import sys
import os
import json
import atexit

from docopt import docopt

from .modules.utility import Utility

# Environmental variable required for store
path = Utility.get_path(__file__)
Utility.set_env('root_path', path)

from .modules.store import Store
from .modules.error import Error
from .modules.handler import Handler
from .modules.feed import Feed


def main():
  # Initialize state and create environment variables
  Store.init_state(
      default_state={
          'show': None,
          'quality': "best",
          'lang': "en",
          'autoplay': False,
          'playing': False,
          'tracked': [],
      })

  Utility.set_env("languages", '["en"]')

  atexit.register(Handler.exit)

  [playing] = Store.fetch.state("playing")

  if playing:
    return print(
        "[crli] Error: Please close the current show before issuing commands.")

  # Handle any edge cases
  Error.check.required_native_packages(['streamlink'])
  Error.check.no_argument_help(sys.argv, __doc__)

  # Initialize docopt
  options = docopt(__doc__, help=True, version='crly v0.1.0')

  # The order in which option handlers should execute
  option_priority = [
      '--debug', '--show', '--episode', '--quality', '--next', '--info',
      '--autoplay', '--play'
  ]

  # Option handler delegation
  for opt in option_priority:
    value = options[opt]
    if value:
      # Normalize method name and retrieve method
      method_name = opt.removeprefix('--').replace('-', '_')
      method = Handler.get(method_name)

      if method and method_name == "debug":
        method(options)
      elif method:
        method(value)
      else:
        print(f"Error: Option '{opt}' hasn't been implemented yet!")


if __name__ == '__main__':
  main()