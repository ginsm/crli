import os

from dotmap import DotMap
from tinydb import TinyDB, Query

from .utility import Utility

# Initialize the database using the root path
# -----------
path = Utility.env.get_env('root_path')
db = TinyDB(os.path.join(path, 'db.json'))


# Utility Functions
# -----------
def _query_show(value=''):
  return Query().show == value


# Allows for destructuring as a list
def _destructure_dict(dictionary={}, args=[]):
  if len(args):
    output = []
    for arg in args:
      output.append(dictionary.get(arg))
    return output


# Initializer
# -----------
def _init_state(default_state={}):
  state = db.table("state")
  if state.get(doc_id=1) is None:
    state.insert(default_state)


# Exposed methods (setters)
# -----------
def _update_state(data={}):
  state = db.table("state")
  if bool(data):
    state.update(data, doc_ids=[1])
  return state.get(doc_id=1)


def _update_show(data={}, new_data={}):
  shows = db.table("shows")
  [show] = _fetch_state("show")

  if shows.search(_query_show(show)):
    shows.update(data, _query_show(show))
  elif bool(new_data):
    shows.insert(new_data)


def _update_episode(index=0, data={}):
  if bool(data):
    [episodes] = _fetch_show("episodes")
    episodes[index].update(data)
    _update_show(data={'episodes': episodes})


# Exposed methods (getters)
# -----------
def _fetch_state(*args):
  # state object
  state = db.table("state").get(doc_id=1)
  # allow for custom data fetches
  output = _destructure_dict(state, args=args)
  return output if bool(output) else state


def _fetch_show(*args, show=''):
  # Allow for specified show
  if not show:
    [show] = _fetch_state("show")

  # Retrieve the show's data
  shows = db.table("shows")
  show_data = shows.get(_query_show(show))

  # If no previous data was found, return False
  if not bool(show_data):
    return False

  # Allow for custom data fetches, otherwise return show's data
  output = _destructure_dict(show_data, args)
  return output if bool(output) else show_data


def _fetch_episode(*args):
  # The episode data is stored within
  [episode_data] = _fetch_show("episode")
  output = _destructure_dict(episode_data, args)
  return output if bool(output) else episode_data


Store = DotMap({
    'init_state': _init_state,
    'update_show': _update_show,
    'update_state': _update_state,
    'update_episode': _update_episode,
    'fetch': {
        'state': _fetch_state,
        'show': _fetch_show,
        'episode': _fetch_episode
    }
})