"""
Because support for google-style docstrings wont be merged into jedi, we can do
a simple monkey patch to get the functionality here.
"""


def apply_monkey_patch_jedi():
    """
    To use, modify your vimrc to execute this code:

    Usage:
        Python2or3 << EOF
        from vimtk import jedi_monkeypatch
        jedi_monkeypatch.apply_monkey_patch_jedi()
        EOF
    """
    DEBUG = 0

    if DEBUG:
        print('Applying jedi monkey patch')

    # import os
    # ret = os.system(sys.executable + ' -m pip install xdoctest -U --user')
    # print('ret = {!r}'.format(ret))

    try:
        import jedi
    except ImportError:
        print('cannot monkey patch jedi, jedi module not found')
        return

    import re
    import sys
    import vimtk
    import ubelt as ub
    try:
        import xdoctest
        if 0:
            print('sys.executable = {!r}'.format(sys.executable))
            print('sys.prefix = {!r}'.format(sys.prefix))
            print('xdoctest = {!r}'.format(xdoctest))
            print('xdoctest.__version__ = {!r}'.format(xdoctest.__version__))
            print('xdoctest.__file__ = {!r}'.format(xdoctest.__file__))
        from xdoctest.docstr import docscrape_google
    except ImportError as ex:
        print('vimtk = {!r}'.format(vimtk))
        print('ub = {!r}'.format(ub))
        print('jedi = {!r}'.format(jedi))
        print('sys.prefix = {!r}'.format(sys.prefix))
        print('ERROR ex = {!r}'.format(ex))
        raise
    from distutils.version import LooseVersion

    acceptable_versions = [
        LooseVersion('0.10.2'),
        LooseVersion('0.11.1'),
        LooseVersion('0.12.0'),
        LooseVersion('0.13.3'),
        LooseVersion('0.14.1'),
    ]
    # min_ver = min(acceptable_versions)
    # max_ver = max(acceptable_versions)
    jedi_version = LooseVersion(jedi.__version__)

    if DEBUG:
        print('jedi.__file__ = {!r}'.format(jedi.__file__))

    if jedi_version not in acceptable_versions:
        import warnings
        warnings.warn('Monkey patching an unknown version of jedi={}. '
                      'Possible this may not work'.format(jedi_version))

    # This is the module we are going to monkey patch
    module = jedi.evaluate.docstrings

    # These are the functions we will inject into the module
    def _search_param_in_googledocstr(docstr, param_str):
        r"""
        >>> docstr = '\n'.join([
        ...     'Args:',
        ...     '    x ( ndarray ):',
        ...     '    y (int or str or list):',
        ...     '    z ({"foo", "bar", 100500}):',
        ... ])
        >>> sorted(set(_search_param_in_googledocstr(docstr, 'x')))
        ['ndarray']
        >>> sorted(set(_search_param_in_googledocstr(docstr, 'y')))
        ['int', 'list', 'str']
        >>> sorted(set(_search_param_in_googledocstr(docstr, 'z')))
        ['int', 'str']
        """
        if DEBUG:
            open(ub.expandpath('~/jedi-test.txt'), 'a').write('search google param\n')
        for garg in docscrape_google.parse_google_args(docstr):
            if garg['name'] == param_str:
                typestr = garg['type']
                for type_ in module._expand_typestr(typestr):
                    yield type_
                break

    def _search_return_in_googledocstr(docstr):
        r"""
        >>> docstr = '\n'.join([
        ...     'Returns:',
        ...     '    ndarray:',
        ...     '    int:',
        ... ])
        >>> sorted(_search_return_in_googledocstr(docstr))
        ['int', 'ndarray']
        """
        if DEBUG:
            open(ub.expandpath('~/jedi-test.txt'), 'a').write('search google ret\n')
        google_rets = list(docscrape_google.parse_google_returns(docstr))
        found = set()
        for retdict in google_rets:
            p_type = retdict['type']
            found.update(module._expand_typestr(p_type))
        return found

    def _search_param_in_docstr(docstr, param_str):
        """
        Search `docstr` for type(-s) of `param_str`.
        >>> _search_param_in_docstr(':type param: int', 'param')
        ['int']
        >>> _search_param_in_docstr('@type param: int', 'param')
        ['int']
        >>> _search_param_in_docstr(
        ...   ':type param: :class:`threading.Thread`', 'param')
        ['threading.Thread']
        >>> bool(_search_param_in_docstr('no document', 'param'))
        False
        >>> _search_param_in_docstr(':param int param: some description', 'param')
        ['int']
        """
        if DEBUG:
            open(ub.expandpath('~/jedi-test.txt'), 'a').write('search param\n')
        # look at #40 to see definitions of those params
        patterns = [re.compile(p % re.escape(param_str))
                    for p in module.DOCSTRING_PARAM_PATTERNS]
        for pattern in patterns:
            match = pattern.search(docstr)
            if match:
                return [module._strip_rst_role(match.group(1))]

        return (module._search_param_in_numpydocstr(docstr, param_str) or
                list(_search_param_in_googledocstr(docstr, param_str)))

    # NOTE: WE ARE INJECTING OUR GOOGLE RETURN DOCSTRING IN THE NUMPY PARSER
    # BECAUSE infer_return_types IS AN INTERNAL FUNCTION :(

    def _search_return_in_numpydocstr(docstr):
        """
        Search `docstr` (in numpydoc format) for type(-s) of function returns.
        """
        if DEBUG:
            open(ub.expandpath('~/jedi-test.txt'), 'a').write('search return\n')
        try:
            doc = module._get_numpy_doc_string_cls()(docstr)
        except ImportError:
            return
        try:
            # This is a non-public API. If it ever changes we should be
            # prepared and return gracefully.
            returns = doc._parsed_data['Returns']
            returns += doc._parsed_data['Yields']
        except (KeyError, AttributeError):
            return
        for r_name, r_type, r_descr in returns:
            # Return names are optional and if so the type is in the name
            if not r_type:
                r_type = r_name
            for type_ in module._expand_typestr(r_type):
                yield type_

        # Injected code:
        # Check for google style return hint
        for type_ in _search_return_in_googledocstr(docstr):
            yield type_

    # def infer_return_types(function_context):
    #     def search_return_in_docstr(code):
    #         for p in module.DOCSTRING_RETURN_PATTERNS:
    #             match = p.search(code)
    #             if match:
    #                 yield module._strip_rst_role(match.group(1))
    #         # Check for numpy style return hint
    #         for type_ in module._search_return_in_numpydocstr(code):
    #             yield type_

    #         # Check for google style return hint
    #         for type_ in _search_return_in_googledocstr(code):
    #             yield type_

    #     for type_str in search_return_in_docstr(function_context.py__doc__()):
    #         for type_eval in module._evaluate_for_statement_string(function_context.get_root_context(), type_str):
    #             yield type_eval

    module._search_param_in_docstr = _search_param_in_docstr
    module._search_return_in_numpydocstr = _search_return_in_numpydocstr
