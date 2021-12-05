from . lsp_metals_text_command import LspMetalsTextCommand
from LSP.plugin.core.protocol import Notification
from LSP.plugin.core.types import Optional, Dict, Any

import sublime
import sublime_plugin
import functools

class LspMetalsFocusViewCommand(LspMetalsTextCommand):

    def run(self, edit: sublime.Edit) -> None:
        fname = self.view.file_name()
        if not fname:
            return
        sublime.set_timeout_async(functools.partial(self.run_async, fname))

    def run_async(self, fname: str) -> None:
        session = self.session_by_name()
        if not session:
            return
        uri = session.config.map_client_path_to_server_uri(fname)
        session.send_notification(Notification("metals/didFocusTextDocument", uri))


class ActiveViewListener(sublime_plugin.EventListener):
    def on_activated_async(self, view: sublime.View) -> None:
        if view.file_name():
            view.run_command("lsp_metals_focus_view")
