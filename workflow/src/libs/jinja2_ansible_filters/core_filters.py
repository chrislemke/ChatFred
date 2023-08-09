# (c) 2012, Jeroen Hoekx <jeroen@hoekx.be>
#
# This file was ported from Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import base64
import datetime
import glob
import hashlib
import json
import ntpath
import os.path
import re
import time
import uuid
from functools import partial
from random import Random, SystemRandom, shuffle

import yaml
from jinja2.exceptions import FilterArgumentError
try:
    from jinja2.filters import environmentfilter as pass_environment
except ImportError:  # renamed in jinja2 3.1
    from jinja2.filters import pass_environment
from jinja2.filters import do_groupby as _do_groupby

from jinja2_ansible_filters.ansible_utils import (recursive_check_defined,
                                                  merge_hash)
from jinja2_ansible_filters.module_utils import (is_sequence,
                                                 integer_types,
                                                 string_types,
                                                 to_bytes,
                                                 to_native,
                                                 to_text,
                                                 unicode_wrap)

try:
    from functools import reduce
    from shlex import quote as shlex_quote
except ImportError:  # pragma: no cover
    # reduce builtin in python2.x
    from pipes import quote as shlex_quote

# Note, sha1 is the only hash algorithm compatible with python2.4 and with
# FIPS-140 mode (as of 11-2014)
try:
    from hashlib import sha1
except ImportError:  # pragma: no cover
    from sha import sha as sha1

# Backwards compat only
try:  # pragma: no cover
    from hashlib import md5 as _md5
except ImportError:  # pragma: no cover
    try:
        from md5 import md5 as _md5
    except ImportError:  # pragma: no cover
        # Assume we're running in FIPS mode here
        _md5 = None


UUID_NAMESPACE = uuid.UUID("20851c88-ac15-449f-9ee7-74829105da86")


def to_yaml(a, *args, **kw):
    """Make verbose, human readable yaml"""
    default_flow_style = kw.pop("default_flow_style", None)
    transformed = yaml.dump(a,
                            allow_unicode=True,
                            default_flow_style=default_flow_style,
                            **kw)
    return to_text(transformed)


def to_nice_yaml(a, indent=4, *args, **kw):
    """Make verbose, human readable yaml"""
    transformed = yaml.dump(a,
                            indent=indent,
                            allow_unicode=True,
                            default_flow_style=False,
                            **kw)
    return to_text(transformed)


def to_json(a, *args, **kw):
    """ Convert the value to JSON """
    return json.dumps(a, *args, **kw)


def to_nice_json(a, indent=4, sort_keys=True, *args, **kw):
    """Make verbose, human readable JSON"""
    try:
        return json.dumps(a, indent=indent, sort_keys=sort_keys,
                          separators=(",", ": "),
                          *args, **kw)
    except Exception:
        return to_json(a, *args, **kw)


def to_bool(a):
    """ return a bool for the arg """
    if a is None or isinstance(a, bool):
        return a
    if isinstance(a, string_types):
        a = a.lower()
    if a in ("yes", "on", "1", "true", 1):
        return True
    return False


def to_datetime(_string, format="%Y-%m-%d %H:%M:%S"):
    return datetime.datetime.strptime(_string, format)


def strftime(string_format, second=None):
    """ return a date string using string.
    See https://docs.python.org/2/library/time.html#time.strftime for format """
    if second is not None:
        try:
            second = int(second)
        except Exception:
            raise FilterArgumentError(
                "Invalid value for epoch value (%s)" % second)
    return time.strftime(string_format, time.localtime(second))


def quote(a):
    """ return its argument quoted for shell usage """
    return shlex_quote(to_text(a))


def fileglob(pathname):
    """ return list of matched regular files for glob """
    return [g for g in glob.glob(pathname) if os.path.isfile(g)]


def regex_replace(value="", pattern="", replacement="", ignorecase=False):
    """ Perform a `re.sub` returning a string """

    value = to_text(value, errors="surrogate_or_strict", nonstring="simplerepr")

    if ignorecase:
        flags = re.I
    else:
        flags = 0
    _re = re.compile(pattern, flags=flags)
    return _re.sub(replacement, value)


def regex_findall(value, regex, multiline=False, ignorecase=False):
    """ Perform re.findall and return the list of matches """
    flags = 0
    if ignorecase:
        flags |= re.I
    if multiline:
        flags |= re.M
    return re.findall(regex, value, flags)


def regex_search(value, regex, *args, **kwargs):
    """ Perform re.search and return the list of matches or a backref """

    groups = list()
    for arg in args:
        if arg.startswith("\\g"):
            match = re.match(r"\\g<(\S+)>", arg).group(1)
            groups.append(match)
        elif arg.startswith("\\"):
            match = int(re.match(r"\\(\d+)", arg).group(1))
            groups.append(match)
        else:
            raise FilterArgumentError("Unknown argument")

    flags = 0
    if kwargs.get("ignorecase"):
        flags |= re.I
    if kwargs.get("multiline"):
        flags |= re.M

    match = re.search(regex, value, flags)
    if match:
        if not groups:
            return match.group()
        else:
            items = list()
            for item in groups:
                items.append(match.group(item))
            return items


def ternary(value, true_val, false_val, none_val=None):
    """  value ? true_val : false_val """
    if value is None and none_val is not None:
        return none_val
    elif bool(value):
        return true_val
    else:
        return false_val


def regex_escape(string, re_type="python"):
    """Escape all regular expressions special characters from STRING."""
    if re_type == "python":
        return re.escape(string)
    elif re_type == "posix_basic":
        # list of BRE special chars:
        return regex_replace(string, r"([].[^$*\\])", r"\\\1")
    elif re_type == "posix_extended":
        raise NotImplementedError(
            "Regex type (%s) not yet implemented" % re_type)
    else:
        raise NotImplementedError("Invalid regex type (%s)" % re_type)


def from_yaml(data):
    if isinstance(data, string_types):
        return yaml.safe_load(data)
    return data


def from_yaml_all(data):
    if isinstance(data, string_types):
        return yaml.safe_load_all(data)
    return data


@pass_environment
def rand(environment, end, start=None, step=None, seed=None):
    if seed is None:
        r = SystemRandom()
    else:
        r = Random(seed)
    if isinstance(end, integer_types):
        if not start:
            start = 0
        if not step:
            step = 1
        return r.randrange(start, end, step)
    elif hasattr(end, "__iter__"):
        if start or step:
            raise FilterArgumentError("start and step can only be "
                                      "used with integer values")
        return r.choice(end)
    else:
        raise FilterArgumentError("random can only be used on "
                                  "sequences and integers")


def randomize_list(mylist, seed=None):
    try:
        mylist = list(mylist)
        if seed:
            r = Random(seed)
            r.shuffle(mylist)
        else:
            shuffle(mylist)
    except Exception:
        pass
    return mylist


def get_hash(data, hashtype="sha1"):

    try:  # see if hash is supported
        h = hashlib.new(hashtype)
    except Exception:
        return None

    h.update(to_bytes(data, errors="surrogate_or_strict"))
    return h.hexdigest()


def to_uuid(string):
    return str(uuid.uuid5(UUID_NAMESPACE, str(string)))


def mandatory(a, msg=None):
    from jinja2.runtime import Undefined

    """ Make a variable mandatory """
    if isinstance(a, Undefined):
        if a._undefined_name is not None:
            name = "\"%s\" " % to_text(a._undefined_name)
        else:
            name = ""

        if msg is not None:
            raise FilterArgumentError(to_native(msg))
        else:
            raise FilterArgumentError(
                "Mandatory variable %s not defined." % name)

    return a


def combine(*terms, **kwargs):
    recursive = kwargs.pop('recursive', False)
    list_merge = kwargs.pop('list_merge', 'replace')
    if kwargs:
        raise FilterArgumentError("'recursive' and 'list_merge' "
                                  + "are the only valid keyword arguments")

    # allow the user to do `[dict1, dict2, ...] | combine`
    dictionaries = flatten(terms, levels=1)

    # recursively check that every elements are defined (for jinja2)
    recursive_check_defined(dictionaries)

    if not dictionaries:
        return {}

    if len(dictionaries) == 1:
        return dictionaries[0]

    # merge all the dicts so that the dict at
    # the end of the array have precedence
    # over the dict at the beginning.
    # we merge the dicts from the highest
    # to the lowest priority because there is
    # a huge probability that the lowest
    # priority dict will be the biggest in size
    # (as the low prio dict will hold
    # the "default" values and the others will be "patches")
    # and merge_hash create a copy of it's first argument.
    # so high/right -> low/left is more efficient than low/left -> high/right
    high_to_low_prio_dict_iterator = reversed(dictionaries)
    result = next(high_to_low_prio_dict_iterator)
    for dictionary in high_to_low_prio_dict_iterator:
        result = merge_hash(dictionary, result, recursive, list_merge)

    return result


def comment(text, style="plain", **kw):
    # Predefined comment types
    comment_styles = {
        "plain": {
            "decoration": "# "
        },
        "erlang": {
            "decoration": "% "
        },
        "c": {
            "decoration": "// "
        },
        "cblock": {
            "beginning": "/*",
            "decoration": " * ",
            "end": " */"
        },
        "xml": {
            "beginning": "<!--",
            "decoration": " - ",
            "end": "-->"
        }
    }

    # Pointer to the right comment type
    style_params = comment_styles[style]

    if "decoration" in kw:
        prepostfix = kw["decoration"]
    else:
        prepostfix = style_params["decoration"]

    # Default params
    p = {
        "newline": "\n",
        "beginning": "",
        "prefix": (prepostfix).rstrip(),
        "prefix_count": 1,
        "decoration": "",
        "postfix": (prepostfix).rstrip(),
        "postfix_count": 1,
        "end": ""
    }

    # Update default params
    p.update(style_params)
    p.update(kw)

    # Compose substrings for the final string
    str_beginning = ""
    if p["beginning"]:
        str_beginning = "%s%s" % (p["beginning"], p["newline"])
    str_prefix = ""
    if p["prefix"]:
        if p["prefix"] != p["newline"]:
            str_prefix = str(
                "%s%s" % (p["prefix"], p["newline"])) * int(p["prefix_count"])
        else:
            str_prefix = str(
                "%s" % (p["newline"])) * int(p["prefix_count"])
    str_text = ("%s%s" % (
        p["decoration"],
        # Prepend each line of the text with the decorator
        text.replace(
            p["newline"], "%s%s" % (p["newline"], p["decoration"])))).replace(
                # Remove trailing spaces when only decorator is on the line
                "%s%s" % (p["decoration"], p["newline"]),
                "%s%s" % (p["decoration"].rstrip(), p["newline"]))
    str_postfix = p["newline"].join(
        [""] + [p["postfix"] for x in range(p["postfix_count"])])
    str_end = ""
    if p["end"]:
        str_end = "%s%s" % (p["newline"], p["end"])

    # Return the final string
    return "%s%s%s%s%s" % (
        str_beginning,
        str_prefix,
        str_text,
        str_postfix,
        str_end)


def extract(item, container, morekeys=None):
    from jinja2.runtime import Undefined

    value = container[item]

    if value is not Undefined and morekeys is not None:
        if not isinstance(morekeys, list):
            morekeys = [morekeys]

        try:
            value = reduce(lambda d, k: d[k], morekeys, value)
        except KeyError:
            value = Undefined()

    return value


@pass_environment
def do_groupby(environment, value, attribute):
    """Overridden groupby filter for jinja2, to address an issue with
    jinja2>=2.9.0,<2.9.5 where a namedtuple was returned which
    has repr that prevents ansible.template.safe_eval.safe_eval from being
    able to parse and eval the data.

    jinja2<2.9.0,>=2.9.5 is not affected, as <2.9.0 uses a tuple, and
    >=2.9.5 uses a standard tuple repr on the namedtuple.

    The adaptation here, is to run the jinja2 `do_groupby` function, and
    cast all of the namedtuples to a regular tuple.

    See https://github.com/ansible/ansible/issues/20098

    We may be able to remove this in the future.
    """
    return [tuple(t) for t in _do_groupby(environment, value, attribute)]


def b64encode(string, encoding="utf-8"):
    return to_text(base64.b64encode(to_bytes(string,
                                             encoding=encoding,
                                             errors="surrogate_or_strict")))


def b64decode(string, encoding="utf-8"):
    return to_text(base64.b64decode(to_bytes(string,
                                             errors="surrogate_or_strict")),
                   encoding=encoding)


def flatten(mylist, levels=None):

    ret = []
    for element in mylist:
        if element in (None, "None", "null"):
            # ignore undefined items
            break
        elif is_sequence(element):
            if levels is None:
                ret.extend(flatten(element))
            elif levels >= 1:
                # decrement as we go down the stack
                ret.extend(flatten(element, levels=(int(levels) - 1)))
            else:
                ret.append(element)
        else:
            ret.append(element)

    return ret


def subelements(obj, subelements, skip_missing=False):
    """Accepts a dict or list of dicts, and a dotted accessor
    and produces a product of the element and the results of
    the dotted accessor

    >>> obj = [{"name": "alice",
                "groups": ["wheel"],
                "authorized": ["/tmp/alice/onekey.pub"]}]
    >>> subelements(obj, "groups")
        [({"name": "alice",
          "groups": ["wheel"],
          "authorized": ["/tmp/alice/onekey.pub"]},
         "wheel")]

    """
    if isinstance(obj, dict):
        element_list = list(obj.values())
    elif isinstance(obj, list):
        element_list = obj[:]
    else:
        raise FilterArgumentError(
            "obj must be a list of dicts or a nested dict")

    if isinstance(subelements, list):
        subelement_list = subelements[:]
    elif isinstance(subelements, string_types):
        subelement_list = subelements.split(".")
    else:
        raise FilterArgumentError(
            "subelements must be a list or a string")

    results = []

    for element in element_list:
        values = element
        for subelement in subelement_list:
            try:
                values = values[subelement]
            except KeyError:
                if skip_missing:
                    values = []
                    break
                raise FilterArgumentError(
                    "could not find %r key in iterated item %r" % (subelement,
                                                                   values))
            except TypeError:
                raise FilterArgumentError(
                    "the key %s should point to a dictionary, "
                    "got \"%s\"" % (subelement, values))
        if not isinstance(values, list):
            raise FilterArgumentError(
                "the key %r should point to a list, got %r" % (subelement,
                                                               values))

        for value in values:
            results.append((element, value))

    return results


def random_mac(value, seed=None):
    """ takes string prefix, and return it completed with random bytes
        to get a complete 6 bytes MAC address """

    if not isinstance(value, string_types):
        raise FilterArgumentError(
            "Invalid value type (%s) for random_mac (%s)" % (type(value),
                                                             value))

    value = value.lower()
    mac_items = value.split(":")

    if len(mac_items) > 5:
        raise FilterArgumentError(
            "Invalid value (%s) for random_mac: "
            "5 colon(:) separated items max" % value)

    err = ""
    for mac in mac_items:
        if len(mac) == 0:
            err += ",empty item"
            continue
        if not re.match("[a-f0-9]{2}", mac):
            err += ",%s not hexa byte" % mac
    err = err.strip(",")

    if len(err):
        raise FilterArgumentError("Invalid value (%s)"
                                  " for random_mac: %s" % (value, err))

    if seed is None:
        r = SystemRandom()
    else:
        r = Random(seed)
    # Generate random int between x1000000000 and xFFFFFFFFFF
    v = r.randint(68719476736, 1099511627775)
    # Select first n chars to complement input prefix
    remain = 2 * (6 - len(mac_items))
    rnd = ("%x" % v)[:remain]
    return value + re.sub(r"(..)", r":\1", rnd)


def secure_hash_s(data, hash_func=sha1):
    """ Return a secure hash hex digest of data. """

    digest = hash_func()
    data = to_bytes(data, errors="surrogate_or_strict")
    digest.update(data)
    return digest.hexdigest()


def md5s(data):
    if not _md5:  # pragma: no cover
        raise ValueError("MD5 not available.  Possibly running in FIPS mode")
    return secure_hash_s(data, _md5)


checksum_s = secure_hash_s


class FilterModule(object):
    """ Ansible core jinja2 filters """

    def filters(self):
        return {
            # jinja2 overrides
            "ans_groupby": do_groupby,

            # base 64
            "b64decode": b64decode,
            "b64encode": b64encode,

            # uuid
            "to_uuid": to_uuid,

            # json
            "to_json": to_json,
            "to_nice_json": to_nice_json,
            "from_json": json.loads,

            # yaml
            "to_yaml": to_yaml,
            "to_nice_yaml": to_nice_yaml,
            "from_yaml": from_yaml,
            "from_yaml_all": from_yaml_all,

            # path
            "basename": partial(unicode_wrap, os.path.basename),
            "dirname": partial(unicode_wrap, os.path.dirname),
            "expanduser": partial(unicode_wrap, os.path.expanduser),
            "expandvars": partial(unicode_wrap, os.path.expandvars),
            "realpath": partial(unicode_wrap, os.path.realpath),
            "relpath": partial(unicode_wrap, os.path.relpath),
            "splitext": partial(unicode_wrap, os.path.splitext),
            "win_basename": partial(unicode_wrap, ntpath.basename),
            "win_dirname": partial(unicode_wrap, ntpath.dirname),
            "win_splitdrive": partial(unicode_wrap, ntpath.splitdrive),

            # file glob
            "fileglob": fileglob,

            # types
            "bool": to_bool,
            "to_datetime": to_datetime,

            # date formatting
            "strftime": strftime,

            # quote string for shell usage
            "quote": quote,

            # hash filters
            # md5 hex digest of string
            "md5": md5s,
            # sha1 hex digest of string
            "sha1": checksum_s,
            # checksum of string as used by ansible for checksumming files
            "checksum": checksum_s,
            # generic hashing
            # get_encrypted_password removed due to dependencies on ansible core
            "hash": get_hash,

            # regex
            "regex_replace": regex_replace,
            "regex_escape": regex_escape,
            "regex_search": regex_search,
            "regex_findall": regex_findall,

            # ? : ;
            "ternary": ternary,

            # random stuff
            "ans_random": rand,
            "shuffle": randomize_list,

            # undefined
            "mandatory": mandatory,

            # comment-style decoration
            "comment": comment,

            # debug
            "type_debug": lambda o: o.__class__.__name__,

            # Data structures
            # The following have been removed due to
            # extensive dependencies on ansible core:
            "combine": combine,
            #   'dict2items': dict_to_list_of_dict_key_value_elements,
            #   'items2dict': list_of_dict_key_value_elements_to_dict,
            "extract": extract,
            "flatten": flatten,
            "subelements": subelements,

            # Misc
            "random_mac": random_mac,
        }
