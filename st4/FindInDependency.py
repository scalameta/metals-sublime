from LSP.plugin.core.protocol import Request, Location
from LSP.plugin.core.registry import LspTextCommand
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

class FindInDependencyCommand(LspTextCommand):
    _command = "metals/findTextInDependencyJars"
    session_name = "metals"

    def input(self, _args: Any) -> sublime_plugin.TextInputHandler:
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
                session.send_request(request, self._handle_response, self._handle_error)

    def _handle_response(self, response: Union[List[Location], None]) -> None:
        if response:
            locations = response
            session = self.weaksession()
            self.view.run_command("add_jump_record", {"selection": [(r.a, r.b) for r in self.view.sel()]})
            LocationPicker(self.view, session, locations, side_by_side=False)
        else:
            sublime.message_dialog("No matches found")

    def _handle_error(self, error: Dict[str, Any]) -> None:
        reason = error.get("message", "none provided by server :(")
        msg = "command '{}' failed. Reason: {}".format(self._command, reason)
        sublime.error_message(msg)
