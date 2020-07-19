import sublime
import sublime_plugin
from LSP.plugin.core.url import filename_to_uri

class NewScalaFileCommand(sublime_plugin.TextCommand):

    def run(self, edit: sublime.Edit, paths) -> None:
        view = sublime.active_window().active_view()
        path = ''
        if(paths):
            path = paths[0]
        else:
            path = view.file_name()
        args = {
            "command_name": "new-scala-file",
            "command_args": [filename_to_uri(path)]
        }
        view.run_command("lsp_execute", args)
