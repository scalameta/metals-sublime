from . lsp_metals_text_command import LspMetalsTextCommand
from . utils import handle_error
from LSP.plugin.core.protocol import Request, Location
from LSP.plugin.core.sessions import Session
from LSP.plugin.core.typing import Any, List, Union, Dict
from LSP.plugin.locationpicker import LocationPicker
import weakref

import sublime
import sublime_plugin

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

    def next_input(handler, value):
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
                session.send_request(request, self._handle_response,
                    lambda r: handle_error(self._command, r))

    def _handle_response(self, response: Union[List[Location], None]) -> None:
        if response:
            locations = response
            session = self.weaksession()
            if session:
                self.view.run_command("add_jump_record", {"selection": [(r.a, r.b) for r in self.view.sel()]})
                LocationPicker(self.view, session, locations, side_by_side=False)
        else:
            sublime.message_dialog("No matches found")
