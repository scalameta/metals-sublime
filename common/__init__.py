from LSP.plugin.core.css import css
from LSP.plugin.core.protocol import Range
from LSP.plugin.core.types import Optional, Dict, Any, Tuple, List
from LSP.plugin.core.url import filename_to_uri  # TODO: deprecated in a future version
from LSP.plugin.core.views import range_to_region, FORMAT_MARKED_STRING, FORMAT_MARKUP_CONTENT, minihtml
from LSP.plugin.execute_command import LspExecuteCommand  # TODO: bring to public API
import os
import sublime
import sublime_plugin
import mdpopups
from functools import reduce

_COURSIER_PATH = os.path.join(os.path.dirname(__file__), '..', 'coursier')


def get_java_path(settings: sublime.Settings) -> str:
    java_home = settings.get("java_home")
    if isinstance(java_home, str) and java_home:
        return os.path.join(java_home, "bin", "java")
    java_home = os.environ.get('JAVA_HOME')
    if java_home:
        return os.path.join(java_home, "bin", "java")
    return "java"


def create_launch_command(java_path: str, artifact_version: str, server_properties: List[str]) -> List[str]:
    return [java_path] + server_properties + [
        "-jar",
        _COURSIER_PATH,
        "launch",
        "--ttl",
        "Inf",
        "--repository",
        "bintray:scalacenter/releases",
        "--repository",
        "sonatype:snapshots",
        "--main-class",
        "scala.meta.metals.Main",
        "org.scalameta:metals_2.12:{}".format(artifact_version)
    ]


def prepare_server_properties(properties: List[str]) -> List[str]:
    stripped = map(lambda p: p.strip(), properties)
    none_empty = list(filter(None, stripped))
    return none_empty

def deep_get(dictionary: Dict[str, Any], *keys):
    return reduce(lambda d, key: d.get(key) if d else None, keys, dictionary)

PHANTOM_HTML = """
<style>div.phantom {{font-style: italic; color: {}}}</style>
<div class='phantom'>{} {}</div>"""

def show_popup(content: Dict[str, Any], view: sublime.View, location: int):
    html = minihtml(view, content, allowed_formats=FORMAT_MARKED_STRING | FORMAT_MARKUP_CONTENT)
    mdpopups.show_popup(
        view,
        html,
        css=css().popups,
        md=False,
        flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY,
        location=location,
        wrapper_class=css().popups_classname,
        max_width=800,
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
        link = "<a href='more'>more</a>"
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


class NewScalaFileCommand(sublime_plugin.TextCommand):

    def run(self, edit: sublime.Edit, paths) -> None:
        path = paths[0] if paths else self.view.file_name()
        args = {
            "command_name": "new-scala-file",
            "command_args": [filename_to_uri(path)]
        }
        self.view.run_command("lsp_metals_execute", args)


class LspMetalsExecuteCommand(LspExecuteCommand):
    session_name = "metals"
