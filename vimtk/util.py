"""
Autogen:
    # Autogenerated from ubelt (via liberator) on 2024-04-26T124620-5
    python3 /home/joncrall/code/vimtk/dev/autogen_utils.py
    python3 ../dev/autogen_utils.py
"""

import itertools as it
import os
import sys
from collections import OrderedDict, defaultdict
from os.path import (abspath, basename, dirname, exists, expanduser,
                     expandvars, isdir, isfile, join, normpath, realpath,
                     relpath, split, splitext)


def expandpath(path):
    path = expanduser(path)
    path = expandvars(path)
    return path


def shrinkuser(path, home="~"):
    path = normpath(path)
    userhome_dpath = userhome()
    if path.startswith(userhome_dpath):
        if len(path) == len(userhome_dpath):
            path = home
        elif path[len(userhome_dpath)] == os.path.sep:
            path = home + path[len(userhome_dpath) :]
    return path


def userhome(username=None):
    if username is None:
        if "HOME" in os.environ:
            userhome_dpath = os.environ["HOME"]
        else:
            if sys.platform.startswith("win32"):
                if "USERPROFILE" in os.environ:
                    userhome_dpath = os.environ["USERPROFILE"]
                elif "HOMEPATH" in os.environ:
                    drive = os.environ.get("HOMEDRIVE", "")
                    userhome_dpath = join(drive, os.environ["HOMEPATH"])
                else:
                    raise OSError("Cannot determine the user's home directory")
            else:
                import pwd

                userhome_dpath = pwd.getpwuid(os.getuid()).pw_dir
    else:
        if sys.platform.startswith("win32"):
            c_users = dirname(userhome())
            userhome_dpath = join(c_users, username)
            if not exists(userhome_dpath):
                raise KeyError("Unknown user: {}".format(username))
        else:
            import pwd

            try:
                pwent = pwd.getpwnam(username)
            except KeyError:
                raise KeyError("Unknown user: {}".format(username))
            userhome_dpath = pwent.pw_dir
    return userhome_dpath


def dict_diff(*args):
    if not args:
        return {}
    else:
        first_dict = args[0]
        dictclass = OrderedDict if isinstance(first_dict, OrderedDict) else dict
        remove_keys = set.union(*map(set, args[1:]))
        new = dictclass((k, first_dict[k]) for k in first_dict.keys() if k not in remove_keys)
        return new


def dict_union(*args):
    if not args:
        return {}
    else:
        dictclass = OrderedDict if isinstance(args[0], OrderedDict) else dict
        return dictclass(it.chain.from_iterable(d.items() for d in args))


def ensure_unicode(text):
    if isinstance(text, str):
        return text
    elif isinstance(text, bytes):
        return text.decode("utf8")
    else:
        raise ValueError("unknown input type {!r}".format(text))


def indent(text, prefix="    "):
    return prefix + text.replace("\n", "\n" + prefix)


def codeblock(text):
    import textwrap

    return textwrap.dedent(text).strip("\n")


def group_items(items, key):
    if callable(key):
        keyfunc = key
        pair_list = ((keyfunc(item), item) for item in items)
    else:
        pair_list = zip(key, items)
    id_to_items = defaultdict(list)
    for key, item in pair_list:
        id_to_items[key].append(item)
    return id_to_items


def split_modpath(modpath, check=True):
    modpath_ = abspath(expanduser(modpath))
    if check:
        if not exists(modpath_):
            if not exists(modpath):
                raise ValueError("modpath={} does not exist".format(modpath))
            raise ValueError("modpath={} is not a module".format(modpath))
        if isdir(modpath_) and not exists(join(modpath, "__init__.py")):
            raise ValueError("modpath={} is not a module".format(modpath))
    full_dpath, fname_ext = split(modpath_)
    _relmod_parts = [fname_ext]
    dpath = full_dpath
    while exists(join(dpath, "__init__.py")):
        dpath, dname = split(dpath)
        _relmod_parts.append(dname)
    relmod_parts = _relmod_parts[::-1]
    rel_modpath = os.path.sep.join(relmod_parts)
    return dpath, rel_modpath


def modpath_to_modname(
    modpath, hide_init=True, hide_main=False, check=True, relativeto=None
):
    if check and relativeto is None:
        if not exists(modpath):
            raise ValueError("modpath={} does not exist".format(modpath))
    modpath_ = abspath(expanduser(modpath))
    modpath_ = normalize_modpath(modpath_, hide_init=hide_init, hide_main=hide_main)
    if relativeto:
        dpath = dirname(abspath(expanduser(relativeto)))
        rel_modpath = relpath(modpath_, dpath)
    else:
        dpath, rel_modpath = split_modpath(modpath_, check=check)
    modname = splitext(rel_modpath)[0]
    if "." in modname:
        modname, abi_tag = modname.split(".", 1)
    modname = modname.replace("/", ".")
    modname = modname.replace("\\", ".")
    return modname


IS_PY_GE_308 = (sys.version_info[0] >= 3) and (sys.version_info[1] >= 8)


def _parse_static_node_value(node):
    import ast
    import numbers
    from collections import OrderedDict

    if (
        isinstance(node, ast.Constant) and isinstance(node.value, numbers.Number)
        if IS_PY_GE_308
        else isinstance(node, ast.Num)
    ):
        value = node.value if IS_PY_GE_308 else node.n
    elif (
        isinstance(node, ast.Constant) and isinstance(node.value, str)
        if IS_PY_GE_308
        else isinstance(node, ast.Str)
    ):
        value = node.value if IS_PY_GE_308 else node.s
    elif isinstance(node, ast.List):
        value = list(map(_parse_static_node_value, node.elts))
    elif isinstance(node, ast.Tuple):
        value = tuple(map(_parse_static_node_value, node.elts))
    elif isinstance(node, (ast.Dict)):
        keys = map(_parse_static_node_value, node.keys)
        values = map(_parse_static_node_value, node.values)
        value = OrderedDict(zip(keys, values))
    elif isinstance(node, (ast.NameConstant)):
        value = node.value
    else:
        print(node.__dict__)
        raise TypeError(
            "Cannot parse a static value from non-static node "
            "of type: {!r}".format(type(node))
        )
    return value


def _extension_module_tags():
    import sysconfig

    tags = []
    tags.append(sysconfig.get_config_var("SOABI"))
    tags.append("abi3")
    tags = [t for t in tags if t]
    return tags


def _static_parse(varname, fpath):
    import ast

    if not exists(fpath):
        raise ValueError("fpath={!r} does not exist".format(fpath))
    with open(fpath, "r") as file_:
        sourcecode = file_.read()
    pt = ast.parse(sourcecode)

    class StaticVisitor(ast.NodeVisitor):
        def visit_Assign(self, node):
            for target in node.targets:
                if getattr(target, "id", None) == varname:
                    self.static_value = _parse_static_node_value(node.value)

    visitor = StaticVisitor()
    visitor.visit(pt)
    try:
        value = visitor.static_value
    except AttributeError:
        value = "Unknown {}".format(varname)
        raise AttributeError(value)
    return value


def _platform_pylib_exts():
    import sysconfig

    valid_exts = []
    base_ext = "." + sysconfig.get_config_var("EXT_SUFFIX").split(".")[-1]
    for tag in _extension_module_tags():
        valid_exts.append("." + tag + base_ext)
    valid_exts.append(base_ext)
    return tuple(valid_exts)


def normalize_modpath(modpath, hide_init=True, hide_main=False):
    if hide_init:
        if basename(modpath) == "__init__.py":
            modpath = dirname(modpath)
            hide_main = True
    else:
        modpath_with_init = join(modpath, "__init__.py")
        if exists(modpath_with_init):
            modpath = modpath_with_init
    if hide_main:
        if basename(modpath) == "__main__.py":
            parallel_init = join(dirname(modpath), "__init__.py")
            if exists(parallel_init):
                modpath = dirname(modpath)
    return modpath


def _syspath_modname_to_modpath(modname, sys_path=None, exclude=None):
    import glob

    def _isvalid(modpath, base):
        subdir = dirname(modpath)
        while subdir and subdir != base:
            if not exists(join(subdir, "__init__.py")):
                return False
            subdir = dirname(subdir)
        return True

    _fname_we = modname.replace(".", os.path.sep)
    candidate_fnames = [
        _fname_we + ".py",
    ]
    candidate_fnames += [_fname_we + ext for ext in _platform_pylib_exts()]
    if sys_path is None:
        sys_path = sys.path
    candidate_dpaths = ["." if p == "" else p for p in sys_path]
    if exclude:

        def normalize(p):
            if sys.platform.startswith("win32"):
                return realpath(p).lower()
            else:
                return realpath(p)

        real_exclude = {normalize(p) for p in exclude}
        candidate_dpaths = [
            p for p in candidate_dpaths if normalize(p) not in real_exclude
        ]

    def check_dpath(dpath):
        modpath = join(dpath, _fname_we)
        if exists(modpath):
            if isfile(join(modpath, "__init__.py")):
                if _isvalid(modpath, dpath):
                    return modpath
        for fname in candidate_fnames:
            modpath = join(dpath, fname)
            if isfile(modpath):
                if _isvalid(modpath, dpath):
                    return modpath

    _pkg_name = _fname_we.split(os.path.sep)[0]
    _pkg_name_hypen = _pkg_name.replace("_", "-")
    _egglink_fname1 = _pkg_name + ".egg-link"
    _egglink_fname2 = _pkg_name_hypen + ".egg-link"
    _editable_fname_pth_pat = "__editable__." + _pkg_name + "-*.pth"
    _editable_fname_finder_py_pat = "__editable___*_*finder.py"
    found_modpath = None
    for dpath in candidate_dpaths:
        modpath = check_dpath(dpath)
        if modpath:
            found_modpath = modpath
            break
        new_editable_finder_paths = sorted(
            glob.glob(join(dpath, _editable_fname_finder_py_pat))
        )
        if new_editable_finder_paths:
            for finder_fpath in new_editable_finder_paths:
                mapping = _static_parse("MAPPING", finder_fpath)
                try:
                    target = dirname(mapping[_pkg_name])
                except KeyError:
                    ...
                else:
                    if not exclude or normalize(target) not in real_exclude:
                        modpath = check_dpath(target)
                        if modpath:
                            found_modpath = modpath
                            break
            if found_modpath is not None:
                break
        new_editable_pth_paths = sorted(glob.glob(join(dpath, _editable_fname_pth_pat)))
        if new_editable_pth_paths:
            import pathlib

            for editable_pth in new_editable_pth_paths:
                editable_pth = pathlib.Path(editable_pth)
                target = editable_pth.read_text().strip().split("\n")[-1]
                if not exclude or normalize(target) not in real_exclude:
                    modpath = check_dpath(target)
                    if modpath:
                        found_modpath = modpath
                        break
            if found_modpath is not None:
                break
        linkpath1 = join(dpath, _egglink_fname1)
        linkpath2 = join(dpath, _egglink_fname2)
        linkpath = None
        if isfile(linkpath1):
            linkpath = linkpath1
        elif isfile(linkpath2):
            linkpath = linkpath2
        if linkpath is not None:
            with open(linkpath, "r") as file:
                target = file.readline().strip()
            if not exclude or normalize(target) not in real_exclude:
                modpath = check_dpath(target)
                if modpath:
                    found_modpath = modpath
                    break
    return found_modpath


def modname_to_modpath(modname, hide_init=True, hide_main=False, sys_path=None):
    modpath = _syspath_modname_to_modpath(modname, sys_path)
    if modpath is None:
        return None
    modpath = normalize_modpath(modpath, hide_init=hide_init, hide_main=hide_main)
    return modpath


WIN32 = sys.platform == "win32"  # type: bool
