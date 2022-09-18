from . lsp_metals_text_command import LspMetalsTextCommand
from LSP.plugin.core.views import text_document_position_params, first_selection_region

import sublime

class LspMetalsRunScalafixCommand(LspMetalsTextCommand):

    def run(self, edit: sublime.Edit) -> None:
        region = first_selection_region(self.view)
        if region is not None:
            point = region.begin()
            args = {
                "command_name": "scalafix-run",
                "command_args": [text_document_position_params(self.view, point)]
            }
            self.view.run_command("lsp_metals_execute", args)
