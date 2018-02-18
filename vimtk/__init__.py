"""
python -c "import ubelt._internal as a; a.autogen_init('vimtk', attrs=True)"
"""
# flake8: noqa
from vimtk.core import *
# from vimtk import core
# from vimtk import xctrl
# from vimtk.core import (CONFIG, Config, execute_text_in_terminal,)
# from vimtk.xctrl import (XCtrl, copy_text_to_clipboard, get_clipboard,
                         # get_number_of_monitors, get_resolution_info,
                         # import_pyqt,)


def reload():
    logger.debug('Reloading vimtk')
    import vimtk
    import vimtk.core
    import vimtk.xctrl
    import vimtk.pyinspect

    import imp
    imp.reload(vimtk.pyinspect)
    imp.reload(vimtk.core)
    imp.reload(vimtk.xctrl)
    imp.reload(vimtk)
