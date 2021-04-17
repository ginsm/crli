import sys
import subprocess

from dotmap import DotMap

from .store import Store


# ANCHOR - Error.check.<fn>
# -----------
def _required_native_packages(required_pkgs=[]):
  missing_pkg = []
  for package in required_pkgs:
    # Output is redirected to /dev/null
    response = subprocess.call(['which', package],
                               stderr=subprocess.DEVNULL,
                               stdout=subprocess.DEVNULL)
    if response != 0:
      missing_pkg.append(package)

  if len(missing_pkg):
    sys.exit(
        f"[crly] Error: Missing required linux package(s): {', '.join(missing_pkg)}."
    )


def _no_arguments_issue_help(argv, doc):
  if 1 > len(argv[1::]):
    sys.exit(doc)


def _must_select_show(show=''):
  if not show:
    sys.exit(
        "[crly] Error: You need to select a show before you can do that.\n[crly] Tip: You can select a show via 'crly --show <name>'."
    )


def _is_playing(cmd=""):
  [playing] = Store.fetch.state("playing")
  if playing:
    sys.exit(
        f"[crly] Error: Please close the current show before issuing '{cmd}'.")


def _no_episodes(episodes=[], show="", previous_show=""):
  if not bool(episodes):
    Store.update_state(data={'show': previous_show})
    sys.exit(f"[crly] Error: Could not find episodes for show '{show}'.")


def _on_last_episode(show="", episodes=[], index=0):
  if (len(episodes) - 1) == index:
    sys.exit(f"[crly] Error: There are are no more episodes for {show}.")


def _episode_not_found(show="", ep_num=0, data={}):
  if not bool(data):
    sys.exit(
        f"[crly] Error: Could not find episode {ep_num} for {show}.\n[crly] Tip: Use 'crly --info' for a list of episodes."
    )


# ANCHOR - Expose methods
# -----------
Error = DotMap({
    'check': {
        'must_select_show': _must_select_show,
        'required_native_packages': _required_native_packages,
        'no_arguments_issue_help': _no_arguments_issue_help,
        'is_playing': _is_playing,
        'no_episodes': _no_episodes,
        'on_last_episode': _on_last_episode,
        'episode_not_found': _episode_not_found
    }
})