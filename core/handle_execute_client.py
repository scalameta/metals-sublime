from . status import status_key
from .. commands.utils import open_location
from LSP.plugin.core.sessions import Session
from LSP.plugin.core.types import Any
import json
import sublime
import mdpopups


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

        header = content.get("header")
        messages = content.get('messages')
        targets = content.get('targets')
        explanations = content.get('explanations')

        markdown = ""
        markdown += "# {} \n\n".format(content.get('title'))

        if header:
            markdown += "{} \n\n".format(header.get('buildServer'))
            markdown += "{} \n\n".format(header.get('jdkInfo'))
            markdown += "{} \n\n".format(header.get('serverInfo'))
            markdown += "{} \n\n".format(header.get('buildTargetDescription'))

        if messages:
            for message in messages:
                markdown += "### {} \n".format(message.get('title'))
                for recommendation in message.get('recommendations'):
                    markdown += '* {}\n'.format(recommendation)
                markdown += '\n\n'

        if targets:
            markdown += "## Build Targets\n"
            lines = []
            for target in targets:
                line = [
                    '#### {}'.format(target.get('buildTarget')),
                    '```',
                    '* {0:<20}: {1}'.format("Target Type", target.get('targetType')),
                    '* {0:<20}: {1}'.format("Compilation status",target.get('compilationStatus')),
                    '* {0:<20}: {1}'.format("Diagnostics", target.get('diagnostics')),
                    '* {0:<20}: {1}'.format("Interactive", target.get('interactive')),
                    '* {0:<20}: {1}'.format("SemanticDB", target.get('semanticdb')),
                    '* {0:<20}: {1}'.format("Debugging", target.get('debugging')),
                    '* {0:<20}: {1}'.format("Java Support", target.get('java'))
                ]

                if target.get('recommendation'):
                    line.append('* {0:<20}: {1}'.format("Recommendation", target.get('recommendation')))

                line.append("```")

                lines.append('\n'.join(line))

            markdown += "{}\n\n".format('\n'.join(lines))

        if explanations:
            markdown += "## Explanations\n"
            for explanation in explanations:
                markdown += '{}\n\n'.format(explanation.get('title'))
                for explanation in explanation.get('explanations'):
                    markdown += '* {}\n'.format(explanation)
                markdown += '\n\n'

        custom_css = """
        .metals-doctor { padding: 1.5rem }
        .metals-doctor h1, .metals-doctor h2 { text-decoration: underline }
        .metals-doctor h2, .metals-doctor h3, .metals-doctor h4, .metals-doctor p, .metals-doctor ul { margin-top: 1rem }
        """
        mdpopups.new_html_sheet(session.window, "Metals Doctor", markdown, True, css=custom_css, wrapper_class="metals-doctor")
