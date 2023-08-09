__metaclass__ = type

from collections.abc import (MutableMapping, MutableSequence)
from jinja2_ansible_filters.module_utils import (to_native)

from jinja2.exceptions import FilterArgumentError


def recursive_check_defined(item):
    from jinja2.runtime import Undefined

    if isinstance(item, MutableMapping):
        for key in item:
            recursive_check_defined(item[key])
    elif isinstance(item, list):
        for i in item:
            recursive_check_defined(i)
    else:
        if isinstance(item, Undefined):
            raise FilterArgumentError("{0} is undefined".format(item))


def _obj_to_text(x):
    return [o.text for o in x]


def _obj_to_raw(x):
    return [o.raw for o in x]


def _obj_to_block(objects, visited=None):
    items = list()
    for o in objects:
        if o not in items:
            items.append(o)
            for child in o._children:
                if child not in items:
                    items.append(child)
    return _obj_to_raw(items)


def dumps(objects, output='block', comments=False):
    if output == 'block':
        items = _obj_to_block(objects)
    elif output == 'commands':
        items = _obj_to_text(objects)
    elif output == 'raw':
        items = _obj_to_raw(objects)
    else:
        raise TypeError('unknown value supplied for keyword output')

    if output == 'block':
        if comments:
            for index, item in enumerate(items):
                nextitem = index + 1
                if nextitem < len(items) and not item.startswith(' ') \
                        and items[nextitem].startswith(' '):
                    item = '!\n%s' % item
                items[index] = item
            items.append('!')
        items.append('end')

    return '\n'.join(items)


def _validate_mutable_mappings(a, b):
    """
    Internal convenience function to ensure arguments are MutableMappings
    This checks that all arguments are MutableMappings or raises an error
    :raises AnsibleError: if one of the arguments is not a MutableMapping
    """

    # If this becomes generally needed, change the signature to operate on
    # a variable number of arguments instead.

    if not (isinstance(a, MutableMapping) and isinstance(b, MutableMapping)):
        myvars = []
        for x in [a, b]:
            try:
                myvars.append(dumps(x))
            except Exception:
                myvars.append(to_native(x))
        raise FilterArgumentError(
            "failed to combine variables, expected "
            + "dicts but got a '{0}' and a '{1}': \n{2}\n{3}".format(
                a.__class__.__name__,
                b.__class__.__name__, myvars[0], myvars[1])
        )


def merge_hash(x, y, recursive=True, list_merge='replace'):
    """
    Return a new dictionary result of the merges of y into x,
    so that keys from y take precedence over keys from x.
    (x and y aren't modified)
    """
    if list_merge not in ('replace', 'keep', 'append',
                          'prepend', 'append_rp', 'prepend_rp'):
        raise FilterArgumentError(
            "merge_hash: 'list_merge' argument can only be equal to 'replace',"
            " 'keep', 'append', 'prepend', 'append_rp' or 'prepend_rp'")

    # verify x & y are dicts
    _validate_mutable_mappings(x, y)

    # to speed things up: if x is empty or equal to y, return y
    # (this `if` can be remove without impact on the function
    #  except performance)
    if x == {} or x == y:
        return y.copy()

    # in the following we will copy elements from y to x, but
    # we don't want to modify x, so we create a copy of it
    x = x.copy()

    # to speed things up: use dict.update if possible
    # (this `if` can be remove without impact on the function
    #  except performance)
    if not recursive and list_merge == 'replace':
        x.update(y)
        return x

    # insert each element of y in x, overriding the one in x
    # (as y has higher priority)
    # we copy elements from y to x instead of x to y because
    # there is a high probability x will be the "default" dict the user
    # want to "patch" with y
    # therefore x will have much more elements than y

    for key, y_value in y.items():
        # if `key` isn't in x
        # update x and move on to the next element of y
        if key not in x:
            x[key] = y_value
            continue
        # from this point we know `key` is in x

        x_value = x[key]

        # if both x's element and y's element are dicts
        # recursively "combine" them or override x's with y's element
        # depending on the `recursive` argument
        # and move on to the next element of y
        if isinstance(x_value, MutableMapping) \
                and isinstance(y_value, MutableMapping):
            if recursive:
                x[key] = merge_hash(x_value, y_value, recursive, list_merge)
            else:
                x[key] = y_value
            continue

        # if both x's element and y's element are lists
        # "merge" them depending on the `list_merge` argument
        # and move on to the next element of y
        if isinstance(x_value, MutableSequence) and \
                isinstance(y_value, MutableSequence):
            if list_merge == 'replace':
                # replace x value by y's one as it has higher priority
                x[key] = y_value
            elif list_merge == 'append':
                x[key] = x_value + y_value
            elif list_merge == 'prepend':
                x[key] = y_value + x_value
            elif list_merge == 'append_rp':
                # append all elements from
                # y_value (high prio)
                # to x_value (low prio)
                # and remove x_value elements that are also in y_value
                # we don't remove elements from
                # x_value nor y_value that were already in double
                # (we assume that there is a reason if
                # there where such double elements)
                # _rp stands for "remove present"
                x[key] = [z for z in x_value if z not in y_value] + y_value
            elif list_merge == 'prepend_rp':
                # same as 'append_rp' but y_value elements are prepend
                x[key] = y_value + [z for z in x_value if z not in y_value]

            # else 'keep'
            #   keep x value even if y it's of higher priority
            #   it's done by not changing x[key]
            continue

        # else just override x's element with y's one
        x[key] = y_value

    return x
