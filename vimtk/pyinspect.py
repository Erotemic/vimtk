"""
TODO: use the closer to ensure these functions are synced with xdoctest
"""
import ubelt as ub
import ast
import os
import six


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
        modpath = ub.modname_to_modpath(modname)
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
        >>> fpath = pyinspect.__file__.replace('.pyc', '.py')
        >>> sourcecode = ub.readfrom(fpath)
        >>> func_names = parse_import_names(sourcecode)
        >>> result = ('func_names = %s' % (ub.repr2(func_names),))
        >>> print(result)
    """
    import_names = []
    if six.PY2:
        sourcecode = ub.ensure_unicode(sourcecode)
        encoded = sourcecode.encode('utf8')
        pt = ast.parse(encoded)
    else:
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
                        modparts = ub.split_modpath(os.path.abspath(fpath))[1].replace('\\', '/').split('/')
                        parts = modparts[:-node.level]
                        # parts = os.path.split(ub.split_modpath(os.path.abspath(fpath))[1])[:-node.level]
                        prefix = '.'.join(parts) + '.'
                        # prefix = '.'.join(os.path.split(fpath)[-node.level:]) + '.'
                    else:
                        prefix = '.' * node.level
                # modules.append(node.level * '.' + node.module + '.' + alias.name)
                # modules.append(prefix + node.module + '.' + alias.name)
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
        >>> fpath = pyinspect.__file__.replace('.pyc', '.py')
        >>> sourcecode = ub.readfrom(fpath)
        >>> func_names = parse_function_names(sourcecode)
        >>> result = ('func_names = %s' % (ub.repr2(func_names),))
        >>> print(result)
    """
    func_names = []
    if six.PY2:
        sourcecode = ub.ensure_unicode(sourcecode)
        encoded = sourcecode.encode('utf8')
        pt = ast.parse(encoded)
    else:
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
            # if ignore_conditional:
            #     return
            # Ignore the main statement
            # print('----')
            # print('node.test = {!r}'.format(node.test))
            # print('node.orelse = {!r}'.format(node.orelse))
            if _node_is_main_if(node):
                return

            # if isinstance(node.orelse, ast.If):
            #     # THIS IS AN ELIF
            #     self.condition_id += 1
            #     self.in_condition_chain = True
            #     ast.NodeVisitor.generic_visit(self, node)
            #     self.in_condition_chain = False
            #     pass
            # # TODO: where does else get parsed exactly?

            # Reset the set of conditionals
            # self.condition_id = 0
            # self.condition_names = ub.ddict(list)

            # self.in_condition_chain = True
            ast.NodeVisitor.generic_visit(self, node)
            # self.in_condition_chain = False

            # if False:
            #     # IF THIS WAS AN ELSE:
            #     if self.condition_names is not None:
            #         # anything defined in all conditions is kosher
            #         from six.moves import reduce
            #         common_names = reduce(set.intersection,
            #                               map(set, self.condition_names.values()))
            #         self.func_names.extend(common_names)
            #         self.condition_names = None

        def visit_FunctionDef(self, node):
            # if self.in_condition_chain and self.condition_names is not None:
            #     # dont immediately add things in conditions. Wait until we can
            #     # ensure which definitions are common in all conditions.
            #     self.condition_names[self.condition_id].append(node.name)
            # else:
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
