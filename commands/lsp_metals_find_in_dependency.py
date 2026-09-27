from __future__ import annotations

from .lsp_metals_text_command import LspMetalsTextCommand
from .utils import handle_error
from LSP.plugin import Error
from LSP.plugin import LocationPicker
from LSP.plugin import Request
from LSP.protocol import Location
from typing import Any
from typing import List
import sublime
import sublime_plugin
import weakref


class IncludeInput(sublime_plugin.TextInputHandler):
    def validate(self, txt: str) -> bool:
        return txt != ""

    def placeholder(self) -> str:
        return "File filter"

class PatternInput(sublime_plugin.TextInputHandler):
    def validate(self, txt: str) -> bool:
        return txt != ""

    def placeholder(self) -> str:
        return "Text pattern to search for"

    def next_input(self, value):
        return IncludeInput()

class LspMetalsFindInDependencyCommand(LspMetalsTextCommand):
    _command = "metals/findTextInDependencyJars"

    def input(self, _args: Any):
        return PatternInput()

    def run(self, edit: sublime.Edit, pattern_input: str, include_input: str) -> None:
        if pattern_input and include_input:
            session = self.session_by_name()
            if session:
                params = {
                    "query": {"pattern": pattern_input},
                    "options": {"include": include_input}
                  }
                request = Request(self._command, params, None, progress=True)
                self.weaksession = weakref.ref(session)
                session.send_request_task(request).then(self._handle_response)

    def _handle_response(self, response: List[Location] | Error | None) -> None:
        if isinstance(response, Error):
            handle_error(self._command, response)
            return
        if response:
            locations = response
            session = self.weaksession()
            if session:
                self.view.run_command("add_jump_record", {"selection": [(r.a, r.b) for r in self.view.sel()]})
                LocationPicker(self.view, session, locations, side_by_side=False)
        else:
            sublime.message_dialog("No matches found")
