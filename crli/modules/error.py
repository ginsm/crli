import sys
import subprocess

from dotmap import DotMap


def _required_native_packages(required_pkgs=[]):
  missing_pkg = []
  for package in required_pkgs:
    # Output is redirected to /dev/null
    response = subprocess.call(['which', package],
                               stderr=subprocess.DEVNULL,
                               stdout=subprocess.DEVNULL)

    # Handle response
    if response != 0:
      missing_pkg.append(package)
    if len(missing_pkg):
      sys.exit(
          f"[crli] Error: Missing required linux package(s): {', '.join(missing_pkg)}."
      )


def _no_arguments_issue_help(argv, doc):
  if 1 > len(argv[1::]):
    sys.exit(doc)


def _must_select_show(show=''):
  if not show:
    sys.exit(
        "[crli] Error: You need to select a show before you can do that.\n[crli] Tip: You can select a show via 'crli --show <name>'."
    )


def _is_playing(playing=False):
  if playing:
    return print(
        "[crli] Error: Please close the current show before issuing commands.")


Error = DotMap({
    'check': {
        'must_select_show': _must_select_show,
        'required_native_packages': _required_native_packages,
        'no_arguments_issue_help': _no_arguments_issue_help,
        'is_playing': _is_playing
    }
})