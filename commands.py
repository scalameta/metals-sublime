import sublime
import sublime_plugin
from LSP.plugin.core.url import filename_to_uri

class NewScalaFileCommand(sublime_plugin.TextCommand):

    def run(self, edit: sublime.Edit, paths) -> None:
        if(paths):
            path = paths[0]
        else:
            path = self.view.file_name()
        args = {
            "command_name": "new-scala-file",
            "command_args": [filename_to_uri(path)]
        }
        self.view.run_command("lsp_execute", args)
