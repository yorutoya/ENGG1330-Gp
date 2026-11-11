# Python `curses`: Function Reference and Usage Guide

## 1. Scope and reference version

The Python module is named **`curses`**, not `curse`. It supports character-cell terminal interfaces: drawing text, reading keys, managing windows, and controlling screen updates.

This English guide inventories the public functions and window methods available in this project's **CPython 3.15.0** environment. It also covers the public APIs of `curses.ascii`, `curses.panel`, and `curses.textpad`. It excludes private implementation helpers and C-library functions that Python does not expose. Some APIs depend on the Python version, the linked curses implementation, and the terminal. A complete inventory for this version is not a promise that every function exists on every installation.

The API descriptions and examples below are an independently written reference, checked against the installed module's signatures and help information. Official references for version-specific details are the [Python curses documentation](https://docs.python.org/3.15/library/curses.html), [ASCII utilities](https://docs.python.org/3.15/library/curses.ascii.html), and [panel documentation](https://docs.python.org/3.15/library/curses.panel.html).

**Project dependencies:** the game imports `curses` only, plus its own modules. The companion modules described here are optional learning material; writing this guide does not add them to the game.

## 2. Essential conventions

- Coordinates are **`(y, x)`**, meaning **row first, column second**. The upper-left cell is `(0, 0)`.
- Coordinates passed to a window's drawing methods are normally relative to that window. APIs using screen-relative coordinates are identified below.
- In signatures, square brackets indicate optional arguments; do not type the brackets in a real call. For example, `addstr([y, x,] text[, attr])` supports `win.addstr("Hi")` and `win.addstr(2, 4, "Hi", curses.A_BOLD)`.
- `win` means a window returned by `curses.newwin()` or the `stdscr` passed to a wrapper callback. `pad` means a window created by `curses.newpad()`.
- `attr` combines display attributes and color pairs with bitwise OR: `curses.A_BOLD | curses.color_pair(1)`.
- Most drawing operations change an in-memory window. Call `refresh()`, or `noutrefresh()` followed by `doupdate()`, to display changes.
- Many operations require initialization. A successful `import curses` alone does not initialize a terminal.
- A function that fails commonly raises `curses.error`. Check coordinates and terminal capabilities rather than suppressing every error.
- Unless a return value is identified, use a function for its side effect rather than testing its result as a Boolean.

## 3. A complete starter program

Save this example separately if you want to run it. It uses only `curses`, confines drawing to the top-left 80x24 area, and pauses movement when the terminal is smaller.

```python
import curses


def draw_text(screen, y, x, message, attr=0):
    rows, cols = screen.getmaxyx()
    rows, cols = min(rows, 24), min(cols, 80)
    if 0 <= y < rows and 0 <= x < cols - 1:
        screen.addnstr(y, x, message, cols - x - 1, attr)


def run(screen):
    screen.keypad(True)
    curses.noecho()
    try:
        curses.curs_set(0)
    except curses.error:
        pass  # Some terminals cannot change cursor visibility.

    style = curses.A_BOLD
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        style |= curses.color_pair(1)

    y, x = 10, 20
    directions = {
        curses.KEY_UP: (-1, 0), curses.KEY_DOWN: (1, 0),
        curses.KEY_LEFT: (0, -1), curses.KEY_RIGHT: (0, 1),
    }
    while True:
        rows, cols = screen.getmaxyx()
        ready = rows >= 24 and cols >= 80
        for row in range(min(rows, 24)):
            draw_text(screen, row, 0, " " * 79)

        if ready:
            draw_text(screen, 2, 5, "CURSES DEMO", style)
            draw_text(screen, y, x, "@", style)
            draw_text(screen, 22, 5, "Arrows: move    Q: quit")
        else:
            draw_text(screen, 0, 0, "Resize to 80x24. Q: quit.")
        screen.refresh()

        key = screen.getch()
        if key in (ord("q"), ord("Q"), 27):
            return
        if not ready or key == curses.KEY_RESIZE:
            continue
        dy, dx = directions.get(key, (0, 0))
        y = max(5, min(20, y + dy))
        x = max(5, min(73, x + dx))


if __name__ == "__main__":
    curses.wrapper(run)
```

Run it in an interactive terminal. `curses.wrapper()` restores normal terminal settings when the callback returns or raises an exception. Avoid ordinary `print()` calls while curses owns the display.

## 4. All core module functions

These tables use the prefix `curses.`. Examples are individual calls, not independent runnable programs. They assume appropriate initialization and valid arguments. Input-mode examples describe alternatives; do not enable every mode at once.

### 4.1 Initialization, shutdown, and terminal state

| Function | Purpose and usage |
| --- | --- |
| `wrapper(func, *args, **kwargs)` | Initialize curses, call `func(stdscr, ...)`, and restore terminal settings afterward. Preferred entry: `curses.wrapper(run)`. Returns the callback's result. |
| `initscr()` | Initialize the screen manually and return `stdscr`: `screen = curses.initscr()`. Manual setup requires reliable cleanup. |
| `endwin()` | Restore the terminal from curses mode: `curses.endwin()`. Usually managed by `wrapper`. |
| `isendwin()` | Check whether curses is currently in the ended state: `ended = curses.isendwin()`. |
| `setupterm(term=None, fd=-1)` | Initialize terminal capability access without creating a screen: `curses.setupterm()`. `term` selects a terminal description; `fd` selects the output descriptor. |
| `def_prog_mode()` | Save current terminal modes as the program state, for later `reset_prog_mode()`. |
| `def_shell_mode()` | Save current terminal modes as the shell state, for later `reset_shell_mode()`. |
| `reset_prog_mode()` | Restore the state saved with `def_prog_mode()`. Useful when returning from temporary shell interaction. |
| `reset_shell_mode()` | Restore the state saved with `def_shell_mode()`. |
| `savetty()` | Save a terminal-mode snapshot: `curses.savetty()`. |
| `resetty()` | Restore the snapshot saved by `savetty()`. |
| `filter()` | Restrict curses to a single-line interface. Call before initialization; it is unsuitable for this game's full-screen layout. |
| `use_env(flag)` | Choose whether initialization uses environment-based dimensions. Call before `initscr()`, for example `curses.use_env(False)`. |

### 4.2 Input modes, input queues, and timing

| Function | Purpose and usage |
| --- | --- |
| `cbreak()` | Make keys available without waiting for Enter while retaining terminal signal processing. |
| `nocbreak()` | Leave cbreak mode. |
| `raw()` | Use immediate input and bypass more terminal processing, including normal interpretation of interrupt characters. |
| `noraw()` | Leave raw mode. |
| `echo()` | Let curses echo typed characters during input. |
| `noecho()` | Disable automatic echo so the application can draw its own input field. |
| `halfdelay(tenths)` | Wait up to 1-255 tenths of a second for input: `curses.halfdelay(5)` waits at most half a second. `nocbreak()` leaves this mode. |
| `meta(flag)` | Select whether terminal input preserves the eighth bit: `curses.meta(True)`. This is not a general Unicode-enabling switch. |
| `nl()` | Enable newline/carriage-return translation in terminal I/O. |
| `nonl()` | Disable that translation. |
| `intrflush(flag)` | Control output-queue flushing when an interrupt key is processed: `curses.intrflush(False)`. |
| `qiflush([flag])` | Enable terminal queue flushing for interrupt, quit, or suspend input; a false flag disables it. |
| `noqiflush()` | Disable that queue flushing. |
| `flushinp()` | Discard pending input. Useful when deliberately abandoning buffered keystrokes, not on every frame. |
| `ungetch(ch)` | Push one integer or character back for a later `getch()`: `curses.ungetch(ord("q"))`. Do not assume an unlimited pushback queue. |
| `unget_wch(ch)` | Push a Unicode character for a later `get_wch()`: `curses.unget_wch("A")`. |
| `typeahead(fd)` | Select the descriptor checked for pending input during screen updates. `curses.typeahead(-1)` disables this optimization. |
| `get_escdelay()` | Read the Escape-sequence disambiguation delay in milliseconds. |
| `set_escdelay(ms)` | Set that delay, for example `curses.set_escdelay(50)`. Very short values can misread slowly arriving special-key sequences. |
| `get_tabsize()` | Read the tab expansion width. |
| `set_tabsize(size)` | Set the tab expansion width: `curses.set_tabsize(4)`. |
| `napms(ms)` | Sleep for a number of milliseconds: `curses.napms(100)`. It blocks the calling thread. |
| `delay_output(ms)` | Request a delay in terminal output: `curses.delay_output(100)`. Prefer input timeouts or `napms()` for application timing. |

`getch()` returns `-1` when no key arrives in a nonblocking or timed read. The string-returning input methods raise `curses.error` in that situation. Window-level timeouts are described in Section 5.

### 4.3 Windows, screen updates, resizing, and cursor state

| Function | Purpose and usage |
| --- | --- |
| `newwin(nlines, ncols[, begin_y, begin_x])` | Create a window: `win = curses.newwin(10, 30, 3, 5)`. Zero dimensions can extend toward the screen boundary. |
| `newpad(nlines, ncols)` | Create an off-screen buffer that may exceed the screen: `pad = curses.newpad(100, 70)`. Display a rectangle with pad-specific refresh arguments. |
| `getwin(file)` | Reconstruct a window saved with `win.putwin(file)`. Use a compatible binary file; this is not the game's logical save format. |
| `doupdate()` | Apply pending virtual-screen changes to the terminal. Call after one or more `noutrefresh()` operations. |
| `curs_set(visibility)` | Set cursor visibility to 0, 1, or 2; return its previous visibility. Unsupported modes can raise `curses.error`. |
| `getsyx()` | Return the virtual-screen cursor `(y, x)`; `(-1, -1)` represents the leave-cursor-unspecified state. |
| `setsyx(y, x)` | Set that virtual cursor: `curses.setsyx(2, 5)`. `(-1, -1)` allows curses to leave it unspecified. |
| `is_term_resized(nlines, ncols)` | Test whether resizing to the requested dimensions would change the curses screen structures. |
| `resize_term(nlines, ncols)` | Perform low-level curses screen resizing. This does not resize the user's terminal application. |
| `resizeterm(nlines, ncols)` | Resize curses' standard screen structures and update related bookkeeping. Independent windows may still need resizing. |
| `update_lines_cols()` | Update the module's `LINES` and `COLS` values. Use `win.getmaxyx()` for a particular window's dimensions. |

For this project, a resize event should trigger a size check and pause below 80x24; it should not enlarge the playable area.

### 4.4 Colors and attributes

| Function | Purpose and usage |
| --- | --- |
| `has_colors()` | Ask whether the terminal supports colors before configuring them. |
| `start_color()` | Initialize color handling. `wrapper()` normally attempts this, but explicit initialization is common in setup code. |
| `can_change_color()` | Test whether the terminal permits redefining palette entries. |
| `has_extended_color_support()` | Test whether this Python/curses build supports extended color operations. Also respect terminal limits and each API's limits. |
| `init_pair(pair, fg, bg)` | Define a foreground/background pair: `curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)`. Normally use positive pair numbers. |
| `color_pair(pair)` | Produce the drawing attribute for a pair: `style = curses.color_pair(1)`. This attribute interface supports the first 256 pairs. |
| `pair_content(pair)` | Read a pair's foreground/background numbers: `fg, bg = curses.pair_content(1)`. |
| `pair_number(attr)` | Extract a pair number from an attribute value: `pair = curses.pair_number(style)`. |
| `init_color(color, r, g, b)` | Redefine a palette entry with components in 0-1000, if supported. Example: `curses.init_color(1, 1000, 300, 0)`. |
| `color_content(color)` | Return a palette entry's `(r, g, b)` components. |
| `use_default_colors()` | Permit `-1` for the terminal's default foreground/background, where supported. Useful for retaining the terminal background. |
| `assume_default_colors(fg, bg)` | Enable default colors and redefine pair zero's defaults. Example: `curses.assume_default_colors(-1, -1)`. Introduced in Python 3.14. |
| `termattrs()` | Return a bitmask describing supported display attributes. |

Always retain a readable monochrome style. A terminal may ignore or approximate attributes such as dim, blink, or italic.

### 4.5 Keyboard identification and terminal characteristics

| Function | Purpose and usage |
| --- | --- |
| `has_key(ch)` | Ask whether a special key is recognized by the current terminal description: `curses.has_key(curses.KEY_F1)`. |
| `keyname(k)` | Return a byte-string name for an input code: `curses.keyname(curses.KEY_UP)`. |
| `erasechar()` | Return the terminal's configured erase character as bytes. |
| `killchar()` | Return its configured line-kill character as bytes. |
| `unctrl(ch)` | Return a byte-string display form of a character, including control notation: `curses.unctrl(3)` represents Ctrl-C. |
| `baudrate()` | Return the reported terminal output speed; mostly useful for historical terminal behavior. |
| `has_ic()` | Report terminal insert/delete-character capability. |
| `has_il()` | Report terminal insert/delete-line capability. |
| `longname()` | Return the terminal description's long name as bytes. |
| `termname()` | Return the terminal type name as bytes. |
| `beep()` | Request an audible alert; the terminal may render it differently or ignore it. |
| `flash()` | Request a visual alert. |

### 4.6 Mouse input

| Function | Purpose and usage |
| --- | --- |
| `mousemask(mask)` | Request mouse events and return `(available_mask, previous_mask)`: `curses.mousemask(curses.ALL_MOUSE_EVENTS)`. |
| `getmouse()` | After `KEY_MOUSE`, retrieve `(id, x, y, z, bstate)`. Notice that this tuple places **x before y**. |
| `ungetmouse(id, x, y, z, bstate)` | Queue a mouse event, for example with `curses.BUTTON1_CLICKED`. |
| `mouseinterval(ms)` | Set the click recognition interval in milliseconds and return its previous value. |

Mouse support depends on the terminal. Inspect `available_mask`; a request does not guarantee every event will be delivered.

### 4.7 Low-level terminfo access

| Function | Purpose and usage |
| --- | --- |
| `tigetflag(capname)` | Read a Boolean capability: `curses.tigetflag("am")`. Returns `-1` for an invalid Boolean capability name. |
| `tigetnum(capname)` | Read a numeric capability: `curses.tigetnum("colors")`. `-1` means unavailable; `-2` means the name is not a numeric capability. |
| `tigetstr(capname)` | Read a byte-string capability, or `None` when unavailable: `curses.tigetstr("cup")`. |
| `tparm(capability, *parameters)` | Substitute numeric parameters into a capability: `curses.tparm(cup, 2, 4)`. The interface accepts up to nine parameters. |
| `putp(capability)` | Emit a byte-string capability to standard output. Use deliberately: direct output can disagree with curses' screen model. |

Example for inspecting a capability outside a full-screen application:

```python
import curses

curses.setupterm()
cup = curses.tigetstr("cup")
if cup is not None:
    sequence = curses.tparm(cup, 2, 4)
    # `sequence` is the terminal-specific byte sequence for this position.
    print(repr(sequence))
```

## 5. All window and pad methods

A window is created by curses; do not instantiate `curses.window` directly. Most methods also apply to pads, but pad refresh operations require a source position and a destination rectangle.

### 5.1 Writing, inserting, deleting, and reading cells

| Method | Purpose and usage |
| --- | --- |
| `win.addch([y, x,] ch[, attr])` | Write one character and advance the cursor: `win.addch(2, 3, "@", curses.A_BOLD)`. |
| `win.addstr([y, x,] text[, attr])` | Write a string: `win.addstr(1, 2, "Inventory")`. Explicitly limit width if it must stay on one line. |
| `win.addnstr([y, x,] text, n[, attr])` | Write at most `n` characters: `win.addnstr(1, 2, label, 20)`. Unicode character count is not necessarily terminal-cell width. |
| `win.echochar(ch[, attr])` | Write one character and immediately refresh. Useful for isolated output, less efficient for full frames. |
| `win.insch([y, x,] ch[, attr])` | Insert one character at the cursor; shift the rest of the row right and discard overflow. |
| `win.insstr([y, x,] text[, attr])` | Insert a string without ordinary cursor advancement; displaced right-edge content is lost. |
| `win.insnstr([y, x,] text, n[, attr])` | Insert a limited string: `win.insnstr(2, 2, "CODE", 3)`. For this method, zero or negative `n` means the whole string. |
| `win.delch([y, x])` | Delete a character and shift the remaining row left: `win.delch(2, 2)`. |
| `win.deleteln()` | Delete the cursor's line and move lower lines upward. |
| `win.insertln()` | Insert a blank line at the cursor and move lower lines downward. |
| `win.insdelln(n)` | Insert `n` lines when positive or delete `abs(n)` lines when negative. |
| `win.inch([y, x])` | Return an integer combining a cell's character and attributes: `cell = win.inch(1, 2)`. Use attribute masks when inspecting it. |
| `win.instr([y, x,] n=2047)` | Read up to `n` bytes of displayed text, without attributes: `data = win.instr(1, 2, 20)`. Returns bytes. |

Writing into the lower-right cell can raise `curses.error` even when the cell was drawn, because cursor advancement would cross the boundary. This game avoids the last column instead of relying on that behavior.

### 5.2 Borders, lines, backgrounds, and attributes

| Method | Purpose and usage |
| --- | --- |
| `win.border([ls, rs, ts, bs, tl, tr, bl, br])` | Draw all four borders and corners. Zero arguments use default line characters. Example: `win.border()`. |
| `win.box([verch, horch])` | Draw a simple border: `win.box()` or `win.box(ord("\|"), ord("-"))`. |
| `win.hline([y, x,] ch, n[, attr])` | Draw `n` horizontal cells: `win.hline(3, 2, "-", 15)`. |
| `win.vline([y, x,] ch, n[, attr])` | Draw `n` vertical cells: `win.vline(2, 3, "\|", 5)`. |
| `win.attron(attr)` | Add attributes for subsequent output: `win.attron(curses.A_BOLD)`. |
| `win.attroff(attr)` | Remove selected attributes from subsequent output: `win.attroff(curses.A_BOLD)`. |
| `win.attrset(attr)` | Replace the current output attributes: `win.attrset(curses.A_NORMAL)`. |
| `win.chgat([y, x,] [n,] attr)` | Change attributes of existing cells: `win.chgat(2, 3, 8, curses.A_REVERSE)`. Omitted `n`, or `-1`, covers the rest of the row. |
| `win.standout()` | Enable standout mode for subsequent output. |
| `win.standend()` | Disable standout; some terminals also clear other attributes. |
| `win.bkgd(ch[, attr])` | Set the background and apply the change to existing window contents: `win.bkgd(" ", curses.color_pair(1))`. |
| `win.bkgdset(ch[, attr])` | Set the background used by subsequent operations without repainting existing contents immediately. |
| `win.getbkgd()` | Read the background character/attribute value. |

### 5.3 Erasing, refreshing, and redraw bookkeeping

| Method | Purpose and usage |
| --- | --- |
| `win.erase()` | Replace window contents with background blanks. A later refresh displays the change. |
| `win.clear()` | Erase and request a complete screen repaint at the next refresh. |
| `win.clrtoeol()` | Erase from the cursor through the end of its line. |
| `win.clrtobot()` | Erase from the cursor through the rest of the window. |
| `win.refresh()` | Update the terminal from this window. Pad form: `pad.refresh(pminrow, pmincol, sminrow, smincol, smaxrow, smaxcol)`. |
| `win.noutrefresh()` | Merge this window into the virtual screen without immediate terminal output. Pads take the same six viewport arguments as their `refresh()`. |
| `win.clearok(flag)` | Request a full screen repaint on the next refresh when true. |
| `win.immedok(flag)` | Automatically refresh after changes when true. Usually leave false for frame-based games. |
| `win.redrawwin()` | Mark the entire window as needing a redraw after external display corruption. |
| `win.redrawln(beg, num)` | Mark a range of lines for redraw: `win.redrawln(2, 3)`. |
| `win.touchwin()` | Mark the whole window changed, even if curses has not detected content changes. |
| `win.touchline(start, count[, changed=True])` | Mark a line range changed or unchanged: `win.touchline(1, 4)`. |
| `win.untouchwin()` | Mark all lines unchanged since the previous refresh. |
| `win.is_linetouched(line)` | Test whether a particular line is marked changed. |
| `win.is_wintouched()` | Test whether any part of the window is marked changed. |

`erase()` and `clear()` operate on the entire window. For this project's fixed area inside a larger terminal, the production drawing helper clears only the allowed rows and columns instead.

### 5.4 Keyboard input and blocking behavior

| Method | Purpose and usage |
| --- | --- |
| `win.getch([y, x])` | Read an integer key code; return `-1` when a nonblocking or timed read has no input. |
| `win.getkey([y, x])` | Read a string: an ordinary character or a name such as `"KEY_UP"`. No available input raises `curses.error`. It is not the preferred Unicode input API. |
| `win.get_wch([y, x])` | Read a Unicode character as `str`, or a special key as an integer. No available input raises `curses.error`. |
| `win.getstr([y, x,] [n])` | Read an editable line and return bytes. Supply a limit, for example `win.getstr(3, 2, 20)`. The installed version defaults to 2047. |
| `win.keypad(flag)` | Enable decoding of special keys: `win.keypad(True)` lets arrows arrive as `KEY_UP`, etc. |
| `win.nodelay(flag)` | Select nonblocking input when true; false restores blocking input. |
| `win.timeout(delay)` | Set input wait in milliseconds: negative blocks indefinitely, zero polls, positive waits up to that duration. |
| `win.notimeout(flag)` | Disable Escape-sequence timeout when true. This affects sequence interpretation, not the ordinary input wait set by `timeout()`. |

Do not combine `echo()` and a custom input renderer accidentally. The production `read_command()` function draws characters itself, imposes a length limit, and supports hints and notebook access.

### 5.5 Geometry, cursor position, subwindows, and pads

| Method | Purpose and usage |
| --- | --- |
| `win.getyx()` | Return the cursor's window-relative `(y, x)`. |
| `win.getbegyx()` | Return the window's upper-left screen position. |
| `win.getmaxyx()` | Return `(height, width)`, not the highest valid indices. |
| `win.getparyx()` | Return a subwindow's position relative to its parent, or `(-1, -1)` without a parent. |
| `win.move(y, x)` | Move the window's cursor without moving the window itself. |
| `win.mvwin(y, x)` | Move the window's upper-left corner to a screen position. |
| `win.mvderwin(y, x)` | Change which parent-buffer region a derived window displays while retaining its screen position. |
| `win.resize(nlines, ncols)` | Resize this window: `win.resize(8, 30)`. Recheck its position and contents afterward. |
| `win.enclose(y, x)` | Test whether a **screen-relative** point lies within the window; useful for mouse hit testing. |
| `win.derwin([nlines, ncols,] begin_y, begin_x)` | Create a child sharing parent storage; its origin is **parent-relative**. Example: `child = win.derwin(3, 20, 1, 1)`. |
| `win.subwin([nlines, ncols,] begin_y, begin_x)` | Create a shared-storage child using a **screen-relative** origin. |
| `pad.subpad([nlines, ncols,] begin_y, begin_x)` | Create a shared-storage child within a pad; coordinates address the parent pad's space, not its displayed viewport. |
| `win.leaveok(flag)` | Allow refresh to leave the terminal cursor wherever convenient. This does not guarantee that the cursor is hidden. |

A window also exposes **`win.encoding`**, an encoding-name attribute used for text conversion. It is an attribute, not a method. Keep character encodings distinct from terminal-cell widths.

### 5.6 Scrolling, copying, synchronization, and serialization

| Method | Purpose and usage |
| --- | --- |
| `win.scroll([lines=1])` | Move contents upward for positive counts or downward for negative counts. Enable scrolling first when required. |
| `win.scrollok(flag)` | Permit automatic scrolling at the bottom when true. This game keeps scrolling disabled. |
| `win.setscrreg(top, bottom)` | Restrict scrolling to an inclusive row interval. |
| `win.idcok(flag)` | Permit curses to use terminal insert/delete-character optimizations. |
| `win.idlok(flag)` | Permit terminal insert/delete-line optimizations. |
| `win.overlay(destwin[, sminrow, smincol, dminrow, dmincol, dmaxrow, dmaxcol])` | Copy a region while preserving destination cells beneath source background cells. Example: `win.overlay(other)`. |
| `win.overwrite(destwin[, sminrow, smincol, dminrow, dmincol, dmaxrow, dmaxcol])` | Copy a region including its background: `win.overwrite(other)`. Explicit destination ending coordinates are inclusive. |
| `win.syncup()` | Propagate this window's changed-region markers to its ancestors. |
| `win.syncdown()` | Bring ancestor changed-region markers into this window; refresh normally performs this as needed. |
| `win.syncok(flag)` | Automatically call `syncup()` after changes when true. |
| `win.cursyncup()` | Propagate this window's cursor position to its ancestors. |
| `win.putwin(file)` | Write window state to a binary file for `curses.getwin()`. This is implementation-dependent screen serialization, not portable gameplay persistence. |

## 6. Constants, attributes, and exceptions

Constants are data rather than functions. Their availability can vary; some appear only after screen or color initialization.

| Group | Examples and meaning |
| --- | --- |
| Text styles | `A_NORMAL`, `A_BOLD`, `A_DIM`, `A_REVERSE`, `A_UNDERLINE`, `A_BLINK`, `A_STANDOUT`, `A_INVIS`, `A_PROTECT`, `A_ALTCHARSET`; additional styles depend on the build. |
| Cell masks | `A_CHARTEXT` extracts character bits, `A_ATTRIBUTES` extracts attribute bits, and `A_COLOR` selects color bits. |
| Basic colors | `COLOR_BLACK`, `COLOR_RED`, `COLOR_GREEN`, `COLOR_YELLOW`, `COLOR_BLUE`, `COLOR_MAGENTA`, `COLOR_CYAN`, `COLOR_WHITE`. |
| Color limits | `COLORS` and `COLOR_PAIRS` describe supported counts after color setup. |
| Screen dimensions | `LINES` and `COLS` describe the curses screen; `getmaxyx()` describes a particular window. |
| Navigation keys | `KEY_UP`, `KEY_DOWN`, `KEY_LEFT`, `KEY_RIGHT`, `KEY_HOME`, `KEY_END`, `KEY_NPAGE`, `KEY_PPAGE`. |
| Editing and function keys | `KEY_BACKSPACE`, `KEY_DC`, `KEY_IC`, `KEY_ENTER`, `KEY_F0`, `KEY_F1`, and further supported function-key constants. |
| Event keys | `KEY_RESIZE` requests size handling; `KEY_MOUSE` indicates a queued mouse event. |
| Mouse masks | `BUTTON1_PRESSED`, `BUTTON1_RELEASED`, `BUTTON1_CLICKED`, `BUTTON1_DOUBLE_CLICKED`, corresponding supported buttons, modifier masks, `ALL_MOUSE_EVENTS`, `REPORT_MOUSE_POSITION`. |
| Line-drawing cells | `ACS_HLINE`, `ACS_VLINE`, `ACS_ULCORNER`, `ACS_URCORNER`, `ACS_LLCORNER`, `ACS_LRCORNER`, `ACS_PLUS`, and other `ACS_*` symbols. |
| Build information | `version` identifies the module as bytes; `ncurses_version`, when available, identifies the linked ncurses version. |
| Status values | `ERR` represents failure for integer-returning operations; `OK` represents success. |
| Error type | `curses.error` is raised for failed curses operations. |

For Enter, account for `10`, `13`, and `curses.KEY_ENTER` as needed. Backspace can arrive as `8`, `127`, or `KEY_BACKSPACE`. Escape is commonly `27`; Tab is `9`.

To inspect all constant names on your installation, run after initialization when needed:

```python
names = sorted(name for name in dir(curses) if name.isupper())
```

## 7. Related standard-library modules

### 7.1 `curses.ascii`: every public function

Import explicitly with `import curses.ascii`. These helpers classify ASCII values, not arbitrary Unicode letters. Classification functions accept an integer or a one-character string. All entries below take one argument `c`.

| Function | Test or transformation | Example |
| --- | --- | --- |
| `isalnum(c)` | ASCII letter or decimal digit | `curses.ascii.isalnum("A")` |
| `isalpha(c)` | ASCII letter | `curses.ascii.isalpha("z")` |
| `isascii(c)` | Value within seven-bit ASCII | `curses.ascii.isascii(127)` |
| `isblank(c)` | Space or horizontal tab | `curses.ascii.isblank("\t")` |
| `iscntrl(c)` | Control value 0-31 or DEL at 127 | `curses.ascii.iscntrl(127)` |
| `isctrl(c)` | Control value 0-31, excluding DEL | `curses.ascii.isctrl(3)` |
| `isdigit(c)` | Decimal digit | `curses.ascii.isdigit("7")` |
| `isgraph(c)` | Visible ASCII character other than space | `curses.ascii.isgraph("!")` |
| `islower(c)` | Lowercase ASCII letter | `curses.ascii.islower("a")` |
| `ismeta(c)` | Value at least 128 | `curses.ascii.ismeta(128)` |
| `isprint(c)` | Printable ASCII, including space | `curses.ascii.isprint(" ")` |
| `ispunct(c)` | Printable non-space, non-alphanumeric ASCII | `curses.ascii.ispunct("?")` |
| `isspace(c)` | ASCII whitespace | `curses.ascii.isspace("\n")` |
| `isupper(c)` | Uppercase ASCII letter | `curses.ascii.isupper("A")` |
| `isxdigit(c)` | Hexadecimal digit | `curses.ascii.isxdigit("F")` |
| `ascii(c)` | Keep the low seven bits | `curses.ascii.ascii(193)` |
| `ctrl(c)` | Keep the low five bits | `curses.ascii.ctrl("G")` |
| `alt(c)` | Set bit 7 | `curses.ascii.alt("A")` |
| `unctrl(c)` | Return readable control notation as a string | `curses.ascii.unctrl(3)` |

`ascii()`, `ctrl()`, and `alt()` preserve whether the input is an integer or a character string. Constants include `NUL`, `BEL`, `BS`, `TAB`, `LF`, `CR`, `ESC`, `SP`, and `DEL`.

### 7.2 `curses.panel`: every public function and panel method

Import explicitly with `import curses.panel`. Panels provide stacking for overlapping windows. Keep a Python reference to each panel or it may disappear when garbage-collected. Refresh with `curses.panel.update_panels()` followed by `curses.doupdate()`. [Official panel reference](https://docs.python.org/3.15/library/curses.panel.html).

| Function or method | Usage |
| --- | --- |
| `curses.panel.new_panel(win)` | Create a panel around `win`. |
| `curses.panel.bottom_panel()` | Get the bottom panel, or `None` for an empty stack. |
| `curses.panel.top_panel()` | Get the top panel, or `None` for an empty stack. |
| `curses.panel.update_panels()` | Recompose visible panels into the virtual screen. |
| `panel.above()` | Get the panel above, or `None`. |
| `panel.below()` | Get the panel below, or `None`. |
| `panel.bottom()` | Move to the bottom. |
| `panel.top()` | Move to the top. |
| `panel.hide()` | Hide without deleting. |
| `panel.show()` | Show at the top. |
| `panel.hidden()` | Check visibility state. |
| `panel.move(y, x)` | Move the associated window using screen coordinates. |
| `panel.replace(win)` | Associate a different window. |
| `panel.window()` | Retrieve the associated window. |
| `panel.set_userptr(obj)` | Attach application data. |
| `panel.userptr()` | Retrieve attached data. |

Create panel objects with `new_panel()`, not by directly constructing `curses.panel.panel`. Operations can raise `curses.panel.error`.

### 7.3 `curses.textpad`: every public callable

Import explicitly with `from curses import textpad`. It supplies a basic terminal text editor. The project's custom input helper remains more suitable for its fixed limits and notebook commands.

| Callable | Purpose and usage |
| --- | --- |
| `textpad.rectangle(win, uly, ulx, lry, lrx)` | Draw a rectangle using inclusive upper-left and lower-right coordinates. |
| `textpad.Textbox(win, insert_mode=False)` | Create an editor using the supplied window. `insert_mode=True` shifts existing text on insertion. |
| `box.edit(validate=None)` | Run editing and return collected text. An optional callback transforms integer input codes; returning zero ignores a key. |
| `box.do_command(ch)` | Process one integer input code; return a false value when editing should terminate. Useful in a custom event loop. |
| `box.gather()` | Collect current window text without running the editing loop. |

`box.stripspaces` controls trailing-space handling and related cursor behavior; it is an attribute, not a function. The documented Textbox interface is covered in the [textpad section of the curses reference](https://docs.python.org/3.15/library/curses.html#module-curses.textpad).

Common editing commands:

| Key | Action |
| --- | --- |
| Ctrl-A / Ctrl-E | Move to the start / end of the line. |
| Ctrl-B / Ctrl-F | Move left / right; arrow keys also work. |
| Ctrl-P / Ctrl-N | Move up / down; arrow keys also work. |
| Ctrl-D | Delete under the cursor. |
| Ctrl-H | Delete backward. |
| Ctrl-G | Finish editing. |
| Ctrl-J | Finish a one-line editor; move to the next line in a multiline editor. |
| Ctrl-K | Clear to line end, or delete a blank line at its start. |
| Ctrl-L | Refresh the editor. |
| Ctrl-O | Insert a blank line. |

## 8. Practical patterns

These snippets belong inside an initialized curses callback unless explicitly stated otherwise. Check that the requested windows fit before creating them.

### 8.1 Update several windows together

```python
# Assume the terminal is at least 80x24.
left = curses.newwin(8, 30, 4, 5)
right = curses.newwin(8, 30, 4, 40)
left.box()
right.box()
left.addstr(2, 2, "Journal")
right.addstr(2, 2, "Expedition")
left.noutrefresh()
right.noutrefresh()
curses.doupdate()
```

For overlapping windows, use panels or explicitly manage draw order and changed-region markers. Independent windows do not automatically behave like stacked layers.

### 8.2 Show a viewport into a larger pad

```python
# Assume the terminal is at least 80x24.
pad = curses.newpad(100, 70)
for row in range(100):
    pad.addstr(row, 0, f"Record {row + 1}")

# Source begins at row 10, column 0.
# Destination rectangle is rows 4-18, columns 5-64, inclusive.
pad.refresh(10, 0, 4, 5, 18, 64)
```

To scroll, change the source row rather than drawing outside the destination rectangle. Validate both source and destination bounds.

### 8.3 Use timed input without a busy loop

```python
screen.timeout(100)
key = screen.getch()
if key == -1:
    pass  # No input within 100 ms; an application may advance a timed update.
elif key == curses.KEY_RESIZE:
    rows, cols = screen.getmaxyx()
else:
    pass  # Process the key.
screen.timeout(-1)  # Restore blocking input for menus.
```

This is an input timeout, not a guarantee of a constant frame rate. Decide separately when simulation state should advance.

### 8.4 Read mouse clicks

```python
screen.keypad(True)
available, previous = curses.mousemask(curses.ALL_MOUSE_EVENTS)
key = screen.getch()
if key == curses.KEY_MOUSE:
    device, x, y, z, state = curses.getmouse()
    if state & curses.BUTTON1_CLICKED:
        inside_play_area = 0 <= y < 24 and 0 <= x < 80
        # Use (y, x) when passing this position to window methods.
curses.mousemask(previous)
```

### 8.5 Use a small text editor

```python
from curses import textpad

# Inside a curses callback; assume at least 80x24.
entry = curses.newwin(1, 30, 10, 5)
editor = textpad.Textbox(entry)
editor.stripspaces = True
result = editor.edit()  # Enter/Ctrl-J finishes this one-line editor.
```

Textbox takes over input while editing. Integrating pause, resize, and custom shortcuts requires additional handling; it is not a replacement for the game's current input loop by itself.

## 9. How the production game uses curses

| File | Relevant calls and their role |
| --- | --- |
| `main.py` | `wrapper()` owns the session; `keypad()` decodes navigation; `noecho()` disables automatic text echo; `curs_set()` hides the cursor; color calls initialize the theme. |
| `include/interface.py` | `getmaxyx()` checks dimensions, `addnstr()` clips output, `getch()` processes commands, and `refresh()` displays the frame. |
| `include/decipher_3.py` | `napms()` and `timeout()` control circuit input cadence; `KEY_RESIZE` pauses the circuit when needed. |
| `include/decipher_4.py` | Key constants drive movement and device interaction; attributes distinguish crates, doors and terminals. |
| `include/finale.py` | Blocking input keeps the exit challenges turn-based; screen and drawing helpers enforce the viewport. |
| `include/archive.py` | Key constants handle story paging; shared frame helpers retain the same terminal limits. |

The first two puzzles primarily call the project's interface helpers rather than using curses directly. Save and archive files use Python's built-in file operations; curses does not store gameplay progress.

## 10. Common mistakes and corrections

| Problem | Correction |
| --- | --- |
| Text appears at the wrong position | Check `(y, x)` ordering and whether coordinates are window-relative or screen-relative. |
| Drawing succeeds but nothing appears | Refresh the window, or call `doupdate()` after `noutrefresh()`. |
| Arrow keys arrive as several characters | Enable `keypad(True)` on the window that reads input. |
| A menu consumes high CPU | Use blocking input or a positive timeout instead of repeatedly polling with `timeout(0)`. |
| `curses.error` occurs at an edge | Check dimensions, clipping, and the lower-right cursor-advance rule. |
| Input unexpectedly appears twice | Disable automatic echo when drawing typed input yourself. |
| Colors fail | Initialize colors and check capabilities; retain a monochrome fallback. |
| Resizing crashes a window | Recheck bounds on `KEY_RESIZE`, pause or rebuild windows, and avoid stale dimensions. |
| A hidden cursor reappears | `leaveok()` and `curs_set()` have different roles; explicitly request cursor visibility. |
| A character occupies unexpected space | Unicode code points and terminal cells are different units; ASCII is simplest for this game's fixed grid. |
| Output corrupts the interface | Do not mix unmanaged `print()` output with curses screen updates. |
| The terminal remains in an unusual mode after an exception | Start through `curses.wrapper()` so cleanup runs. |
| A window dump is treated as a game save | Persist logical state explicitly, as `savegame.py` does, instead of relying on `putwin()`. |

## 11. Compatibility and further reading

Check the Python version and the actual exported API when moving the project to a different machine. `assume_default_colors()` requires Python 3.14 or later; extended colors and wide-character operations also depend on the build. Python documents curses as an optional module primarily available on Unix platforms. These platform and version details are described in the [official reference](https://docs.python.org/3.15/library/curses.html).

The tables cover every public function and window method in the inspected environment, plus the public helper APIs listed above. They are not an inventory of every function in the underlying C ncurses library, every constant supported by every terminal, or every future Python release.

For the authoritative version-specific specification, use the linked official pages and the built-in `help()` function, for example `help(curses.window.addnstr)`. The installed Python source for `curses.textpad` is also useful when learning how its editing loop works.
