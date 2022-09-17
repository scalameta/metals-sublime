from LSP.plugin import register_plugin
from LSP.plugin import unregister_plugin

import os
import sublime

package_name = __package__
if package_name != "LSP-metals":
    fmt = (
        'The directory of the LSP-metals package is named "{}".',
        'Please rename it to "LSP-metals" for correct functioning of',
        'this package.'
    )
    sublime.error_message(" ".join(fmt).format(package_name))
elif sublime.version() < '4000':
    sublime.error_message('This version requires st4, use the st3 branch')
else:
    from . commands.lsp_metals_analyze_stacktrace import LspMetalsAnalyzeStacktraceCommand
    from . commands.lsp_metals_copy_worksheet import LspMetalsCopyWorksheetCommand
    from . commands.lsp_metals_execute_command import LspMetalsExecuteCommand
    from . commands.lsp_metals_file_decoder import LspMetalsFileDecoderCommand
    from . commands.lsp_metals_find_in_dependency import LspMetalsFindInDependencyCommand
    from . commands.lsp_metals_focus import LspMetalsFocusViewCommand, ActiveViewListener
    from . commands.lsp_metals_goto import LspMetalsGoto
    from . commands.lsp_metals_goto_super_method import LspMetalsSendPositionCommand
    from . commands.lsp_metals_metals_goto_location import LspMetalsMetalsGotoLocationCommand
    from . commands.lsp_metals_run_scalafix import LspMetalsRunScalafixCommand
    from . commands.lsp_metals_show_build_target_info import LspMetalsShowBuildTargetInfoCommand
    from . commands.lsp_metals_text_command import LspMetalsTextCommand
    from . core.decorations import WorksheetListener, LspMetalsClearPhantomsCommand
    from . core.metals import Metals

    def plugin_loaded() -> None:
        register_plugin(Metals)

    def plugin_unloaded() -> None:
        unregister_plugin(Metals)
