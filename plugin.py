import os
import sublime

if os.path.basename(os.path.dirname(__file__)) != "LSP-metals":
    name = os.path.basename(os.path.dirname(__file__))
    fmt = (
        'The directory of the LSP-metals package is named "{}".',
        'Please rename it to "LSP-metals" for correct functioning of',
        'this package.'
    )
    sublime.error_message(" ".join(fmt).format(name))
else:
    try:
        from LSP.plugin import __version__ as v
        if v < (1, 1, 0):
            from .st3 import *
        elif (1, 1, 0) <= v < (1, 2, 0):
            from .st4 import *
        else:
            fmt = "LSP-metals: unsupported LSP version: {}"
            sublime.error_message(fmt.format(v))
    except ImportError:
        # Ancient LSP
        from .st3 import *
