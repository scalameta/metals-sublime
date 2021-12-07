from . status import status_key
from LSP.plugin.core.sessions import Session
from LSP.plugin.core.types import Any
from LSP.plugin.core.views import location_to_encoded_filename
from urllib.parse import urlparse, unquote
import re
import json
import sublime
import mdpopups
from tabulate import tabulate


def handle_execute_client(session: Session, params: Any) -> None:
    """Handle the metals/executeClientCommand notification."""

    if not isinstance(params, dict):
        return
    command_name = params.get('command')
    args = params.get('arguments')

    if command_name == "metals-goto-location":
        goto_location(session, args)
    elif command_name == 'metals-show-stacktrace':
        show_stacktrace(session, args)
    elif command_name in {'metals-doctor-run', 'metals-doctor-reload'}:
        run_doctor(session, args)
    else:
        msg = "Unknown command {}".format(command_name)
        session.set_window_status_async(status_key, msg)

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

def run_doctor(session: Session, args: Any) -> None:
    if isinstance(args, list) and args:
        content = json.loads(args[0])
        messages = content.get('messages')
        targets = content.get('targets')
        markdown = ""
        markdown += "## {}  \n\n".format(content.get('headerText'))

        if messages:
            for message in messages:
                markdown += "### {} \n".format(message.get('title'))
                for recommendation in message.get('recommendations'):
                    markdown += '* {}\n'.format(recommendation)
                markdown += '\n\n'
        else:
            headers = [
                'Build Target',
                'Scala Version',
                'Diagnostics',
                'Goto Definition',
                'Completions',
                'Find References',
                'Recommendation'
            ]
            markdown += "## Build Targets\n"
            lines = []
            for target in targets:
                lines.append([
                    target.get('buildTarget'),
                    target.get('scalaVersion'),
                    target.get('diagnostics'),
                    target.get('gotoDefinition'),
                    target.get('completions'),
                    target.get('findReferences'),
                    target.get('recommendation')
                ])
            table = tabulate(lines, headers, "pretty")
            markdown += "```\n{}\n```\n\n".format(table)
        mdpopups.new_html_sheet(session.window, "Metals Doctor", markdown, True)
