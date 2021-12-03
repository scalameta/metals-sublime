from functools import reduce
from LSP.plugin.core.css import css
from LSP.plugin.core.protocol import Range
from LSP.plugin.core.sessions import Session
from LSP.plugin.core.typing import Any, List, Dict, Optional
from LSP.plugin.core.views import range_to_region, FORMAT_MARKED_STRING, FORMAT_MARKUP_CONTENT, minihtml
import mdpopups
import sublime


def handle_publish_decorations(session: Session, decorations_params: Any) -> None:
    phantom_key = "metals_decoraction"

    if not isinstance(decorations_params, dict):
        return

    uri = decorations_params.get('uri')
    if not uri:
        return

    session_buffer = session.get_session_buffer_for_uri_async(uri)
    if not session_buffer:
        return

    for sv in session_buffer.session_views:
        try:
            phantom_set = getattr(sv, "_lsp_metals_decorations")
        except AttributeError:
            phantom_set = sublime.PhantomSet(sv.view, phantom_key)
            setattr(sv, "_lsp_metals_decorations", phantom_set)

        phantom_set.update(decorations_to_phantom(decorations_params.get('options', []), sv.view))

PHANTOM_HTML = """
<style>div.phantom {{font-style: italic; color: {}}}</style>
<div class='phantom'>{}{}</div>"""

def show_popup(content: Dict[str, Any], view: sublime.View, location: int) -> None:
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
    decoration_range = Range.from_lsp(option['range'])
    region = range_to_region(decoration_range, view)
    region.a = region.b  # make the start point equal to the end point
    hoverMessage = deep_get(option, 'hoverMessage')
    contentText = deep_get(option, 'renderOptions', 'after', 'contentText')
    link = ''
    point = view.text_point(decoration_range.start.row, decoration_range.start.col)
    if hoverMessage:
        link = " <a href='more'>more</a>"

    color = view.style_for_scope("comment")["foreground"]
    phantom_content = PHANTOM_HTML.format(color, contentText, link)
    phantom = sublime.Phantom(
        region,
        phantom_content,
        sublime.LAYOUT_INLINE,
        lambda href: show_popup(hoverMessage, view, point))

    return phantom

def decorations_to_phantom(options: Dict[str, Any], view: sublime.View) -> List[sublime.Phantom]:
    return map(lambda o: decoration_to_phantom(o, view), options)

def deep_get(dictionary: Dict[str, Any], *keys):
    return reduce(lambda d, key: d.get(key) if d else None, keys, dictionary)
