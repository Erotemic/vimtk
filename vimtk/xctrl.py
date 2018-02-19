# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import ubelt as ub
from vimtk import cplat
import time
import six
import re
import pipes
# from functools import partial
# from six.moves import builtins
import logging

logger = logging.getLogger(__name__)


def _wmctrl_terminal_patterns():
    """
    wmctrl patterns associated with common terminals
    """
    terminal_pattern = r'|'.join([
        'terminal',
        re.escape('terminator.Terminator'),  # gtk3 terminator
        re.escape('x-terminal-emulator.X-terminal-emulator'),  # gtk2 terminator
        # other common terminal applications
        'tilix',
        'konsole',
        'rxvt',
        'terminology',
        'xterm',
        'tilda',
        'Yakuake',
    ])
    return terminal_pattern


class XCtrl(object):
    r"""
    xdotool key ctrl+shift+i

    References:
        http://superuser.com/questions/382616/detecting-currently-active-window
        http://askubuntu.com/questions/455762/xbindkeys-wont-work-properly

    Ignore:
        xdotool keyup --window 0 7 type --clearmodifiers ---window 0 '%paste'

        # List current windows:
        wmctrl  -l

        # Get current window
        xdotool getwindowfocus getwindowname


        #====
        # Get last opened window
        #====

        win_title=x-terminal-emulator.X-terminal-emulator
        key_ = 'x-terminal-emulator.X-terminal-emulator'

        # Get all windows in current workspace
        workspace_number=`wmctrl -d | grep '\*' | cut -d' ' -f 1`
        win_list=`wmctrl -lx | grep $win_title | grep " $workspace_number " | awk '{print $1}'`

        # Get stacking order of windows in current workspace
        win_order=$(xprop -root|grep "^_NET_CLIENT_LIST_STACKING" | tr "," " ")
        echo $win_order

    CommandLine:
        python -m vimtk.xctrl XCtrl:0

    Example:
        >>> # DISABLE_DOCTEST
        >>> # Script
        >>> orig_window = []
        >>> copy_text_to_clipboard(lorium_ipsum())
        >>> doscript = [
        >>>     ('focus', 'x-terminal-emulator.X-terminal-emulator'),
        >>>     ('type', '%paste'),
        >>>     ('key', 'KP_Enter'),
        >>>    # ('focus', 'GVIM')
        >>> ]
        >>> XCtrl.do(*doscript, sleeptime=.01)

    Ignore:
        >>> copy_text_to_clipboard(text)
        >>> if '\n' in text or len(text) > 20:
        >>>     text = '\'%paste\''
        >>> else:
        >>>     import pipes
        >>>     text = pipes.quote(text.lstrip(' '))
        >>>     ('focus', 'GVIM'),
        >>> #
        >>> doscript = [
        >>>     ('focus', 'x-terminal-emulator.X-terminal-emulator'),
        >>>     ('type', text),
        >>>     ('key', 'KP_Enter'),
        >>> ]
        >>> XCtrl.do(*doscript, sleeptime=.01)


    """
    # @staticmethod
    # def send_raw_key_input(keys):
    #     print('send key input: %r' % (keys,))
    #     args = ['xdotool', 'type', keys]
    #     XCtrl.cmd(*args, quiet=True, silence=True)

    @staticmethod
    def move_window(win_key, bbox):
        """
        CommandLine:
            # List windows
            wmctrl -l
            # List desktops
            wmctrl -d

            # Window info
            xwininfo -id 60817412

            python -m vimtk.xctrl XCtrl.move_window joncrall 0+1920,680,400,600,400
            python -m vimtk.xctrl XCtrl.move_window joncrall [0,0,1000,1000]
            python -m vimtk.xctrl XCtrl.move_window GVIM special2
            python -m vimtk.xctrl XCtrl.move_window joncrall special2
            python -m vimtk.xctrl XCtrl.move_window x-terminal-emulator.X-terminal-emulator [0,0,1000,1000]

        CommandLine:
            python -m vimtk.xctrl XCtrl.move_window

        Example:
            >>> # DISABLE_DOCTEST
            >>> XCtrl.move_window('joncrall', '[0,0,1000,1000]')

        Ignore:
            # >>> orig_window = []
            # >>> X = xctrl.XCtrl
            win_key =  'x-terminal-emulator.X-terminal-emulator'
            win_id = X.findall_window_ids(key)[0]

            python -m xctrl XCtrl.findall_window_ids gvim

        """
        monitor_infos = {
            i + 1: cplat.get_resolution_info(i)
            for i in range(2)
        }
        # TODO: cut out borders
        # TODO: fix screeninfo monitor offsets
        # TODO: dynamic num screens
        def rel_to_abs_bbox(m, x, y, w, h):
            """ monitor_num, relative x, y, w, h """
            minfo = monitor_infos[m]
            # print('minfo(%d) = %s' % (m, ub.repr2(minfo),))
            mx, my = minfo['off_x'], minfo['off_y']
            mw, mh = minfo['pixels_w'], minfo['pixels_h']
            # Transform to the absolution position
            abs_x = (x * mw) + mx
            abs_y = (y * mh) + my
            abs_w = (w * mw)
            abs_h = (h * mh)
            abs_bbox = [abs_x, abs_y, abs_w, abs_h]
            abs_bbox = ','.join(map(str, map(int, abs_bbox)))
            return abs_bbox

        if win_key.startswith('joncrall') and bbox == 'special2':
            # Specify the relative position
            abs_bbox = rel_to_abs_bbox(m=2,
                                       x=0.0, y=0.7,
                                       w=1.0, h=0.3)
        elif win_key.startswith('GVIM') and bbox == 'special2':
            # Specify the relative position
            abs_bbox = rel_to_abs_bbox(m=2,
                                       x=0.0, y=0.0,
                                       w=1.0, h=0.7)
        else:
            abs_bbox = ','.join(map(str, eval(bbox)))

        print('MOVING: win_key = %r' % (win_key,))
        print('TO: abs_bbox = %r' % (abs_bbox,))
        # abs_bbox.replace('[', '').replace(']', '')
        # get = lambda cmd: XCtrl.cmd(' '.join(["/bin/bash", "-c", cmd]))['out']  # NOQA
        win_id = XCtrl.find_window_id(win_key, error='raise')
        print('MOVING: win_id = %r' % (win_id,))
        fmtdict = locals()
        cmd_list = [
            ("wmctrl -ir {win_id} -b remove,maximized_horz".format(**fmtdict)),
            ("wmctrl -ir {win_id} -b remove,maximized_vert".format(**fmtdict)),
            ("wmctrl -ir {win_id} -e 0,{abs_bbox}".format(**fmtdict)),
        ]
        print('\n'.join(cmd_list))
        for cmd in cmd_list:
            XCtrl.cmd(cmd)

    @staticmethod
    def cmd(command):
        logging.debug('[cmd] {}'.format(command))
        info = ub.cmd(command)
        if info['ret'] != 0:
            logging.warn('Something went wrong {}'.format(ub.repr2(info)))
        return info

    @staticmethod
    def findall_window_ids(pattern):
        """
        CommandLine:
            python -m vimtk.xctrl XCtrl.findall_window_ids --pat=gvim
            python -m vimtk.xctrl XCtrl.findall_window_ids --pat=gvim
            python -m vimtk.xctrl XCtrl.findall_window_ids --pat=joncrall

        Example:
            >>> # SCRIPT
            >>> pattern = ub.argval('--pat')
            >>> winid_list = XCtrl.findall_window_ids(pattern)
            >>> print('winid_list = {!r}'.format(winid_list))

        Ignore:
            wmctrl -l
            xprop -id
            wmctrl -l | awk '{print $1}' | xprop -id
            0x00a00007 | grep "WM_CLASS(STRING)"
        """
        # List all windows and their identifiers
        info = XCtrl.cmd('wmctrl -lx')
        lines = info['out'].split('\n')
        # Find windows with identifiers matching the pattern
        lines = [line for line in lines if re.search(pattern, line)]
        # Get the hex-id portion of the output
        winid_list = [line.split()[0] for line in lines]
        winid_list = [int(h, 16) for h in winid_list if h]
        return winid_list

    @staticmethod
    def sort_window_ids(winid_list, order='mru'):
        """
        Orders window ids by most recently used
        """
        def isect(list1, list2):
            set2 = set(list2)
            return [item for item in list1 if item in set2]

        winid_order = XCtrl.sorted_window_ids(order)
        sorted_win_ids = isect(winid_order, winid_list)
        return sorted_win_ids

    @staticmethod
    def killold(pattern, num=4):
        """
        Leaves no more than `num` instances of a program alive.  Ordering is
        determined by most recent usage.

        CommandLine:
            python -m vimtk.xctrl XCtrl.killold gvim 2

        Example:
            >>> # SCRIPT
            >>> XCtrl = xctrl.XCtrl
            >>> pattern = 'gvim'
            >>> num = 2
        """
        import psutil
        num = int(num)
        winid_list = XCtrl.findall_window_ids(pattern)
        winid_list = XCtrl.sort_window_ids(winid_list, 'mru')[num:]

        info = XCtrl.cmd('wmctrl -lxp')
        lines = info['out'].split('\n')
        lines = [' '.join(list(ub.take(line.split(), [0, 2])))
                 for line in lines]
        output_lines = lines
        # output_lines = XCtrl.cmd(
        #     """wmctrl -lxp | awk '{print $1 " " $3}'""",
        #     **cmdkw)['out'].strip().split('\n')
        output_fields = [line.split(' ') for line in output_lines]
        output_fields = [(int(wid, 16), int(pid)) for wid, pid in output_fields]
        pid_list = [pid for wid, pid in output_fields if wid in winid_list]
        for pid in pid_list:
            proc = psutil.Process(pid=pid)
            proc.kill()

    @staticmethod
    def sorted_window_ids(order='mru'):
        """
        Returns window ids orderd by criteria
        default is mru (most recently used)

        CommandLine:
            xprop -root | grep "^_NET_CLIENT_LIST_STACKING" | tr "," " "
            python -m vimtk.xctrl XCtrl.sorted_window_ids

        CommandLine:
            python -m vimtk.xctrl XCtrl.sorted_window_ids

        Example:
            >>> # SCRIPT
            >>> winid_order = XCtrl.sorted_window_ids()
            >>> print('winid_order = {!r}'.format(winid_order))
        """
        info = XCtrl.cmd('xprop -root')
        lines = [line for line in info['out'].split('\n')
                 if line.startswith('_NET_CLIENT_LIST_STACKING')]
        assert len(lines) == 1, str(lines)
        winid_order_str = lines[0]
        winid_order = winid_order_str.split('#')[1].strip().split(', ')[::-1]
        winid_order = [int(h, 16) for h in winid_order]
        if order == 'lru':
            winid_order = winid_order[::-1]
        elif order == 'mru':
            winid_order = winid_order
        else:
            raise NotImplementedError(order)
        return winid_order

    @staticmethod
    def find_window_id(pattern, method='mru', error='raise'):
        """
        xprop -id 0x00a00007 | grep "WM_CLASS(STRING)"
        """
        logging.debug('Find window id pattern={}, method={}'.format(pattern, method))
        winid_candidates = XCtrl.findall_window_ids(pattern)
        if len(winid_candidates) == 0:
            if error == 'raise':
                available_windows = XCtrl.cmd('wmctrl -lx')['out']
                msg = 'No window matches pattern=%r' % (pattern,)
                msg += '\navailable windows are:\n%s' % (available_windows,)
                logger.error(msg)
                raise Exception(msg)
            win_id = None
        elif len(winid_candidates) == 1:
            win_id = winid_candidates[0]
        else:
            # print('Multiple (%d) windows matches pattern=%r' % (
            #     len(winid_list), pattern,))
            # Find most recently used window with the focus name.
            win_id = XCtrl.sort_window_ids(winid_candidates, method)[0]
        return win_id

    @staticmethod
    def current_gvim_edit(op='e', fpath=''):
        r"""
        CommandLine:
            python -m vimtk.xctrl XCtrl.current_gvim_edit sp ~/.bashrc
        """
        fpath = ub.compressuser(ub.truepath(fpath))
        # print('fpath = %r' % (fpath,))
        cplat.copy_text_to_clipboard(fpath)
        doscript = [
            ('focus', 'gvim'),
            ('key', 'Escape'),
            ('type2', ';' + op + ' ' + fpath),
            # ('type2', ';' + op + ' '),
            # ('key', 'ctrl+v'),
            ('key', 'KP_Enter'),
        ]
        XCtrl.do(*doscript, verbose=0, sleeptime=.001)

    @staticmethod
    def copy_gvim_to_terminal_script(text, return_to_win="1", verbose=0, sleeptime=.02):
        """
        vimtk.xctrl.XCtrl.copy_gvim_to_terminal_script('print("hi")', verbose=1)
        python -m vimtk.xctrl XCtrl.copy_gvim_to_terminal_script "echo hi" 1 1

        If this doesn't work make sure pyperclip is installed and set to xsel

        print('foobar')
        echo hi
        """
        # Prepare to send text to xdotool
        cplat.copy_text_to_clipboard(text)

        if verbose:
            print('text = %r' % (text,))
            print(cplat.get_clipboard())

        terminal_pattern = r'\|'.join([
            'terminal',
            re.escape('terminator.Terminator'),  # gtk3 terminator
            re.escape('x-terminal-emulator.X-terminal-emulator'),  # gtk2 terminator
        ])

        # Build xdtool script
        doscript = [
            ('remember_window_id', 'ACTIVE_WIN'),
            # ('focus', 'x-terminal-emulator.X-terminal-emulator'),
            ('focus', terminal_pattern),
            ('key', 'ctrl+shift+v'),
            ('key', 'KP_Enter'),
        ]
        if '\n' in text:
            # Press enter twice for multiline texts
            doscript += [
                ('key', 'KP_Enter'),
            ]

        if return_to_win == "1":
            doscript += [
                ('focus_id', '$ACTIVE_WIN'),
            ]
        # execute script
        # verbose = 1
        XCtrl.do(*doscript, sleeptime=sleeptime, verbose=verbose)

    @staticmethod
    def do(*cmd_list, **kwargs):
        verbose = kwargs.get('verbose', False)
        if verbose:
            print = logger.info
        else:
            print = logger.debug

        print('Executing x do: %s' % (ub.repr2(cmd_list),))

        # http://askubuntu.com/questions/455762/xbindkeys-wont-work-properly
        # Make things work even if other keys are pressed
        defaultsleep = 0.0
        sleeptime = kwargs.get('sleeptime', defaultsleep)
        time.sleep(.05)
        XCtrl.cmd('xset r off')

        memory = {}

        for count, item in enumerate(cmd_list):
            # print('item = %r' % (item,))
            sleeptime = kwargs.get('sleeptime', defaultsleep)

            assert isinstance(item, tuple)
            assert len(item) >= 2
            xcmd, key_ = item[0:2]
            if len(item) >= 3:
                if isinstance(item[2], six.string_types) and item[2].endswith('?'):
                    sleeptime = float(item[2][:-1])
                    print('special command sleep')
                    print('sleeptime = %r' % (sleeptime,))
                else:
                    sleeptime = float(item[2])

            args = []

            print('# Step %d' % (count,))
            print('xcmd = {!r}'.format(xcmd))

            if xcmd == 'focus':
                key_ = str(key_)
                if key_.startswith('$'):
                    key_ = memory[key_[1:]]
                pattern = key_
                win_id = XCtrl.find_window_id(pattern, method='mru')
                if win_id is None:
                    args = ['wmctrl', '-xa', pattern]
                else:
                    args = ['wmctrl', '-ia', hex(win_id)]
            elif xcmd == 'focus_id':
                key_ = str(key_)
                if key_.startswith('$'):
                    key_ = memory[key_[1:]]
                args = ['wmctrl', '-ia', hex(key_)]
            elif xcmd == 'remember_window_id':
                memory[key_] = XCtrl.current_window_id()
                continue
            elif xcmd == 'remember_window_name':
                memory[key_] = XCtrl.current_window_name()
                continue
            elif xcmd == 'type':
                args = [
                    'xdotool',
                    'keyup', '--window', '0', '7',
                    'type', '--clearmodifiers',
                    '--window', '0', str(key_)
                ]
            elif xcmd == 'type2':
                args = [
                    'xdotool', 'type', pipes.quote(str(key_))
                ]
            elif xcmd == 'xset-r-on':
                args = ['xset', 'r', 'on']
            elif xcmd == 'xset-r-off':
                args = ['xset', 'r', 'off']
            else:
                args = ['xdotool', str(xcmd), str(key_)]

            print('args = {!r}'.format(args))
            XCtrl.cmd(args)

            if sleeptime > 0:
                time.sleep(sleeptime)

        XCtrl.cmd('xset r on')

    @staticmethod
    def current_window_id():
        logging.debug('Get current window id')
        info = XCtrl.cmd('xdotool getwindowfocus')
        value = int(info['out'].strip())
        logging.debug('... current window id = {}'.format(value))
        return value

    @staticmethod
    def current_window_name():
        logging.debug('Get current window name')
        info = XCtrl.cmd('xdotool getwindowfocus getwindowname')
        value = pipes.quote(info['out'].strip())
        logging.debug('... current window name = {}'.format(value))
        return value

    @staticmethod
    def focus_window(winhandle, path=None, name=None, sleeptime=.01):
        """
        sudo apt-get install xautomation
        apt-get install autokey-gtk

        wmctrl -xa gnome-terminal.Gnome-terminal
        wmctrl -xl
        """
        print('focus: ' + winhandle)
        args = ['wmctrl', '-xa', winhandle]
        XCtrl.cmd(*args, verbose=False)
        time.sleep(sleeptime)


if __name__ == '__main__':
    r"""
    CommandLine:
        export PYTHONPATH=$PYTHONPATH:$HOME/code/vimtk
        python -m vimtk.xctrl
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
