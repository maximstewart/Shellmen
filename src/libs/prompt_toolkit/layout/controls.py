"""
User interface Controls for the layout.
"""
from __future__ import unicode_literals

from abc import ABCMeta, abstractmethod
from collections import namedtuple
from six import with_metaclass
from six.moves import range

from libs.prompt_toolkit.cache import SimpleCache
from libs.prompt_toolkit.enums import DEFAULT_BUFFER, SEARCH_BUFFER
from libs.prompt_toolkit.filters import to_cli_filter
from libs.prompt_toolkit.mouse_events import MouseEventType
from libs.prompt_toolkit.search_state import SearchState
from libs.prompt_toolkit.selection import SelectionType
from libs.prompt_toolkit.token import Token
from libs.prompt_toolkit.utils import get_cwidth

from .lexers import Lexer, SimpleLexer
from .processors import Processor
from .screen import Char, Point
from .utils import token_list_width, split_lines, token_list_to_text

import six
import time


__all__ = (
    'BufferControl',
    'FillControl',
    'TokenListControl',
    'UIControl',
    'UIContent',
)


class UIControl(with_metaclass(ABCMeta, object)):
    """
    Base class for all user interface controls.
    """
    def reset(self):
        # Default reset. (Doesn't have to be implemented.)
        pass

    def preferred_width(self, cli, max_available_width):
        return None

    def preferred_height(self, cli, width, max_available_height, wrap_lines):
        return None

    def has_focus(self, cli):
        """
        Return ``True`` when this user control has the focus.

        If so, the cursor will be displayed according to the cursor position
        reported by :meth:`.UIControl.create_content`. If the created content
        has the property ``show_cursor=False``, the cursor will be hidden from
        the output.
        """
        return False

    @abstractmethod
    def create_content(self, cli, width, height):
        """
        Generate the content for this user control.

        Returns a :class:`.UIContent` instance.
        """

    def mouse_handler(self, cli, mouse_event):
        """
        Handle mouse events.

        When `NotImplemented` is returned, it means that the given event is not
        handled by the `UIControl` itself. The `Window` or key bindings can
        decide to handle this event as scrolling or changing focus.

        :param cli: `CommandLineInterface` instance.
        :param mouse_event: `MouseEvent` instance.
        """
        return NotImplemented

    def move_cursor_down(self, cli):
        """
        Request to move the cursor down.
        This happens when scrolling down and the cursor is completely at the
        top.
        """

    def move_cursor_up(self, cli):
        """
        Request to move the cursor up.
        """


class UIContent(object):
    """
    Content generated by a user control. This content consists of a list of
    lines.

    :param get_line: Callable that returns the current line. This is a list of
        (Token, text) tuples.
    :param line_count: The number of lines.
    :param cursor_position: a :class:`.Point` for the cursor position.
    :param menu_position: a :class:`.Point` for the menu position.
    :param show_cursor: Make the cursor visible.
    :param default_char: The default :class:`.Char` for filling the background.
    """
    def __init__(self, get_line=None, line_count=0,
                 cursor_position=None, menu_position=None, show_cursor=True,
                 default_char=None):
        assert callable(get_line)
        assert isinstance(line_count, six.integer_types)
        assert cursor_position is None or isinstance(cursor_position, Point)
        assert menu_position is None or isinstance(menu_position, Point)
        assert default_char is None or isinstance(default_char, Char)

        self.get_line = get_line
        self.line_count = line_count
        self.cursor_position = cursor_position or Point(0, 0)
        self.menu_position = menu_position
        self.show_cursor = show_cursor
        self.default_char = default_char

        # Cache for line heights. Maps (lineno, width) -> height.
        self._line_heights = {}

    def __getitem__(self, lineno):
        " Make it iterable (iterate line by line). "
        if lineno < self.line_count:
            return self.get_line(lineno)
        else:
            raise IndexError

    def get_height_for_line(self, lineno, width):
        """
        Return the height that a given line would need if it is rendered in a
        space with the given width.
        """
        try:
            return self._line_heights[lineno, width]
        except KeyError:
            text = token_list_to_text(self.get_line(lineno))
            result = self.get_height_for_text(text, width)

            # Cache and return
            self._line_heights[lineno, width] = result
            return result

    @staticmethod
    def get_height_for_text(text, width):
        # Get text width for this line.
        line_width = get_cwidth(text)

        # Calculate height.
        try:
            quotient, remainder = divmod(line_width, width)
        except ZeroDivisionError:
            # Return something very big.
            # (This can happen, when the Window gets very small.)
            return 10 ** 10
        else:
            if remainder:
                quotient += 1  # Like math.ceil.
            return max(1, quotient)


class TokenListControl(UIControl):
    """
    Control that displays a list of (Token, text) tuples.
    (It's mostly optimized for rather small widgets, like toolbars, menus, etc...)

    Mouse support:

        The list of tokens can also contain tuples of three items, looking like:
        (Token, text, handler). When mouse support is enabled and the user
        clicks on this token, then the given handler is called. That handler
        should accept two inputs: (CommandLineInterface, MouseEvent) and it
        should either handle the event or return `NotImplemented` in case we
        want the containing Window to handle this event.

    :param get_tokens: Callable that takes a `CommandLineInterface` instance
        and returns the list of (Token, text) tuples to be displayed right now.
    :param default_char: default :class:`.Char` (character and Token) to use
        for the background when there is more space available than `get_tokens`
        returns.
    :param get_default_char: Like `default_char`, but this is a callable that
        takes a :class:`libs.prompt_toolkit.interface.CommandLineInterface` and
        returns a :class:`.Char` instance.
    :param has_focus: `bool` or `CLIFilter`, when this evaluates to `True`,
        this UI control will take the focus. The cursor will be shown in the
        upper left corner of this control, unless `get_token` returns a
        ``Token.SetCursorPosition`` token somewhere in the token list, then the
        cursor will be shown there.
    """
    def __init__(self, get_tokens, default_char=None, get_default_char=None,
                 align_right=False, align_center=False, has_focus=False):
        assert callable(get_tokens)
        assert default_char is None or isinstance(default_char, Char)
        assert get_default_char is None or callable(get_default_char)
        assert not (default_char and get_default_char)

        self.align_right = to_cli_filter(align_right)
        self.align_center = to_cli_filter(align_center)
        self._has_focus_filter = to_cli_filter(has_focus)

        self.get_tokens = get_tokens

        # Construct `get_default_char` callable.
        if default_char:
            get_default_char = lambda _: default_char
        elif not get_default_char:
            get_default_char = lambda _: Char(' ', Token.Transparent)

        self.get_default_char = get_default_char

        #: Cache for the content.
        self._content_cache = SimpleCache(maxsize=18)
        self._token_cache = SimpleCache(maxsize=1)
            # Only cache one token list. We don't need the previous item.

        # Render info for the mouse support.
        self._tokens = None

    def reset(self):
        self._tokens = None

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.get_tokens)

    def _get_tokens_cached(self, cli):
        """
        Get tokens, but only retrieve tokens once during one render run.
        (This function is called several times during one rendering, because
        we also need those for calculating the dimensions.)
        """
        return self._token_cache.get(
            cli.render_counter, lambda: self.get_tokens(cli))

    def has_focus(self, cli):
        return self._has_focus_filter(cli)

    def preferred_width(self, cli, max_available_width):
        """
        Return the preferred width for this control.
        That is the width of the longest line.
        """
        text = token_list_to_text(self._get_tokens_cached(cli))
        line_lengths = [get_cwidth(l) for l in text.split('\n')]
        return max(line_lengths)

    def preferred_height(self, cli, width, max_available_height, wrap_lines):
        content = self.create_content(cli, width, None)
        return content.line_count

    def create_content(self, cli, width, height):
        # Get tokens
        tokens_with_mouse_handlers = self._get_tokens_cached(cli)

        default_char = self.get_default_char(cli)

        # Wrap/align right/center parameters.
        right = self.align_right(cli)
        center = self.align_center(cli)

        def process_line(line):
            " Center or right align a single line. "
            used_width = token_list_width(line)
            padding = width - used_width
            if center:
                padding = int(padding / 2)
            return [(default_char.token, default_char.char * padding)] + line

        if right or center:
            token_lines_with_mouse_handlers = []

            for line in split_lines(tokens_with_mouse_handlers):
                token_lines_with_mouse_handlers.append(process_line(line))
        else:
            token_lines_with_mouse_handlers = list(split_lines(tokens_with_mouse_handlers))

        # Strip mouse handlers from tokens.
        token_lines = [
            [tuple(item[:2]) for item in line]
            for line in token_lines_with_mouse_handlers
        ]

        # Keep track of the tokens with mouse handler, for later use in
        # `mouse_handler`.
        self._tokens = tokens_with_mouse_handlers

        # If there is a `Token.SetCursorPosition` in the token list, set the
        # cursor position here.
        def get_cursor_position():
            SetCursorPosition = Token.SetCursorPosition

            for y, line in enumerate(token_lines):
                x = 0
                for token, text in line:
                    if token == SetCursorPosition:
                        return Point(x=x, y=y)
                    x += len(text)
            return None

        # Create content, or take it from the cache.
        key = (default_char.char, default_char.token,
                tuple(tokens_with_mouse_handlers), width, right, center)

        def get_content():
            return UIContent(get_line=lambda i: token_lines[i],
                             line_count=len(token_lines),
                             default_char=default_char,
                             cursor_position=get_cursor_position())

        return self._content_cache.get(key, get_content)

    @classmethod
    def static(cls, tokens):
        def get_static_tokens(cli):
            return tokens
        return cls(get_static_tokens)

    def mouse_handler(self, cli, mouse_event):
        """
        Handle mouse events.

        (When the token list contained mouse handlers and the user clicked on
        on any of these, the matching handler is called. This handler can still
        return `NotImplemented` in case we want the `Window` to handle this
        particular event.)
        """
        if self._tokens:
            # Read the generator.
            tokens_for_line = list(split_lines(self._tokens))

            try:
                tokens = tokens_for_line[mouse_event.position.y]
            except IndexError:
                return NotImplemented
            else:
                # Find position in the token list.
                xpos = mouse_event.position.x

                # Find mouse handler for this character.
                count = 0
                for item in tokens:
                    count += len(item[1])
                    if count >= xpos:
                        if len(item) >= 3:
                            # Handler found. Call it.
                            # (Handler can return NotImplemented, so return
                            # that result.)
                            handler = item[2]
                            return handler(cli, mouse_event)
                        else:
                            break

        # Otherwise, don't handle here.
        return NotImplemented


class FillControl(UIControl):
    """
    Fill whole control with characters with this token.
    (Also helpful for debugging.)

    :param char: :class:`.Char` instance to use for filling.
    :param get_char: A callable that takes a CommandLineInterface and returns a
        :class:`.Char` object.
    """
    def __init__(self, character=None, token=Token, char=None, get_char=None):  # 'character' and 'token' parameters are deprecated.
        assert char is None or isinstance(char, Char)
        assert get_char is None or callable(get_char)
        assert not (char and get_char)

        self.char = char

        if character:
            # Passing (character=' ', token=token) is deprecated.
            self.character = character
            self.token = token

            self.get_char = lambda cli: Char(character, token)
        elif get_char:
            # When 'get_char' is given.
            self.get_char = get_char
        else:
            # When 'char' is given.
            self.char = self.char or Char()
            self.get_char = lambda cli: self.char
            self.char = char

    def __repr__(self):
        if self.char:
            return '%s(char=%r)' % (self.__class__.__name__, self.char)
        else:
            return '%s(get_char=%r)' % (self.__class__.__name__, self.get_char)

    def reset(self):
        pass

    def has_focus(self, cli):
        return False

    def create_content(self, cli, width, height):
        def get_line(i):
            return []

        return UIContent(
            get_line=get_line,
            line_count=100 ** 100,  # Something very big.
            default_char=self.get_char(cli))


_ProcessedLine = namedtuple('_ProcessedLine', 'tokens source_to_display display_to_source')


class BufferControl(UIControl):
    """
    Control for visualising the content of a `Buffer`.

    :param input_processors: list of :class:`~libs.prompt_toolkit.layout.processors.Processor`.
    :param lexer: :class:`~libs.prompt_toolkit.layout.lexers.Lexer` instance for syntax highlighting.
    :param preview_search: `bool` or `CLIFilter`: Show search while typing.
    :param get_search_state: Callable that takes a CommandLineInterface and
        returns the SearchState to be used. (If not CommandLineInterface.search_state.)
    :param buffer_name: String representing the name of the buffer to display.
    :param default_char: :class:`.Char` instance to use to fill the background. This is
        transparent by default.
    :param focus_on_click: Focus this buffer when it's click, but not yet focussed.
    """
    def __init__(self,
                 buffer_name=DEFAULT_BUFFER,
                 input_processors=None,
                 lexer=None,
                 preview_search=False,
                 search_buffer_name=SEARCH_BUFFER,
                 get_search_state=None,
                 menu_position=None,
                 default_char=None,
                 focus_on_click=False):
        assert input_processors is None or all(isinstance(i, Processor) for i in input_processors)
        assert menu_position is None or callable(menu_position)
        assert lexer is None or isinstance(lexer, Lexer)
        assert get_search_state is None or callable(get_search_state)
        assert default_char is None or isinstance(default_char, Char)

        self.preview_search = to_cli_filter(preview_search)
        self.get_search_state = get_search_state
        self.focus_on_click = to_cli_filter(focus_on_click)

        self.input_processors = input_processors or []
        self.buffer_name = buffer_name
        self.menu_position = menu_position
        self.lexer = lexer or SimpleLexer()
        self.default_char = default_char or Char(token=Token.Transparent)
        self.search_buffer_name = search_buffer_name

        #: Cache for the lexer.
        #: Often, due to cursor movement, undo/redo and window resizing
        #: operations, it happens that a short time, the same document has to be
        #: lexed. This is a faily easy way to cache such an expensive operation.
        self._token_cache = SimpleCache(maxsize=8)

        self._xy_to_cursor_position = None
        self._last_click_timestamp = None
        self._last_get_processed_line = None

    def _buffer(self, cli):
        """
        The buffer object that contains the 'main' content.
        """
        return cli.buffers[self.buffer_name]

    def has_focus(self, cli):
        # This control gets the focussed if the actual `Buffer` instance has the
        # focus or when any of the `InputProcessor` classes tells us that it
        # wants the focus. (E.g. in case of a reverse-search, where the actual
        # search buffer may not be displayed, but the "reverse-i-search" text
        # should get the focus.)
        return cli.current_buffer_name == self.buffer_name or \
            any(i.has_focus(cli) for i in self.input_processors)

    def preferred_width(self, cli, max_available_width):
        """
        This should return the preferred width.

        Note: We don't specify a preferred width according to the content,
              because it would be too expensive. Calculating the preferred
              width can be done by calculating the longest line, but this would
              require applying all the processors to each line. This is
              unfeasible for a larger document, and doing it for small
              documents only would result in inconsistent behaviour.
        """
        return None

    def preferred_height(self, cli, width, max_available_height, wrap_lines):
        # Calculate the content height, if it was drawn on a screen with the
        # given width.
        height = 0
        content = self.create_content(cli, width, None)

        # When line wrapping is off, the height should be equal to the amount
        # of lines.
        if not wrap_lines:
            return content.line_count

        # When the number of lines exceeds the max_available_height, just
        # return max_available_height. No need to calculate anything.
        if content.line_count >= max_available_height:
            return max_available_height

        for i in range(content.line_count):
            height += content.get_height_for_line(i, width)

            if height >= max_available_height:
                return max_available_height

        return height

    def _get_tokens_for_line_func(self, cli, document):
        """
        Create a function that returns the tokens for a given line.
        """
        # Cache using `document.text`.
        def get_tokens_for_line():
            return self.lexer.lex_document(cli, document)

        return self._token_cache.get(document.text, get_tokens_for_line)

    def _create_get_processed_line_func(self, cli, document):
        """
        Create a function that takes a line number of the current document and
        returns a _ProcessedLine(processed_tokens, source_to_display, display_to_source)
        tuple.
        """
        def transform(lineno, tokens):
            " Transform the tokens for a given line number. "
            source_to_display_functions = []
            display_to_source_functions = []

            # Get cursor position at this line.
            if document.cursor_position_row == lineno:
                cursor_column = document.cursor_position_col
            else:
                cursor_column = None

            def source_to_display(i):
                """ Translate x position from the buffer to the x position in the
                processed token list. """
                for f in source_to_display_functions:
                    i = f(i)
                return i

            # Apply each processor.
            for p in self.input_processors:
                transformation = p.apply_transformation(
                    cli, document, lineno, source_to_display, tokens)
                tokens = transformation.tokens

                if cursor_column:
                    cursor_column = transformation.source_to_display(cursor_column)

                display_to_source_functions.append(transformation.display_to_source)
                source_to_display_functions.append(transformation.source_to_display)

            def display_to_source(i):
                for f in reversed(display_to_source_functions):
                    i = f(i)
                return i

            return _ProcessedLine(tokens, source_to_display, display_to_source)

        def create_func():
            get_line = self._get_tokens_for_line_func(cli, document)
            cache = {}

            def get_processed_line(i):
                try:
                    return cache[i]
                except KeyError:
                    processed_line = transform(i, get_line(i))
                    cache[i] = processed_line
                    return processed_line
            return get_processed_line

        return create_func()

    def create_content(self, cli, width, height):
        """
        Create a UIContent.
        """
        buffer = self._buffer(cli)

        # Get the document to be shown. If we are currently searching (the
        # search buffer has focus, and the preview_search filter is enabled),
        # then use the search document, which has possibly a different
        # text/cursor position.)
        def preview_now():
            """ True when we should preview a search. """
            return bool(self.preview_search(cli) and
                        cli.buffers[self.search_buffer_name].text)

        if preview_now():
            if self.get_search_state:
                ss = self.get_search_state(cli)
            else:
                ss = cli.search_state

            document = buffer.document_for_search(SearchState(
                text=cli.current_buffer.text,
                direction=ss.direction,
                ignore_case=ss.ignore_case))
        else:
            document = buffer.document

        get_processed_line = self._create_get_processed_line_func(cli, document)
        self._last_get_processed_line = get_processed_line

        def translate_rowcol(row, col):
            " Return the content column for this coordinate. "
            return Point(y=row, x=get_processed_line(row).source_to_display(col))

        def get_line(i):
            " Return the tokens for a given line number. "
            tokens = get_processed_line(i).tokens

            # Add a space at the end, because that is a possible cursor
            # position. (When inserting after the input.) We should do this on
            # all the lines, not just the line containing the cursor. (Because
            # otherwise, line wrapping/scrolling could change when moving the
            # cursor around.)
            tokens = tokens + [(self.default_char.token, ' ')]
            return tokens

        content = UIContent(
            get_line=get_line,
            line_count=document.line_count,
            cursor_position=translate_rowcol(document.cursor_position_row,
                                             document.cursor_position_col),
            default_char=self.default_char)

        # If there is an auto completion going on, use that start point for a
        # pop-up menu position. (But only when this buffer has the focus --
        # there is only one place for a menu, determined by the focussed buffer.)
        if cli.current_buffer_name == self.buffer_name:
            menu_position = self.menu_position(cli) if self.menu_position else None
            if menu_position is not None:
                assert isinstance(menu_position, int)
                menu_row, menu_col = buffer.document.translate_index_to_position(menu_position)
                content.menu_position = translate_rowcol(menu_row, menu_col)
            elif buffer.complete_state:
                # Position for completion menu.
                # Note: We use 'min', because the original cursor position could be
                #       behind the input string when the actual completion is for
                #       some reason shorter than the text we had before. (A completion
                #       can change and shorten the input.)
                menu_row, menu_col = buffer.document.translate_index_to_position(
                    min(buffer.cursor_position,
                        buffer.complete_state.original_document.cursor_position))
                content.menu_position = translate_rowcol(menu_row, menu_col)
            else:
                content.menu_position = None

        return content

    def mouse_handler(self, cli, mouse_event):
        """
        Mouse handler for this control.
        """
        buffer = self._buffer(cli)
        position = mouse_event.position

        # Focus buffer when clicked.
        if self.has_focus(cli):
            if self._last_get_processed_line:
                processed_line = self._last_get_processed_line(position.y)

                # Translate coordinates back to the cursor position of the
                # original input.
                xpos = processed_line.display_to_source(position.x)
                index = buffer.document.translate_row_col_to_index(position.y, xpos)

                # Set the cursor position.
                if mouse_event.event_type == MouseEventType.MOUSE_DOWN:
                    buffer.exit_selection()
                    buffer.cursor_position = index

                elif mouse_event.event_type == MouseEventType.MOUSE_UP:
                    # When the cursor was moved to another place, select the text.
                    # (The >1 is actually a small but acceptable workaround for
                    # selecting text in Vi navigation mode. In navigation mode,
                    # the cursor can never be after the text, so the cursor
                    # will be repositioned automatically.)
                    if abs(buffer.cursor_position - index) > 1:
                        buffer.start_selection(selection_type=SelectionType.CHARACTERS)
                        buffer.cursor_position = index

                    # Select word around cursor on double click.
                    # Two MOUSE_UP events in a short timespan are considered a double click.
                    double_click = self._last_click_timestamp and time.time() - self._last_click_timestamp < .3
                    self._last_click_timestamp = time.time()

                    if double_click:
                        start, end = buffer.document.find_boundaries_of_current_word()
                        buffer.cursor_position += start
                        buffer.start_selection(selection_type=SelectionType.CHARACTERS)
                        buffer.cursor_position += end - start
                else:
                    # Don't handle scroll events here.
                    return NotImplemented

        # Not focussed, but focussing on click events.
        else:
            if self.focus_on_click(cli) and mouse_event.event_type == MouseEventType.MOUSE_UP:
                # Focus happens on mouseup. (If we did this on mousedown, the
                # up event will be received at the point where this widget is
                # focussed and be handled anyway.)
                cli.focus(self.buffer_name)
            else:
                return NotImplemented

    def move_cursor_down(self, cli):
        b = self._buffer(cli)
        b.cursor_position += b.document.get_cursor_down_position()

    def move_cursor_up(self, cli):
        b = self._buffer(cli)
        b.cursor_position += b.document.get_cursor_up_position()