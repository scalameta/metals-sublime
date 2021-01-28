from LSP.plugin.core.types import Optional, List
from LSP.plugin.core.url import filename_to_uri  # TODO: deprecated in a future version
from LSP.plugin.execute_command import LspExecuteCommand  # TODO: bring to public API
from LSP.plugin.core.views import range_to_region
from LSP.plugin.core.types import Optional, Dict, Any, Tuple, List
from LSP.plugin.core.protocol import Range, Point
import os
import sublime
import sublime_plugin
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
<style>div.phantom {{font-style: italic; color: #00ff73}}</style>
<div class='phantom'>{}</div>"""

def decoraction_to_phantom(option: Dict[str, Any], view: sublime.View) -> Optional[sublime.Phantom]:
    start = Point(deep_get(option, 'range', 'start', 'line'), deep_get(option, 'range', 'start', 'character') + 1)
    end = Point(deep_get(option, 'range', 'end', 'line'), deep_get(option, 'range', 'end', 'character') + 1)
    region = range_to_region(Range(start, end), view)
    hoverMessage = deep_get(option, 'hoverMessage')
    contentText = deep_get(option, 'renderOptions', 'after', 'contentText')
    color = deep_get(option, 'renderOptions', 'after', 'color')
    fontStyle = deep_get(option, 'renderOptions', 'after', 'fontStyle')
    return sublime.Phantom(region, PHANTOM_HTML.format(contentText), sublime.LAYOUT_INLINE, None)

def decoractions_to_phantom(options: Dict[str, Any], view: sublime.View) -> List[sublime.Phantom]:
    return map(lambda o: decoraction_to_phantom(o, view), options)


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
