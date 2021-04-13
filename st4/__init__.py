from ..common import create_launch_command
from ..common import get_java_path
from ..common import NewScalaFileCommand
from ..common import LspMetalsExecuteCommand
from ..common import prepare_server_properties
from LSP.plugin import AbstractPlugin
from LSP.plugin import register_plugin
from LSP.plugin import Response
from LSP.plugin import unregister_plugin
from LSP.plugin import WorkspaceFolder
from LSP.plugin import ClientConfig
from LSP.plugin.core.types import Optional, Dict, Any, Tuple, List
from LSP.plugin.core.views import range_to_region, FORMAT_MARKED_STRING, FORMAT_MARKUP_CONTENT, minihtml
from LSP.plugin.core.css import css
from LSP.plugin.core.protocol import Range
import sublime
import mdpopups
from functools import reduce
from . LspMetalsFocus import LspMetalsFocusViewCommand, ActiveViewListener

# TODO: Bring to public API
from LSP.plugin.core.views import location_to_encoded_filename


class Metals(AbstractPlugin):

    phantom_key = "metals_decoraction"

    @classmethod
    def name(cls) -> str:
        return cls.__name__.lower()

    @classmethod
    def configuration(cls) -> Tuple[sublime.Settings, str]:
        settings, path = super().configuration()
        java_path = get_java_path(settings)
        version = settings.get("server_version")
        properties = prepare_server_properties(settings.get("server_properties"))
        command = create_launch_command(java_path, version, properties)
        settings.set("command", command)
        return settings, path

    @classmethod
    def can_start(
        cls,
        window: sublime.Window,
        initiating_view: sublime.View,
        workspace_folders: List[WorkspaceFolder],
        configuration: ClientConfig
    ) -> Optional[str]:
        if not workspace_folders :
            return "No workspace detected. Try opening your project at the workspace root."

        plugin_settings = sublime.load_settings("LSP-metals.sublime-settings")
        java_path = get_java_path(plugin_settings)
        if not java_path :
            return "Please install java or set the 'java_home' setting"
        server_version = plugin_settings.get('server_version')
        if not server_version :
            return "'server_version' setting should be set"


    # notification and request handlers

    def m_metals_status(self, params: Any) -> None:
        """Handle the metals/status notification."""
        if not isinstance(params, dict):
            return
        session = self.weaksession()
        if not session:
            return
        key = "metals-status"
        if params.get("hide", False):
            session.set_window_status_async(key, params.get('text', ''))
        else:
            session.erase_window_status_async(key)

    def m_metals_publishDecorations(self, decorationsParams: Any) -> None:
        if not isinstance(decorationsParams, dict):
            return

        session = self.weaksession()
        if not session:
            return

        uri = decorationsParams.get('uri')
        if not uri:
            return

        session_buffer = session.get_session_buffer_for_uri_async(uri)
        if not session_buffer:
            return

        for sv in session_buffer.session_views:
            try:
                phantom_set = getattr(sv, "_lsp_metals_decorations")
            except AttributeError:
                phantom_set = sublime.PhantomSet(sv.view, self.phantom_key)
                setattr(sv, "_lsp_metals_decorations", phantom_set)

            phantom_set.update(decorations_to_phantom(decorationsParams.get('options', []), sv.view))


    def m_metals_executeClientCommand(self, params: Any) -> None:
        """Handle the metals/executeClientCommand notification."""
        # https://scalameta.org/metals/docs/editors/new-editor.html#goto-location-1
        if not isinstance(params, dict):
            return
        if params.get('command') == "metals-goto-location":
            args = params.get('arguments')
            if isinstance(args, list) and args:
                session = self.weaksession()
                if session:
                    session.window.open_file(
                        location_to_encoded_filename(args[0]),
                        flags=sublime.ENCODED_POSITION
                    )

    def m_metals_inputBox(self, params: Any, request_id: Any) -> None:
        """Handle the metals/inputBox request."""
        if not isinstance(params, dict):
            return
        session = self.weaksession()
        if not session:
            return

        def send_response(input: Optional[str]):
            p = { 'value': input, 'cancelled': False } if input else {'cancelled': True}
            session.send_response(Response(request_id, p))

        session.window.show_input_panel(
            params.get('prompt', ''),
            params.get('value', ''),
            send_response,
            None,
            lambda: send_response(None)
        )

PHANTOM_HTML = """
<style>div.phantom {{font-style: italic; color: {}}}</style>
<div class='phantom'>{}{}</div>"""

def show_popup(content: Dict[str, Any], view: sublime.View, location: int):
    html = minihtml(view, content, allowed_formats=FORMAT_MARKED_STRING | FORMAT_MARKUP_CONTENT)
    viewport_width = view.viewport_extent()[0]
    mdpopups.show_popup(
        view,
        html,
        css=css().popups,
        md=False,
        flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY,
        location=location,
        wrapper_class=css().popups_classname,
        max_width=viewport_width,
        on_navigate=None)


def decoration_to_phantom(option: Dict[str, Any], view: sublime.View) -> Optional[sublime.Phantom]:
    decorationRange = Range.from_lsp(option['range'])
    region = range_to_region(decorationRange, view)
    region.a = region.b  # make the start point equal to the end point
    hoverMessage = deep_get(option, 'hoverMessage')
    contentText = deep_get(option, 'renderOptions', 'after', 'contentText')
    link = ''
    point = None
    if hoverMessage:
        link = " <a href='more'>more</a>"
        point = view.text_point(decorationRange.start.row, decorationRange.start.col)

    color = view.style_for_scope("comment")["foreground"]
    phantomContent = PHANTOM_HTML.format(color, contentText, link)
    phantom = sublime.Phantom(
        region,
        phantomContent,
        sublime.LAYOUT_INLINE,
        lambda href: show_popup(hoverMessage, view, point))

    return phantom

def decorations_to_phantom(options: Dict[str, Any], view: sublime.View) -> List[sublime.Phantom]:
    return map(lambda o: decoration_to_phantom(o, view), options)


def deep_get(dictionary: Dict[str, Any], *keys):
    return reduce(lambda d, key: d.get(key) if d else None, keys, dictionary)

def plugin_loaded() -> None:
    register_plugin(Metals)


def plugin_unloaded() -> None:
    unregister_plugin(Metals)
