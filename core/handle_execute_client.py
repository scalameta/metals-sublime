from LSP.plugin.core.sessions import Session
from LSP.plugin.core.types import Any
from LSP.plugin.core.views import location_to_encoded_filename
from urllib.parse import urlparse, unquote
import re
import json
import sublime


def handle_execute_client(session: Session, params: Any) -> None:
    """Handle the metals/executeClientCommand notification."""

    if not isinstance(params, dict):
        return
    command_name = params.get('command')
    args = params.get('arguments')

    if command_name == "metals-goto-location":
        goto_location(session, args)
    if command_name == 'metals-show-stacktrace':
        show_stacktrace(session, args)

def goto_location(session: Session, args: Any) -> None:
    """https://scalameta.org/metals/docs/integrations/new-editor/#goto-location"""

    if isinstance(args, list) and args:
        session.window.open_file(
            location_to_encoded_filename(args[0]),
            flags=sublime.ENCODED_POSITION
        )

def show_stacktrace(session: Session, args: Any) -> None:
    """https://scalameta.org/metals/docs/integrations/new-editor/#show-the-stacktrace-in-the-client"""

    def _replace_link(match) -> str:
        url = urlparse(match.group(1))
        command_args = json.loads(unquote(url.query))
        path = urlparse(command_args[0]).path
        location = command_args[1] + 1
        return "href='subl:lsp_metals_open_file_encoded {{\"file\": \"{}:{}\"}}'".format(path, location)

    if isinstance(args, list) and args:
        new_content = re.sub('href=\'(.*?)\'', _replace_link, args[0])
        session.window.new_html_sheet('Stacktrace', new_content)
