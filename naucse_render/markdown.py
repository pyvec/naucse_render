import unicodedata
from textwrap import dedent
import re

from ansi2html import Ansi2HTMLConverter
import mistune
from markupsafe import Markup
import pygments
import pygments.lexers
from pygments.lexer import RegexLexer, bygroups
from pygments.token import Generic, Text, Comment
import pygments.formatters.html


def naucse_admonition_plugin(md):
    """Parse blockquote-based admonitions

    Like this:

    > [note] Note Title
    > rest of note goes here
    """
    # Based on Mistune's "spoiler" plugin (the documentation says:
    # "take a look at the source code in mistune/plugins to find
    # out how to write a plugin")

    ADMONITION_NAME_PATTERN = re.compile(r' *\[(\S+)\]([^\n]*)\n')

    def parse_naucse_admonition(block, m, state):

        text, end_pos = block.extract_block_quote(m, state)
        name_match = ADMONITION_NAME_PATTERN.match(text)
        if name_match:
            # It's an amonition
            token = {
                'type': 'naucse_admonition',
                'attrs': {
                    'name': name_match[1].strip(),
                    'title': name_match[2].strip(),
                },
            }
            text = text[name_match.end():]
        else:
            token = {
                'type': 'block_quote',
            }

        child = state.child_state(text)
        rules = block.block_quote_rules
        block.parse(child, rules)
        token['children'] = child.tokens
        if end_pos:
            state.prepend_token(token)
            return end_pos
        state.append_token(token)
        return state.cursor

    md.block.register(
        'block_quote',
        None,
        parse_naucse_admonition,
        before='block_quote',
    )


ansi_convertor = Ansi2HTMLConverter(inline=True)

pygments_formatter = pygments.formatters.html.HtmlFormatter(
    cssclass='highlight'
)


def ansi_convert(code):
    replaced = code.replace('\u241b', '\x1b')
    return ansi_convertor.convert(replaced, full=False)


def style_space_after_prompt(html):
    return re.sub(r'<span class="gp">([^<]*[^<\s])</span>(\s)',
                  r'<span class="gp">\1\2</span>',
                  html)


class MSDOSSessionVenvLexer(RegexLexer):
    """Lexer for simplistic MSDOS sessions with optional venvs.

    Note that this doesn't use ``Name.Builtin`` (class="nb"), which naucse
    styles the same as the rest of the command.
    """
    name = 'MSDOS Venv Session'
    aliases = ['dosvenv']
    tokens = {
        'root': [
            (r'((?:\([_\w]+\))?\s?>\s?)([^#\n]*)(#.*)?',
             bygroups(Generic.Prompt, Text, Comment)),
            (r'(.+)', Generic.Output),
        ]
    }


def get_lexer_by_name(lang):
    """
    Workaround for our own lexer. Normally, new lexers have to be added trough
    entrypoints to be locatable by get_lexer_by_name().
    """
    if lang == 'dosvenv':
        return MSDOSSessionVenvLexer()
    return pygments.lexers.get_lexer_by_name(lang)


# https://stackoverflow.com/a/31607735/1107768
def strip_accents(text: str) -> str:
    """
    Strip accents from input string.
    """
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)


def text_to_id(text):
    """
    Convert input text to id.
    """
    text = strip_accents(text.lower())
    text = re.sub('[ ]+', '_', text)
    text = re.sub('[^0-9a-zA-Z_-]', '', text)
    return text


class NaucseRenderer(mistune.HTMLRenderer):
    code_tmpl = '<div class="highlight"><pre><code>{}</code></pre></div>'

    def __init__(self, convert_url, *args, escape=False, **kwargs):
        self._convert_url = convert_url
        super().__init__(*args, **kwargs, escape=False)

    def naucse_admonition(self, text, title, name):
        if title:
            text = f'<p class="admonition-title">{title}</p>\n{text}'
        return '<div class="admonition {}">{}</div>'.format(name, text)

    def heading(self, text, level, raw=None):
        header_id = text_to_id(text)
        return f'''<h{level:d} id="{header_id}">{text}
<a href="#{header_id}" class="header-link">#</a>
</h{level:d}>\n'''

    def block_code(self, code, info=None):
        lang = info
        if lang is not None:
            lang = lang.strip()
        if not lang or lang == 'plain':
            escaped = mistune.escape(code)
            return self.code_tmpl.format(escaped)
        if lang == 'ansi':
            converted = ansi_convert(code)
            return self.code_tmpl.format(converted)
        lexer = get_lexer_by_name(lang)
        html = pygments.highlight(code, lexer, pygments_formatter).strip()
        html = style_space_after_prompt(html)
        return html

    def link(self, text, url, title=None):
        return super().link(text, self._convert_url(url), title)

    def image(self, alt, url, title=None):
        return super().image(alt, self._convert_url(url), title)


def convert_markdown(text, convert_url=None, *, inline=False):
    convert_url = convert_url if convert_url else lambda x: x

    text = dedent(text)

    markdown = mistune.create_markdown(
        plugins=['def_list', naucse_admonition_plugin],
        renderer=NaucseRenderer(convert_url),
    )
    result = markdown(text).strip()

    if inline and result.startswith('<p>') and result.endswith('</p>'):
        result = result[len('<p>'):-len('</p>')]

    return Markup(result)
