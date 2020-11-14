from LSP.plugin.core.types import Optional, List
from LSP.plugin.core.url import filename_to_uri
import os
import sublime
import sublime_plugin


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


class NewScalaFileCommand(sublime_plugin.TextCommand):

    def run(self, edit: sublime.Edit, paths) -> None:
        path = paths[0] if paths else self.view.file_name()
        args = {
            "command_name": "new-scala-file",
            "command_args": [filename_to_uri(path)]
        }
        self.view.run_command("lsp_execute", args)
