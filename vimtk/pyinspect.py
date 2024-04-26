"""
TODO: use the closer to ensure these functions are synced with xdoctest
"""
import ast
import os
from vimtk.util import split_modpath, modname_to_modpath


def check_module_installed(modname):
    """
    Check if a python module is installed without attempting to import it.
    Note, that if ``modname`` indicates a child module, the parent module is
    always loaded.

    Args:
        modname (str):  module name

    Returns:
        bool: found

    References:
        http://stackoverflow.com/questions/14050281/module-exists-without-importing

    Example:
        >>> import sys
        >>> import ubelt as ub
        >>> modname = ub.argval('--modname', default='this')
        >>> is_installed = check_module_installed(modname)
        >>> is_imported = modname in sys.modules
        >>> print('module(%r).is_installed = %r' % (modname, is_installed))
        >>> print('module(%r).is_imported = %r' % (modname, is_imported))
        >>> assert 'this' not in sys.modules, 'module(this) should not have ever been imported'
    """
    import pkgutil
    if '.' in modname:
        # Prevent explicit import if possible
        parts = modname.split('.')
        base = parts[0]
        submods = parts[1:]
        loader = pkgutil.find_loader(base)
        if loader is not None:
            # TODO: check to see if path to the submod exists
            submods
            return True
    loader = pkgutil.find_loader(modname)
    is_installed = loader is not None
    return is_installed


def in_pythonpath(modname):
    try:
        flag = check_module_installed(modname)
    except Exception:
        flag = False
    if flag:
        modpath = modname_to_modpath(modname)
        if modpath is None:
            flag = False
    return flag


def parse_import_names(sourcecode, top_level=True, fpath=None, branch=False):
    """
    Finds all function names in a file without importing it

    Args:
        sourcecode (str):

    Returns:
        list: func_names

    References:
        https://stackoverflow.com/questions/20445733/how-to-tell-which-modules-have-been-imported-in-some-source-code

    Example:
        >>> from vimtk import pyinspect
        >>> import pathlib
        >>> fpath = pathlib.Path(pyinspect.__file__.replace('.pyc', '.py'))
        >>> sourcecode = fpath.read_text()
        >>> func_names = parse_import_names(sourcecode)
        >>> result = (f'func_names = {func_names}')
        >>> print(result)
    """
    import_names = []
    pt = ast.parse(sourcecode)
    modules = []

    class ImportVisitor(ast.NodeVisitor):

        def _parse_alias_list(self, aliases):
            for alias in aliases:
                if alias.asname is not None:
                    import_names.append(alias.asname)
                else:
                    if '.' not in alias.name:
                        import_names.append(alias.name)

        def visit_Import(self, node):
            self._parse_alias_list(node.names)
            self.generic_visit(node)

            for alias in node.names:
                modules.append(alias.name)

        def visit_ImportFrom(self, node):
            self._parse_alias_list(node.names)
            self.generic_visit(node)

            for alias in node.names:
                prefix = ''
                if node.level:
                    if fpath is not None:
                        modparts = split_modpath(os.path.abspath(fpath))[1].replace('\\', '/').split('/')
                        parts = modparts[:-node.level]
                        prefix = '.'.join(parts) + '.'
                    else:
                        prefix = '.' * node.level
                modules.append(prefix + node.module)

        def visit_FunctionDef(self, node):
            # Ignore modules imported in functions
            if not top_level:
                self.generic_visit(node)
                # ast.NodeVisitor.generic_visit(self, node)

        def visit_ClassDef(self, node):
            if not top_level:
                self.generic_visit(node)
                # ast.NodeVisitor.generic_visit(self, node)

        def visit_If(self, node):
            if not branch:
                # TODO: determine how to figure out if a name is in all branches
                if not _node_is_main_if(node):
                    # Ignore the main statement
                    self.generic_visit(node)
    try:
        ImportVisitor().visit(pt)
    except Exception:
        pass
    return import_names, modules


def _node_is_main_if(node):
    if isinstance(node.test, ast.Compare):
        try:
            if all([
                isinstance(node.test.ops[0], ast.Eq),
                node.test.left.id == '__name__',
                node.test.comparators[0].s == '__main__',
            ]):
                return True
        except Exception:
            pass
    return False


def parse_function_names(sourcecode, top_level=True, ignore_condition=1):
    """
    Finds all function names in a file without importing it

    Args:
        sourcecode (str):

    Returns:
        list: func_names

    Example:
        >>> from vimtk import pyinspect
        >>> import ubelt as ub
        >>> fpath = pyinspect.__file__.replace('.pyc', '.py')
        >>> sourcecode = ub.readfrom(fpath)
        >>> func_names = parse_function_names(sourcecode)
        >>> result = (f'func_names = {func_names}')
        >>> print(result)
    """
    func_names = []
    pt = ast.parse(sourcecode)

    class FuncVisitor(ast.NodeVisitor):

        def __init__(self):
            super(FuncVisitor, self).__init__()
            self.condition_names = None
            self.condition_id = -9001
            self.in_condition_chain = False

        def visit_If(self, node):
            if ignore_condition:
                return
            if _node_is_main_if(node):
                return
            ast.NodeVisitor.generic_visit(self, node)

        def visit_FunctionDef(self, node):
            func_names.append(node.name)
            if not top_level:
                ast.NodeVisitor.generic_visit(self, node)

        def visit_ClassDef(self, node):
            if not top_level:
                ast.NodeVisitor.generic_visit(self, node)
    try:
        FuncVisitor().visit(pt)
    except Exception:
        raise
    return func_names
