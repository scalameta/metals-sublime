import sublime
import sublime_plugin


class OpenFileEncodedCommand(sublime_plugin.WindowCommand):
    """
    A simple drop in replacement for the open_file command that allows file
    names with a :row or row:col position encoded at the end for opening files
    at a specific location.
    See https://github.com/sublimehq/sublime_text/issues/4800
    """
    def run(self, file):
        self.window.open_file(file, sublime.ENCODED_POSITION)
