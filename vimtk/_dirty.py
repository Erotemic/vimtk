"""
This is a module for quick and dirty ports from other codebases that I'd like
to include, but need to be cleaned up and integrated into vimtk properly.

This is a staging ground where I can use them, but also keep them separate.


Port Logic
----------
# Liberator makes porting dirty code pretty easy

import liberator
import utool as ut

lib = liberator.Liberator()
lib.add_dynamic(ut.format_multiple_paragraph_sentences)
lib.expand(['utool'])
source = lib.current_sourcecode()
print(source)


lib = liberator.Liberator()
lib.add_dynamic(ut.remove_doublspaces)
lib.add_dynamic(ut.flatten_textlines)
lib.add_dynamic(ut.get_minimum_indentation)
lib.add_dynamic(ut.regex_or)
lib.add_dynamic(ut.interleave)
lib.expand(['utool'])
source = lib.current_sourcecode()
print(source)

"""
import re
import ubelt as ub


def regex_reconstruct_split(pattern, text):
    separators = [match.group() for match in re.finditer(pattern, text)]
    remaining = text
    block_list = []
    for sep in separators:
        head, tail = remaining.split(sep, 1)
        block_list.append(head)
        remaining = tail
    block_list.append(remaining)
    return block_list, separators


def msgblock(key, text, side='|'):
    """ puts text inside a visual ascii block """
    blocked_text = ''.join(
        [' + --- ', key, ' ---\n'] +
        [' ' + side + ' ' + line + '\n' for line in text.split('\n')] +
        [' L ___ ', key, ' ___\n']
    )
    return blocked_text


def get_indentation(line_):
    """
    returns the number of preceding spaces
    """
    return len(line_) - len(line_.lstrip())


def get_minimum_indentation(text):
    r"""
    returns the number of preceding spaces

    Args:
        text (str): unicode text

    Returns:
        int: indentation

    Example:
        >>> # ENABLE_DOCTEST
        >>> text = '    foo\n   bar'
        >>> result = get_minimum_indentation(text)
        >>> print(result)
        3
    """
    lines = text.split('\n')
    indentations = [get_indentation(line_)
                    for line_ in lines  if len(line_.strip()) > 0]
    if len(indentations) == 0:
        return 0
    return min(indentations)


def interleave(args):
    r"""
    zip followed by flatten

    Args:
        args (tuple): tuple of lists to interleave

    Example:
        >>> args = ([1, 2, 3, 4, 5], ['A', 'B', 'C', 'D', 'E', 'F', 'G'])
        >>> genresult = interleave(args)
        >>> result = ub.repr2(list(genresult), nl=False)
        >>> print(result)
        [1, 'A', 2, 'B', 3, 'C', 4, 'D', 5, 'E']
    """
    import itertools as it
    arg_iters = list(map(iter, args))
    cycle_iter = it.cycle(arg_iters)
    for iter_ in cycle_iter:
        try:
            yield next(iter_)
        except StopIteration:
            return


def colorprint(text, color):
    print(ub.color_text(text, color))


def format_single_paragraph_sentences(text, debug=False, myprefix=True,
                                      sentence_break=True, max_width=73,
                                      sepcolon=True):
    r"""
    helps me separatate sentences grouped in paragraphs that I have a
    difficult time reading due to dyslexia

    Args:
        text (str):

    Returns:
        str: wrapped_text

    Example:
        >>> # DISABLE_DOCTEST
        >>> text = '     lorium ipsum doloar dolar dolar dolar erata man foobar is this there yet almost man not quit ate 80 chars yet hold out almost there? dolar erat. sau.ltum. fds.fd... . . fd oob fd. list: (1) abcd, (2) foobar (4) 123456789 123456789 123456789 123456789 123 123 123 123 123456789 123 123 123 123 123456789 123456789 123456789 123456789 123456789 123 123 123 123 123 123456789 123456789 123456789 123456789 123456789 123456789 (3) spam.'
        >>> #text = 'list: (1) abcd, (2) foobar (3) spam.'
        >>> #text = 'foo. when: (1) there is a new individual,'
        >>> #text = 'when: (1) there is a new individual,'
        >>> #text = '? ? . lorium. ipsum? dolar erat. saultum. fds.fd...  fd oob fd. ? '  # causes breakdown
        >>> print('text = %r' % (text,))
        >>> sentence_break = not ub.argflag('--nobreak')
        >>> wrapped_text = format_single_paragraph_sentences(text, debug=True, sentence_break=sentence_break)
        >>> result = ('wrapped_text =\n%s' % (str(wrapped_text),))
        >>> print(result)
    """
    import textwrap
    import re
    min_indent = get_minimum_indentation(text)
    min_indent = (min_indent // 4) * 4
    if debug:
        print(colorprint(msgblock('preflat', repr(text)), 'darkyellow'))

    def remove_doublspaces(text):
        new_text = text
        new_text = re.sub('  *', ' ', new_text)
        return new_text

    def flatten_textlines(text):
        new_text = text
        new_text = re.sub(' *\n *', ' ', new_text, flags=re.MULTILINE).strip(' ')
        return new_text

    text_ = remove_doublspaces(text)
    # TODO: more intelligent sentence parsing
    text_ = flatten_textlines(text)
    if debug:
        print(colorprint(msgblock('postflat', repr(text_)), 'yellow'))

    raw_sep_chars = ['.', '?', '!', ':']
    if not sepcolon:
        raw_sep_chars.remove(':')

    def split_sentences(text_):

        def regex_or(list_):
            return '(' + '|'.join(list_) + ')'
        # TODO: rectify with split_sentences2
        # SPLITS line endings based on regular expressions.
        esc = re.escape
        # Define separation patterns
        regex_sep_chars = list(map(re.escape, raw_sep_chars))
        regex_sep_prefix = [esc('(') + r'\d' + esc(')')]
        regex_sep_list = regex_sep_chars + regex_sep_prefix
        # Combine into a full regex
        sep_pattern = regex_or(regex_sep_list)
        full_pattern = '(' + sep_pattern + r'+\s)'
        full_regex = re.compile(full_pattern)
        # Make the splits
        num_groups = full_regex.groups  # num groups in the regex
        split_list = re.split(full_pattern, text_)
        if len(split_list) > 0:
            num_bins = num_groups + 1
            sentence_list = split_list[0::num_bins]
            sep_list_group1 = split_list[1::num_bins]
            sep_list = sep_list_group1
        if debug:
            print('<SPLIT DBG>')
            print('num_groups = %r' % (num_groups,))
            print('len(split_list) = %r' % (len(split_list)))
            print('len(split_list) / len(sentence_list) = %r' % (
                len(split_list) / len(sentence_list)))
            print('len(sentence_list) = %r' % (len(sentence_list),))
            print('len(sep_list_group1) = %r' % (len(sep_list_group1),))
            #print('len(sep_list_group2) = %r' % (len(sep_list_group2),))
            print('full_pattern = %s' % (full_pattern,))
            #print('split_list = %r' % (split_list,))
            print('sentence_list = %s' % (ub.repr2(sentence_list),))
            print('sep_list = %s' % ((sep_list),))
            print('</SPLIT DBG>')
        return sentence_list, sep_list

    def wrap_sentences(sentence_list, min_indent, max_width):
        # prefix for continuations of a sentence
        if myprefix:
            # helps me read LaTeX
            sentence_prefix = '  '
        else:
            sentence_prefix = ''
        if text_.startswith('>>>'):
            # Hack to do docstrings
            # TODO: make actualy docstring reformater
            sentence_prefix = '...     '

        if max_width is not None:
            width = max_width - min_indent - len(sentence_prefix)

            wrapkw = dict(width=width, break_on_hyphens=False, break_long_words=False)
            #wrapped_lines_list = [textwrap.wrap(sentence_prefix + line, **wrapkw)
            #                      for line in sentence_list]
            wrapped_lines_list = []
            for count, line in enumerate(sentence_list):
                wrapped_lines = textwrap.wrap(line, **wrapkw)
                wrapped_lines = [line_ if count == 0 else sentence_prefix + line_
                                 for count, line_ in enumerate(wrapped_lines)]
                wrapped_lines_list.append(wrapped_lines)

            wrapped_sentences = ['\n'.join(line) for line in wrapped_lines_list]
        else:
            wrapped_sentences = sentence_list[:]
        return wrapped_sentences

    def rewrap_sentences2(sentence_list, sep_list):
        # FIXME: probably where nl error is
        # ******* #
        # put the newline before or after the sep depending on if it is
        # supposed to prefix or suffix the sentence.
        from six.moves import zip_longest
        # FIXME: Place the separators either before or after a sentence
        sentence_list2 = ['']
        _iter = zip_longest(sentence_list, sep_list)
        for count, (sentence, sep) in enumerate(_iter):
            if sep is None:
                sentence_list2[-1] += sentence
                continue
            sepchars = sep.strip()
            if len(sepchars) > 0 and sepchars[0] in raw_sep_chars:
                sentence_list2[-1] += sentence + (sep.strip())
                sentence_list2.append('')
            else:
                # Place before next
                sentence_list2[-1] += sentence
                sentence_list2.append(sep)
        sentence_list2 = [x.strip() for x in sentence_list2 if len(x.strip()) > 0]
        return sentence_list2

    # New way
    #print('last_is_nl = %r' % (last_is_nl,))
    if sentence_break:
        # Break at sentences
        sentence_list, sep_list = split_sentences(text_)
        # FIXME: probably where nl error is
        sentence_list2 = rewrap_sentences2(sentence_list, sep_list)
        wrapped_sentences = wrap_sentences(sentence_list2, min_indent, max_width)
        wrapped_block = '\n'.join(wrapped_sentences)
    else:
        # Break anywhere
        width = max_width - min_indent
        wrapkw = dict(width=width, break_on_hyphens=False,
                      break_long_words=False)
        wrapped_block = '\n'.join(textwrap.wrap(text_, **wrapkw))

    # HACK for last nl (seems to only happen if nl follows a seperator)
    last_is_nl = text.endswith('\n') and  not wrapped_block.endswith('\n')
    first_is_nl = len(text) > 1 and text.startswith('\n') and not wrapped_block.startswith('\n')
    # if last_is_nl and wrapped_block.strip().endswith('.'):
    if last_is_nl:
        wrapped_block += '\n'
    if first_is_nl:
        wrapped_block = '\n' + wrapped_block
    # Do the final indentation
    wrapped_text = ub.indent(wrapped_block, ' ' * min_indent)
    return wrapped_text


def format_multiple_paragraph_sentences(text, debug=False, **kwargs):
    """
    FIXME: funky things happen when multiple newlines in the middle of
    paragraphs

    Example:
        >>> text = ub.codeblock(
            '''
            Test paragraph.
            Far out in the uncharted backwaters of the unfashionable end of the
            western spiral arm of the Galaxy lies a small unregarded yellow sun.
            Orbiting this at a distance of roughly ninety-two million miles is an
            utterly insignificant little blue green planet whose ape-descended life
            forms are so amazingly primitive that they still think digital watches
            are a pretty neat idea.
            % ---
            one. two three. four.
            ''')
        >>> #text = testdata_text(2)
        >>> formated_text = format_multiple_paragraph_sentences(text, debug=True)
        >>> print('+--- Text ---')
        >>> print(text)
        >>> print('+--- Formated Text ---')
        >>> print(formated_text)
        >>> print('L_____')
    """
    # Hack
    text = re.sub('^ *$', '', text, flags=re.MULTILINE)
    if debug:
        colorprint(msgblock('[fmt] text', text), 'yellow')
    #print(text.replace(' ', '_'))
    # Patterns that define separations between paragraphs in latex
    pattern_list = [
        '\n\n\n*',     # newlines
        #'\n\n*$',     # newlines
        #'^\n\n*',     # newlines
        #'\n\n*',     # newlines
        '\n? *%.*\n',  # comments

        # paragraph commands
        '\n? *\\\\paragraph{[^}]*}\n',
        # '\n? *\\\\item \\\\textbf{[^}]*}: *\n',
        '\n? *\\\\item \\\\textbf{[^:]*}: *\n',
        '\n? *\\\\section{[^}]*}\n',
        '\n? *\\\\section{[^}]*}\\\\label{[^}]*}\n',
        '\n? *\\\\section{[^}]*}\\~?\\\\label{[^}]*}\n',

        '\n? *\\\\subsection{[^}]*}\\~?\\\\label{[^}]*}\n',
        '\n? *\\\\subsection{[^~]*}\\~?\\\\label{[^}]*}\n',
        '\n? *\\\\subsection{[^}]*}\n',

        '\n? *\\\\subsubsection{[^~]*}\\~?\\\\label{[^}]*}\n',
        '\n? *\\\\subsubsection{[^}]*}\n',

        '\n----*\n',
        '##* .*\n',

        '\\.}\n',
        '\\?}\n',

        '\n? *\\\\newcommand{[^}]*}.*\n',
        # generic multiline commands with text inside (like devcomment)
        '\n? *\\\\[a-zA-Z]+{ *\n',

        '\n? *\\\\begin{[^}]*}\n',
        '\n? *\\\\item *\n',
        '\n? *\\\\noindent *\n',
        '\n? *\\\\ImageCommand[^}]*}[^}]*}{\n',
        '\n? *\\\\end{[^}]*}\n?',
        '\n}{',

        # docstr stuff
        '\n"""\n',
        '\n? *Args: *\n',
        #'\n? [A-Za-z_]*[0-9A-Za-z_]* (.*?) *:',
    ]
    pattern = '|'.join(['(%s)' % (pat,) for pat in pattern_list])
    # break into paragraph blocks
    block_list, separators = regex_reconstruct_split(pattern, text)

    collapse_pos_list = []
    # Dont format things within certain block types
    _iter = ub.iter_window([''] + separators + [''], 2)
    for count, (block, window) in enumerate(zip(block_list, _iter)):
        if (window[0].strip() == r'\begin{comment}' and
             window[1].strip() == r'\end{comment}'):
            collapse_pos_list.append(count)

    tofmt_block_list = block_list[:]

    collapse_pos_list = sorted(collapse_pos_list)[::-1]
    for pos in collapse_pos_list:
        collapsed_sep = (separators[pos - 1] + tofmt_block_list[pos] +
                         separators[pos])
        separators[pos - 1] = collapsed_sep
        del separators[pos]
        del tofmt_block_list[pos]

    if debug:
        colorprint('[fmt] tofmt_block_list = ' +
                      ub.repr2(tofmt_block_list), 'white')

    # apply formatting
    formated_block_list = []
    for block in tofmt_block_list:
        fmtblock = format_single_paragraph_sentences(
            block, debug=debug, **kwargs)
        formated_block_list.append(fmtblock)
    rejoined_list = list(interleave((formated_block_list, separators)))
    if debug:
        colorprint('[fmt] formated_block_list = ' +
                      ub.repr2(formated_block_list), 'turquoise')
    formated_text = ''.join(rejoined_list)
    return formated_text
