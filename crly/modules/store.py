import os

from dotmap import DotMap
from tinydb import TinyDB, Query

from .utility import Utility

# Initialize the database using the root path
# -----------
path = Utility.env.get_env('root_path')
db = TinyDB(os.path.join(path, 'db.json'))


# Query function
# -----------
def _query(prop='', value=''):
  return Query()[prop] == value


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


def _update_show(data={}, new_data={}):
  shows = db.table("shows")
  [show] = _fetch_state("show")

  if shows.search(_query('show', show)):
    shows.update(data, _query('show', show))
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
  state = db.table("state").get(doc_id=1)
  output = Utility.dict.destructure(state, args=args)
  return output if bool(output) else state


def _fetch_show(*args, show=''):
  # Allow for specified show
  if not show:
    [show] = _fetch_state("show")

  shows = db.table("shows")
  show_data = shows.get(_query('show', show))

  if not bool(show_data):
    return False

  output = Utility.dict.destructure(show_data, args)
  return output if bool(output) else show_data


def _fetch_episode(*args):
  # The episode data is stored within
  [episode_data] = _fetch_show("episode")
  output = Utility.dict.destructure(episode_data, args)
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