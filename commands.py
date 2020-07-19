import sublime
from LSP.plugin.core.url import filename_to_uri
from LSP.plugin.core.registry import LspTextCommand

class NewScalaFileCommand(LspTextCommand):

    def is_enabled(self, event: 'Optional[dict]' = None) -> bool:
        return super().is_enabled() or bool(self.session('executeCommandProvider'))

    def run(self, 
            edit: sublime.Edit,
            paths) -> None:
        if(paths):
          args = {
            "command_name": "new-scala-file",
            "command_args": [filename_to_uri(paths[0])]
          }
          sublime.active_window().active_view().run_command("lsp_execute", args)
