from datetime import datetime
from datetime import timedelta
import os

from dateutil.parser import parse as parse_date
from dateutil.relativedelta import relativedelta as rdelta
from dotmap import DotMap


# Utility.dict.<fn>
def _destructure_dict(dictionary={}, args=[]):
  if len(args):
    output = []
    for arg in args:
      output.append(dictionary.get(arg))
    return output


# Utility.date.<fn>
# -----------
def _gen_next_update(date_string=""):
  if date_string:
    dt = parse_date(date_string)
    now = datetime.now()
    if dt.weekday() == now.weekday():
      now = now + rdelta(weeks=1)
    else:
      now = now + rdelta(weekday=dt.weekday())
    return datetime.combine(now.date(), dt.time())


def _within_n_days(date="", n=0):
  date = parse_date(date)
  now = datetime.now(date.tzinfo)
  if date + timedelta(days=n) >= now >= date:
    return True
  return False


# Utility.path.<fn>
# -----------
def _abs_dir(file):
  return os.path.dirname(os.path.realpath(file))


# Utility.env.<fn>
# -----------
def _set_env(name, value):
  os.environ[f"_crly_{name}"] = value


def _get_env(name):
  return os.environ.get(f"_crly_{name}")


# Utility.decorator.<fn>
# -----------
def _memoize(func):
  cache = dict()

  def fn(*args):
    # Must remove lists and dicts in order to set as prop
    sanitized = tuple(
        [x for x in list(args) if type(x) is not dict and type(x) is not list])

    if sanitized in cache:
      return cache[sanitized]
    result = func(*args)
    cache[sanitized] = result
    return result

  fn.__name__ = func.__name__
  fn.__doc__ = func.__doc__
  fn.__dict__.update(func.__dict__)

  return fn


# Utility.feed.<fn>
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
    'dict': {
        'destructure': _destructure_dict
    },
    'date': {
        'gen_next_update': _gen_next_update,
        'within_n_days': _within_n_days,
    },
    'path': {
        'abs_dir': _abs_dir,
    },
    'env': {
        'set_env': _set_env,
        'get_env': _get_env,
    },
    'decorator': {
        'memoize': _memoize,
    },
    'feed': {
        'update_needed': _update_needed
    }
})