from . status import status_key
from .. commands.utils import open_location
from LSP.plugin.core.sessions import Session
from LSP.plugin.core.types import Any
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
    elif command_name in {'metals-doctor-run'}:
        run_doctor(session, args)
    else:
        msg = "Unknown command {}".format(command_name)
        session.set_window_status_async(status_key, msg)

def goto_location(session: Session, args: Any) -> None:
    """https://scalameta.org/metals/docs/integrations/new-editor/#goto-location"""

    if isinstance(args, list) and args:
        open_location(session.window, args[0])

def show_stacktrace(session: Session, args: Any) -> None:
    """https://scalameta.org/metals/docs/integrations/new-editor/#show-the-stacktrace-in-the-client"""

    if isinstance(args, list) and args:
        session.window.new_html_sheet('Stacktrace', args[0])

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
