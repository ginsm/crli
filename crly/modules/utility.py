from datetime import datetime
from datetime import timedelta
import os

from dateutil.parser import parse as parse_date
from dateutil.relativedelta import relativedelta as rdelta
from dotmap import DotMap


# Dates
# -----------
def _date_to_ms(date_string=""):
  if date_string:
    return parse_date(date_string).timestamp()
  return None


def _gen_next_update(date_string=""):
  if date_string:
    dt = parse_date(date_string)
    now = datetime.now()
    if dt.weekday() == now.weekday():
      now = now + rdelta(weeks=1)
    else:
      now = now + rdelta(weekday=dt.weekday())
    return datetime.combine(now.date(), dt.time())


def _date_within_n_days(date="", n=0):
  date = parse_date(date)
  now = datetime.now(date.tzinfo)
  if date + timedelta(days=n) >= now >= date:
    return True
  return False


# Paths
# -----------
def _get_path(file):
  return os.path.dirname(os.path.realpath(file))


# Environment setters/getters
# -----------
def _set_env(name, value):
  os.environ[f"_crly_{name}"] = value


def _set_env_multi(dictionary={}):
  for key, value in dictionary.items():
    if value:
      _set_env(key, value)


def _get_env(name):
  return os.environ.get(f"_crly_{name}")


def _get_env_multi(*args):
  output = {}
  for arg in args:
    output[arg] = _get_env(arg)
  return output


# Memoization
# -----------
def _memoize(func):
  cache = dict()

  def memoized_fn(*args):
    # Must remove lists and dicts in order to set as prop
    sanitized = tuple(
        [x for x in list(args) if type(x) is not dict and type(x) is not list])

    if sanitized in cache:
      return cache[sanitized]
    result = func(*args)
    cache[sanitized] = result
    return result

  memoized_fn.__name__ = func.__name__
  memoized_fn.__doc__ = func.__doc__
  memoized_fn.__dict__.update(func.__dict__)

  return memoized_fn


# Check if a show needs to be updated
# -----------
def _update_needed(show_data={}):
  if bool(show_data):
    current_time = datetime.now().timestamp()
    next_update = show_data.get("next_update")
    return (not next_update or current_time >= next_update)
  else:
    return True


# Expose methods
# -----------
Utility = DotMap({
    'gen_next_update': _gen_next_update,
    'date_to_ms': _date_to_ms,
    'date_within_n_days': _date_within_n_days,
    'get_path': _get_path,
    'set_env': _set_env,
    'set_env_multi': _set_env_multi,
    'get_env': _get_env,
    'get_env_multi': _get_env_multi,
    'memoize': _memoize,
    'update_needed': _update_needed
})