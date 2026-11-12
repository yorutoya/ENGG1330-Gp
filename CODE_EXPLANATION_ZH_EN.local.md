[中文 / English — 打开可切换语言的阅读页面](CODE_EXPLANATION_ZH_EN.local.html)

# UNDERGROUND — 中英对照代码说明 / Bilingual Code Guide

本地学习与视频讲解用，按 2026-11-08 当前代码编写。覆盖全部 10 个 Python 文件的函数、方法及关键模块级逻辑；较长函数按执行阶段解释。行号对应编写时版本，之后改代码可能变化。说明解释当前实现，不代表所有路径都已经测试通过。

For local study and video preparation, based on the source inspected on 2026-11-08. This guide covers functions, methods, and key module-level logic in all ten Python files. Long functions are explained by execution stage. Line numbers may change with later edits. Describing behavior does not imply every path has been tested.

## 1. 整体流程 / Overall flow

```text
curses.wrapper(main)
  → map / 地图
  → mirror / 镜像 → shift
  → drawer / 抽屉 → order + badges
  → circuit / 电路（可选 optional）→ sequence
  → gate / 门禁 → radio + committed branch
  → Relay / Corridor / Shaft → escaped
  → Archive → hidden story / 隐藏剧情
```

**中文**

- 主程序负责流程，interface 负责通用终端交互，expedition 负责资源规则，四个 decipher 文件实现关卡，finale 实现最终挑战，savegame 与 archive 分别保存当前局和跨局收藏。
- 第三关可跳过，但会影响第四关供电模式和最终挑战。

**English**

- The main controller manages progression; interface provides terminal helpers; expedition owns resource rules; the four decipher modules implement rooms; finale implements exit challenges. savegame and archive persist the current run and cross-run achievements separately.
- Skipping room three changes gate power and the finale.

### 1.1 建议阅读顺序 / Suggested reading order

1. **先看 `main.py`。** 找到 `PUZZLES` 和主循环，理解“地图选择 → 调用关卡 → 根据返回值更新进度”。
   **Start with `main.py`.** Follow map selection, the puzzle call, and the completion result.
2. **再看前两关。** 它们展示最简单的模式：读取答案、检查答案、写入线索。
   **Read rooms one and two next.** They demonstrate input, answer checking, and clue updates.
3. **接着看 `expedition.py` 和 `interface.py`。** 分别理解资源扣除和界面绘制。
   **Then read the resource and UI helpers.** They explain shared costs and screen handling.
4. **最后看移动关卡、结局和存档。** 先理解状态字段，再读改变这些字段的方法。
   **Finish with movement puzzles, endings, and saving.** Understand their state before their actions.

### 1.2 用一次操作理解程序 / Follow one action

以第一关输入正确答案为例：

1. `main.py` 调用 `decipher_1.main(screen, clues)`。
2. 关卡通过 `read_command()` 获取文字；`check_command()` 判断答案。
3. 答案正确后执行 `clues['shift'] = 7`，把偏移量交给后续关卡。
4. 关卡返回 `True`，主程序才把对应的 `solved` 标记改为 `True`。

For a correct room-one answer: the controller calls the room, the input helper
reads the command, the room stores offset 7 in the shared dictionary, and its
`True` result tells the controller to mark the room complete. **Storing a clue
and marking a room complete are two separate operations.**

### 1.3 第四关：两个顺序、三种对象 / Understanding room four

| 容易混淆的内容 / Term | 中文解释 | English explanation |
| --- | --- | --- |
| 箱子 A、B / Crates | 地图中能推动的物体，放在 a、b 上供电 | Movable map objects that press floor plates |
| 徽章 A、C、V / Badges | 第二关得到的数字，只用于算密码 | Drawer numbers used in code calculations |
| 终端顺序 / Terminal order | 决定先去哪个终端，例如 2 → 3 → 1 | Determines which terminal to visit next |
| 终端密码 / Terminal code | 决定在某个终端输入哪个数字 | Determines the number to enter at that terminal |
| 房间 3 的供电 / Mains power | 完成第三关获得，允许使用正常供电路线 | Completing room three enables the mains-powered route |
| `gate.powered` | 当前所需的箱子是否仍压在对应机关上 | Whether the required crates currently press their plates |

**计算示例 / Worked example:** 假设徽章 A=10、C=50、V=80，offset=7，则终端
1 的密码是 17，终端 2 是 43，终端 3 是 94。如果当前顺序是 2 → 3 → 1，
就先去终端 2 输入 43，再去 3 输入 94，最后去 1 输入 17。
这是解释规则的例子，每局应使用笔记中的实际数字与顺序。

With badges A=10, C=50, V=80 and offset=7, the codes are 17, 43 and 94 for
terminals 1, 2 and 3 respectively. An order of 2 → 3 → 1 means entering 43 at
terminal 2, then 94 at terminal 3, then 17 at terminal 1. Use the actual
numbers and order from the current run rather than memorizing this example.

**设备与按键 / Symbols and keys:** 地图中的 O 是无线电，F 是警报开关。
移动到设备旁后按键盘 E 才会操作。地图上的 E 则表示出口；走到出口和按 E 键不是一回事。

O and F are map devices, operated with the E key when nearby. The E shown on
the map is the exit: walking onto it is different from pressing the E key.

### 1.4 三种返回值不能混用 / Three different return conventions

| 接口 / Interface | 返回值 / Result | 含义 / Meaning |
| --- | --- | --- |
| `read_command()` | 文本或 `None` / text or `None` | 提交的答案或取消 / submitted input or cancellation |
| 关卡 `main()` / room entry | `True` 或 `False` | 是否完成该关 / whether the room was completed |
| 最终挑战 `act()` / finale action | `'failure'` 或 `None` | 是否需要公共循环扣资源；胜利另看 `won` / whether to charge a failure; success is tracked by `won` |

`False` 不表示什么都没发生。例如答错后退出关卡，返回值虽然是 `False`，电池已经扣除。
A `False` result does not roll back state: leaving after a wrong answer still keeps the cell loss.

## 2. 共享数据与生命周期 / Shared data and lifetime

| 数据 / Data | 中文说明 | English explanation |
| --- | --- | --- |
| screen | curses 窗口对象，负责绘制和读取按键 | Curses window used for drawing and keyboard input |
| clues | 当前局共享字典；各关卡原地写入取得的线索 | Shared run dictionary updated in place by rooms |
| seed / condition | 生成变化细节及环境条件 | Generate puzzle variation and sector conditions |
| cells / bonus_charge / fuse / modules | 整局资源；与电路 charge、竖井 energy 区分 | Run resources, distinct from circuit charge and shaft energy |
| shift / order / badges | 前两关提供的偏移量、颜色顺序及徽章 | Offset, color order, and badges recovered from the first two rooms |
| sequence | 由完成电路取得的终端顺序，也作为正常供电证据 | Terminal order obtained by completing the circuit; also evidence of mains power |
| solved | 四个布尔值，索引 0–3 对应房间 1–4 | Four completion flags; indices 0–3 represent rooms 1–4 |
| selected | 地图选项；0–3 为房间，4 为新局按钮 | Map selection; 0–3 are rooms and 4 is the new-run button |
| radio | idle、sent 或 cut；门禁通关时写回共享数据 | Radio action committed to shared state when the gate is completed |
| finale_kind / exit_room / escaped | 固定路线、保留的最终挑战对象和真正逃脱标志 | Committed branch, retained finale object, and completed-escape flag |
| collection | 独立 Archive 对象；新局与载入不清空收藏 | Separate Archive object, retained across run resets and loads |

**中文**

- 普通关卡 main 返回 True 表示完成，False 表示未完成，不表示资源未变化。
- 文本输入返回 None 表示取消。
- 最终挑战 act 返回 'failure' 由公共循环扣资源，是否获胜另看 won。
- 不要混淆这些返回约定。

**English**

- A room main returns True for completion and False otherwise; False does not mean resources were unchanged.
- Text input returns None for cancellation.
- Finale act reports 'failure' to the common loop, while won indicates success.
- These return conventions serve different purposes.

## 3. 逐文件与函数说明 / File and function walkthrough

### 3.1 `main.py`

**模块级代码 / Module-level code**

**中文**

- PUZZLES 保存函数对象，索引选中后直接调用；TITLES 与之对齐。
- ROOM_POSITIONS/ROOM_LABELS 只是地图显示数据。
- 文件末尾 __name__ 判断只在直接运行时启动 curses.wrapper，正常退出或异常时由 wrapper 恢复终端。

**English**

- PUZZLES stores callable functions aligned with TITLES.
- ROOM_POSITIONS and ROOM_LABELS are display data.
- The __name__ guard starts curses.wrapper only on direct execution; the wrapper restores terminal settings on exit or error.

#### `new_clues`

<details>
<summary>查看源代码 / View source — main.py · L13–L17</summary>

```python
def new_clues(previous_seed=None):
    # Built-in hash varies between Python processes; no extra library needed.
    # Advance within a session so restarting always changes the badge set.
    seed = hash('underground-access') % 8000 if previous_seed is None else (previous_seed + 137) % 8000
    return new_run(seed)
```

</details>

**中文**

- 首次用字符串哈希生成 0–7999 的种子；重开时将旧种子加 137 后取模，再调用 new_run。
- 意义：集中创建一局数据，并让新一局的徽章等内容变化；哈希跨进程可能不同，不是固定随机种子。

**English**

- Creates a seed from a string hash on first launch, or advances the previous seed by 137 modulo 8000, then calls new_run.
- This centralizes run creation and varies puzzle details.
- The hash may differ between processes.

#### `available`

<details>
<summary>查看源代码 / View source — main.py · L21–L31</summary>

```python
def available(stage, solved, clues):
    """After finding the drawer key, either remaining room is accessible."""
    if clues.get('cells', 3) <= 0:
        return False
    if solved[3]:
        return solved[stage]
    if stage == 0:
        return True
    if stage == 1:
        return solved[0]
    return solved[1]
```

</details>

**中文**

- 先检查电池，再检查是否已过门禁，最后检查前置房间。
- 第一关直接开放，第二关需要第一关，第三、四关都只需要第二关。
- 过门禁后只能访问已完成的房间。
- 意义：允许绕过电路，同时防止路线确定后回头改变供电条件。

**English**

- Checks cells, gate completion, and prerequisites in that order.
- Room 1 is initially available; room 2 requires room 1; both rooms 3 and 4 require room 2.
- After the gate, only completed rooms remain accessible.
- This permits the battery route while preserving the committed branch.

#### `ending`

<details>
<summary>查看源代码 / View source — main.py · L35–L41</summary>

```python
def ending(clues):
    # Outcomes follow completed work and actual room actions, not a route menu.
    if 'sequence' not in clues:
        return 'LAST LIGHT'
    if clues.get('radio') == 'sent':
        return 'DAWN'
    return 'SILENT EXIT'
```

</details>

**中文**

- 没有 sequence 则返回 LAST LIGHT；有 sequence 且 radio 为 sent 则返回 DAWN；其余为 SILENT EXIT。
- 意义：用实际供电和无线电行为推导结局，而不是让玩家直接选结局。

**English**

- Returns LAST LIGHT without sequence, DAWN with restored power and a sent radio call, otherwise SILENT EXIT.
- Endings follow gameplay state rather than an ending-selection menu.

#### `show_ending`

<details>
<summary>查看源代码 / View source — main.py · L45–L73</summary>

```python
def show_ending(screen, clues):
    result = clues.get('finale_kind', ending(clues))
    if result == 'DAWN':
        messages = [
            'You step into daylight. A rescue team answers',
            'the coordinates you transmitted from the gate.',
            'Restored power keeps the evacuation route open.',
        ]
    elif result == 'SILENT EXIT':
        messages = [
            'The facility hums behind you as you reach daylight.',
            'No rescue signal was transmitted.',
            'You leave the powered facility without an escort.',
        ]
        if clues.get('radio') == 'cut':
            messages.append('The isolated alarm feed has silenced the radio.')
    else:
        messages = [
            'The spare battery dies as you reach daylight.',
            'The gate closes. The rescue radio stays silent.',
            'You escaped, but the facility remains offline.',
        ]
    fragments = {
        'DAWN': 'Your evacuation log preserves a fragment of an unknown voice.',
        'SILENT EXIT': 'Your scanner log contains part of a missing crew roster.',
        'LAST LIGHT': 'The lift recorder saves an unlisted shelter location.',
    }
    messages.extend(['', fragments[result]])
    notice(screen, 'ENDING / ' + result, clues, messages)
```

</details>

**中文**

- 根据已固定的 finale_kind（缺省时重新判断）选择故事文字，并加入对应的故事碎片，最后调用 notice。
- 意义：把结局展示与通关、收藏写入分开。

**English**

- Selects narrative text using the committed finale_kind, falling back to ending(), adds a story fragment, and calls notice.
- Presentation is separate from completion and collection updates.

#### `visit_exit`

<details>
<summary>查看源代码 / View source — main.py · L77–L97</summary>

```python
def visit_exit(screen, clues, collection=None):
    # The gate fixes the branch; returning to the map cannot choose another ending.
    kind = clues.setdefault('finale_kind', ending(clues))
    if clues.get('escaped') or finale.play(screen, clues, kind):
        clues['escaped'] = True
        unlocked = collection.record(kind) if collection is not None else False
        show_ending(screen, clues)
        if unlocked:
            archive.show_story(screen, clues)
        if collection is not None and collection.error:
            return collection.error
        if unlocked:
            return 'All records recovered. [V] Archive replays the hidden transmission.'
        return 'EXPEDITION COMPLETE. Start again to explore the facility.'
    if clues.get('cells', 3) <= 0:
        notice(screen, 'EXPEDITION LOST', clues, [
            'Your emergency cells are exhausted.',
            'The last passage remains sealed. Start a new expedition.',
        ])
        return 'RUN OVER. Start a new expedition to try again.'
    return 'Exit passage unfinished. Select the gate to resume where you left off.'
```

</details>

**中文**

- setdefault 只在第一次进入时确定 finale_kind。
- 已逃出或 finale.play 成功时设置 escaped、记录结局并显示故事；刚集齐三种结局则展示隐藏剧情。
- 失败后区分电池耗尽与暂时返回地图。
- 意义：路线不随返回地图改变，收藏只在真正完成最终挑战后增加。

**English**

- Uses setdefault to commit the branch once.
- On an existing or newly completed escape, it sets escaped, records the ending, and displays the narrative; newly collecting all endings opens the hidden story.
- Otherwise it distinguishes resource exhaustion from a temporary return.
- Re-entry cannot change the branch or award an unfinished ending.

#### `navigate`

<details>
<summary>查看源代码 / View source — main.py · L106–L111</summary>

```python
def navigate(selected, direction):
    # Neighbours in left, right, up, down order. No wrap across the map edges.
    neighbours = ((0, 1, 0, 4), (0, 2, 2, 3), (1, 2, 2, 3),
                  (1, 3, 2, 3), (4, 1, 0, 4))
    directions = ((-1, 0), (1, 0), (0, -1), (0, 1))
    return neighbours[selected][directions.index(direction)]
```

</details>

**中文**

- 用邻接表保存五个可选项在左、右、上、下方向的目标索引，边缘指向自身。
- 意义：地图导航与屏幕坐标解耦，不必为每个按键写长串条件。

**English**

- Uses an adjacency table for the five selections and four directions.
- Edge movements point back to the same item.
- Navigation is independent of screen coordinates and avoids repeated conditionals.

#### `draw_map`

<details>
<summary>查看源代码 / View source — main.py · L115–L156</summary>

```python
def draw_map(screen, selected, solved, clues):
    dim = curses.A_DIM
    active = curses.color_pair(1)
    text(screen, 5, 5, 'ACCESS WING', dim)
    text(screen, 6, 5, 'Restore lighting. Find the key.', dim)

    # Solid corridors show accessible connections; dots show locked passages.
    text(screen, 10, 24, '------' if solved[0] else '......', active if solved[0] else dim)
    text(screen, 10, 49, '---+' if solved[1] else '...+', active if solved[1] else dim)
    for y in range(6, 15):
        text(screen, y, 52, '|' if solved[1] else ':', active if solved[1] else dim)
    text(screen, 10, 52, '+', active if solved[1] else dim)
    for y in (6, 14):
        text(screen, y, 52, '+--' if solved[1] else '+..', active if solved[1] else dim)
    # This is an optional power link, not a lock on the lower branch.
    text(screen, 8, 64, '|' if solved[2] else ':', active if solved[2] else dim)
    text(screen, 9, 64, '|' if solved[2] else ':', active if solved[2] else dim)
    text(screen, 9, 66, 'power', dim)
    text(screen, 10, 64, '|' if solved[2] else ':', active if solved[2] else dim)
    text(screen, 11, 64, 'v', active if solved[2] else dim)

    for i, (x, y) in enumerate(ROOM_POSITIONS):
        state = 'LOCKED'
        if i == 3 and solved[i] and not clues.get('escaped'):
            state = 'EXIT AHEAD'
        elif solved[i]:
            state = 'COMPLETE'
        elif available(i, solved, clues):
            state = 'READY'
        style = active if state != 'LOCKED' else dim
        if i == selected:
            style = curses.color_pair(2) | curses.A_BOLD
        text(screen, y, x, '+' + '-' * 17 + '+', style)
        marker = '>' if i == selected else ' '
        text(screen, y + 1, x, '|' + marker + ROOM_LABELS[i].ljust(16) + '|', style)
        text(screen, y + 2, x, '|' + state.center(17) + '|', style)
        text(screen, y + 3, x, '+' + '-' * 17 + '+', style)

    style = curses.color_pair(2) | curses.A_BOLD if selected == 4 else dim
    text(screen, 15, 5, ('> ' if selected == 4 else '  ') + '[N] New expedition', style)
    text(screen, 17, 5, f'{sum(solved)} / 4 rooms complete', dim)
    text(screen, 17, 39, '[P] Save    [L] Load checkpoint', dim)
```

</details>

**中文**

- 先画走廊和可选电力连线，再为房间计算 LOCKED、READY、COMPLETE 或 EXIT AHEAD，最后画边框、选中效果、完成数量与存档提示。
- 意义：把状态转成视觉反馈，本函数不推进游戏。

**English**

- Draws corridors and the optional power link, derives each room label, then draws boxes, selection styles, completion count, and save hints.
- It visualizes state without advancing gameplay.

#### `main`

<details>
<summary>查看源代码 / View source — main.py · L160–L297</summary>

```python
def main(screen):
    screen.keypad(True)
    curses.noecho()
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    # Each puzzle adds evidence to this dictionary for later puzzles.
    # Shared run data: seed controls variation, cells tracks lives, and modules lists installed rewards.
    # shift/order/badges/sequence store recovered clues; radio tracks rescue contact.
    # exit_room holds the final challenge; escaped becomes True only after completing the escape.
    clues = new_clues()
    # Keep the ending collection separate from clues so resets and checkpoint loads cannot erase it.
    collection = archive.Archive()
    # solved tracks the four rooms; selected is only the current map selection.
    solved = [False] * 4
    selected = 0
    message = 'Start at the mirror console to restore emergency lighting.'
    while True:
        screen.timeout(-1)
        controls = 'Arrows: select  1-4: room  Enter: open  Tab: notes  N: new  Q: quit'
        ready = frame(screen, 'FACILITY MAP / SELECT A ROOM', clues, controls)
        if ready:
            descriptions = (
                'Inspect the mirror panel and restore lighting.',
                'Decode the drawer; inspect its numbered badges.',
                'Route coloured energy nodes to restore power.',
                'Explore the gate, radio and alarm equipment.',
                'Clear this expedition and generate new badges.',
            )
            draw_map(screen, selected, solved, clues)
            text(screen, 15, 30, f'[V] Archive {len(collection.completed)}/3', curses.color_pair(1))
            description = descriptions[selected]
            if selected == 3 and solved[3] and not clues.get('escaped'):
                description = 'Resume the exit passage beyond the open security gate.'
            line(screen, 18, description, curses.color_pair(1))
            text(screen, 20, 5, message, curses.color_pair(2))
            screen.refresh()
        key = screen.getch()
        if key in (27, ord('q'), ord('Q')):
            return
        if not ready:
            continue
        if key in (ord('v'), ord('V')):
            archive.show_archive(screen, clues, collection)
            continue
        if key in (ord('p'), ord('P')):
            try:
                savegame.save(clues, solved, selected)
                message = 'Progress saved. You can quit and load it with L next time.'
            except (OSError, ValueError):
                message = 'Could not save progress. Check that the game folder is writable.'
            continue
        if key in (ord('l'), ord('L')):
            try:
                checkpoint = savegame.load()
            except FileNotFoundError:
                message = 'No saved expedition yet. Press P to save your progress.'
            except (OSError, ValueError):
                message = 'Cannot read this checkpoint. Your current expedition is unchanged.'
            else:
                if frame(screen, 'LOAD CHECKPOINT?', clues,
                         'Y: load saved progress    Any other key: cancel'):
                    line(screen, 8, 'Replace this expedition with the saved checkpoint?')
                    line(screen, 10, f'Saved rooms: {sum(checkpoint[1])}/4    Cells: {checkpoint[0]["cells"]}')
                    screen.refresh()
                    if screen.getch() in (ord('y'), ord('Y')):
                        clues, solved, selected = checkpoint
                        message = 'Checkpoint loaded. Continue your expedition.'
                        if clues.get('escaped'):
                            if collection.record(clues['finale_kind']):
                                archive.show_story(screen, clues)
                            if collection.error:
                                message = collection.error
            continue
        if key in (ord('n'), ord('N')):
            selected = 4
            key = 10
        if key == 9:
            show_notes(screen, clues)
        elif ord('1') <= key <= ord('4'):
            selected = key - ord('1')
        elif key in DIRECTIONS:
            selected = navigate(selected, DIRECTIONS[key])
        elif key in (10, 13, curses.KEY_ENTER):
            if selected == 4:
                if not frame(screen, 'RESET EXPEDITION?', clues, 'Y: reset this expedition | Any other key: cancel'):
                    continue
                line(screen, 8, 'Clear all completed systems and recovered clues?')
                line(screen, 10, 'Saved checkpoints and ending records are kept.')
                screen.refresh()
                if screen.getch() in (ord('y'), ord('Y')):
                    clues = new_clues(clues['seed'])
                    solved = [False] * 4
                    selected = 0
                    message = 'New expedition. Start with the mirror console.'
            elif not available(selected, solved, clues):
                message = 'This room is unavailable. Check the earlier systems.'
            elif solved[selected]:
                if selected == 3:
                    message = visit_exit(screen, clues, collection)
                    if clues.get('escaped') or clues.get('cells', 3) <= 0:
                        selected = 4
                    continue
                notice(screen, TITLES[selected].upper() + ' / COMPLETE', clues,
                       ['This system is restored. Its clues are in the journal.',
                        'Continue to the next system from mission control.'])
            # Each puzzle returns whether it was completed; returning False does not refund spent resources.
            elif PUZZLES[selected](screen, clues):
                solved[selected] = True
                if selected in (1, 2):
                    reward(screen, clues, selected)
                message = 'System restored. New evidence added to the journal.'
                if selected == 3:
                    message = visit_exit(screen, clues, collection)
                    if clues.get('escaped') or clues.get('cells', 3) <= 0:
                        selected = 4
                elif selected == 1:
                    selected = 2
                    message = 'The drawer key fits both the energy terminal and the gate.'
                else:
                    selected += 1
            elif clues.get('cells', 3) <= 0:
                notice(screen, 'EXPEDITION LOST', clues, [
                    'Your emergency cells are exhausted.',
                    'The facility seals its remaining systems.', '',
                    'Start a new expedition with a new sector and cache.',
                    'No modules or completed rooms carry into a new run.',
                ])
                selected = 4
                message = 'RUN OVER. Start a new expedition to try again.'
            else:
                message = 'Back at control. Completed systems and clues are kept.'
```

</details>

**中文**

- 初始化 keypad、输入回显、光标和颜色；建立 clues、solved、selected 及独立的 Archive。
- 主循环按“绘制→读键→分派动作”运行。
- P 保存，L 先校验再确认替换，V 查看收藏；N 经确认仅重建当前局。
- Enter 先处理新局、锁定和已完成房间，再调用 PUZZLES 中的函数。
- 关卡返回 True 才标记完成；仅第二、三关完成时给奖励，第四关成功后进入最终挑战。
- 意义：由一个控制器统一掌握进度、资源与页面切换，房间只报告自身是否成功。

**English**

- Initializes terminal input and colors, then creates clues, solved, selected, and a separate Archive.
- The loop draws, reads a key, and dispatches actions.
- P saves; L validates and confirms before replacement; V opens the archive; N confirms and resets only the current run.
- Enter handles reset, access, and completed rooms before calling PUZZLES.
- Only True marks completion; rooms 2 and 3 award salvage, and room 4 leads to the finale.
- One controller owns progression while each room reports its result.

### 3.2 `include/interface.py`

**模块级代码 / Module-level code**

**中文**

- 导入 curses；MIN_ROWS/MIN_COLS 定义视口，CONTENT_WIDTH 定义正文宽度。
- DIRECTIONS 将方向键和小写 WASD 映射为 (dx,dy)，向下是正 y。

**English**

- Imports curses.
- MIN_ROWS/MIN_COLS define the viewport and CONTENT_WIDTH the text width.
- DIRECTIONS maps arrows and lowercase WASD to (dx,dy), with positive y downward.

#### `text`

<details>
<summary>查看源代码 / View source — include/interface.py · L20–L28</summary>

```python
def text(screen, y, x, message, style=0, width=None):
    rows, cols = screen.getmaxyx()
    rows, cols = min(rows, MIN_ROWS), min(cols, MIN_COLS)
    if 0 <= y < rows and 0 <= x < cols - 1:
        limit = cols - x - 1
        if width is not None:
            limit = min(width, limit)
        if limit > 0:
            screen.addnstr(y, x, str(message), limit, style)
```

</details>

**中文**

- 读取屏幕尺寸，限制到左上角 80×24；检查坐标并截断字符串，保留最后一列。
- 意义：共用边界保护，减少越界绘制和自动换行；这是 ASCII 字符布局，不是通用中文字符宽度算法。

**English**

- Clips drawing to the top-left 80×24 area, checks coordinates, truncates text, and leaves the last column unused.
- Shared bounds handling reduces drawing errors and wrapping.
- It assumes an ASCII-style layout rather than general Unicode display widths.

#### `wrap`

<details>
<summary>查看源代码 / View source — include/interface.py · L32–L43</summary>

```python
def wrap(message, width):
    """Word-wrap ASCII text without importing another library."""
    result = []
    remaining = str(message)
    while len(remaining) > width:
        split = remaining.rfind(' ', 0, width + 1)
        if split <= 0:
            split = width
        result.append(remaining[:split])
        remaining = remaining[split:].lstrip()
    result.append(remaining)
    return result
```

</details>

**中文**

- 循环寻找宽度内最后一个空格换行；没有空格时按宽度切开，最后加入剩余文字。
- 意义：让英文提示按词换行，长单词也能显示。
- 调用方应传入正宽度。

**English**

- Wraps at the last space within the width, splits long words when necessary, and appends the remainder.
- English messages fit narrow screens.
- Callers must supply a positive width.

#### `wrap_lines`

<details>
<summary>查看源代码 / View source — include/interface.py · L47–L51</summary>

```python
def wrap_lines(messages, width):
    lines = []
    for message in messages:
        lines.extend(wrap(message, width))
    return lines
```

</details>

**中文**

- 对消息列表逐条调用 wrap，再用 extend 合并结果。
- 意义：复用换行算法，同时保留各条消息的顺序。

**English**

- Applies wrap to every message and extends a combined list.
- This reuses word wrapping while preserving message order.

#### `line`

<details>
<summary>查看源代码 / View source — include/interface.py · L55–L56</summary>

```python
def line(screen, y, message, style=0):
    text(screen, y, 5, message, style, CONTENT_WIDTH)
```

</details>

**中文**

- 将正文统一交给 text，在第 5 列、最大 70 字符宽度内绘制。
- 意义：集中管理正文边距与宽度。

**English**

- Delegates to text using column 5 and a maximum width of 70.
- This keeps body margins and widths consistent.

#### `frame`

<details>
<summary>查看源代码 / View source — include/interface.py · L60–L77</summary>

```python
def frame(screen, title, clues, controls):
    rows, cols = screen.getmaxyx()
    for y in range(min(rows, MIN_ROWS)):
        text(screen, y, 0, ' ' * (MIN_COLS - 1))
    if rows < MIN_ROWS or cols < MIN_COLS:
        for y, message in enumerate(wrap('Paused. Resize to 80 x 24. Q/Esc: back.', max(1, cols - 1))):
            text(screen, y, 0, message)
        screen.refresh()
        return False
    text(screen, 0, 5, 'UNDERGROUND', curses.color_pair(1) | curses.A_BOLD)
    if 'cells' in clues:
        status = f'Cells {clues["cells"]}'
        if clues.get('fuse'):
            status += ' + fuse'
        text(screen, 0, 59, status, curses.color_pair(2))
    line(screen, 2, title, curses.A_BOLD)
    text(screen, 22, 5, controls, curses.A_DIM, width=73)
    return True
```

</details>

**中文**

- 清除固定视口；屏幕不足 80×24 时显示缩放提示并返回 False，否则绘制标题、电池、保险丝状态和底部按键说明。
- 意义：返回值让调用者暂停常规操作；函数本身不控制所有关卡状态。

**English**

- Clears the viewport and returns False with a resize message when the terminal is too small.
- Otherwise it draws the title, resources, and controls.
- The return value lets callers suspend normal actions; the helper does not itself manage every puzzle state.

#### `show_notes`

<details>
<summary>查看源代码 / View source — include/interface.py · L81–L144</summary>

```python
def show_notes(screen, clues):
    """An on-demand notebook. Closing it returns to the unchanged room."""
    page = 0
    titles = ('JOURNAL + EXPEDITION [1/2]', 'ACCESS NOTES [2/2]')
    screen.timeout(-1)
    while True:
        ready = frame(screen, titles[page], clues,
                      'Tab / arrows: page    Enter / Esc: return')
        if ready:
            if page == 0:
                # Two open columns, separated by whitespace rather than borders.
                accent = curses.color_pair(1)
                text(screen, 5, 5, '01   MIRROR CONSOLE', accent)
                offset = f'Cipher offset: +{clues["shift"]}' if 'shift' in clues else 'No record yet.'
                text(screen, 7, 5, offset, width=36)
                text(screen, 10, 5, '02   DRAWER', accent)
                if 'order' in clues:
                    text(screen, 12, 5, 'Fuse order: ' + ' > '.join(clues['order']), width=36)
                    text(screen, 13, 5, 'Repeat twice (6 nodes).', curses.A_DIM)
                else:
                    text(screen, 12, 5, 'No record yet.')
                text(screen, 15, 5, '03   GATE LOG', accent)
                if 'sequence' in clues:
                    text(screen, 17, 5, 'Terminals: ' + ' > '.join(map(str, clues['sequence'])), width=36)
                    text(screen, 19, 5, 'Only plate a is required.' if clues.get('emergency') else 'Keep BOTH plates powered.')
                elif 'order' in clues:
                    text(screen, 17, 5, 'Battery: reverse fuse labels.')
                    text(screen, 19, 5, 'A=1, C=2, V=3. Use plate a.')
                else:
                    text(screen, 17, 5, 'No record yet.')

                condition = clues.get('condition', 'STABLE')
                text(screen, 5, 47, 'EXPEDITION', accent)
                text(screen, 7, 47, condition)
                details = {'STABLE': 'Normal charge and access order.',
                           'POWER LEAK': 'Circuit starts with 80 less charge.',
                           'INTERFERENCE': 'Restored terminal order is altered.'}
                for y, detail in enumerate(wrap(details[condition], 28), 8):
                    text(screen, y, 47, detail, curses.A_DIM, width=28)
                text(screen, 12, 47, 'Installed modules', accent)
                for index, module in enumerate(clues.get('modules') or ['None']):
                    text(screen, 14 + index * 2, 47, module, width=28)
                text(screen, 19, 47, 'Modules last this run.', curses.A_DIM)
                text(screen, 20, 47, 'No cells = run over.', curses.A_DIM)
            elif page == 1:
                if 'badges' in clues:
                    for index, (name, value) in enumerate(clues['badges'].items()):
                        line(screen, 6 + index * 2, f'Badge {name}     {value}', curses.color_pair(2))
                    line(screen, 13, '1 : A + offset')
                    line(screen, 15, '2 : C - offset')
                    line(screen, 17, '3 : V + 2 x offset')
                    line(screen, 19, 'Each terminal has its own rule. Use the console offset.')
                else:
                    line(screen, 7, 'Open the drawer to recover its numbered badges.')
            screen.refresh()
        key = screen.getch()
        if key in (27, ord('q'), ord('Q')) or ready and key in (10, 13, curses.KEY_ENTER):
            return
        if not ready:
            continue
        if key in (9, curses.KEY_RIGHT, curses.KEY_DOWN):
            page = (page + 1) % 2
        elif key in (curses.KEY_LEFT, curses.KEY_UP):
            page = (page - 1) % 2
```

</details>

**中文**

- 单独运行两页笔记循环。
- 第一页显示偏移量、颜色顺序、终端顺序和资源；第二页显示徽章和公式。
- 依据键是否存在隐藏未取得的线索，翻页只改 page。
- 意义：降低记忆负担，并避免笔记操作移动玩家；电路暂停由调用方负责。

**English**

- Runs a separate two-page notebook loop.
- Page one shows progression clues and resources; page two shows badges and formulas.
- Missing keys hide unrecovered clues, and navigation changes only page.
- Players can review evidence without moving; the circuit caller handles pausing.

#### `read_command`

<details>
<summary>查看源代码 / View source — include/interface.py · L148–L182</summary>

```python
def read_command(screen, title, clues, prompt_lines, hints):
    """Return a submitted string, or None on Escape; retain input on resize."""
    answer = ''
    hint = -1
    screen.timeout(-1)
    while True:
        ready = frame(screen, title, clues, 'Enter: submit    F1: hint    Tab: notebook    Esc: back')
        if ready:
            for y, message in enumerate(wrap_lines(prompt_lines, CONTENT_WIDTH)[:12], 4):
                line(screen, y, message)
            line(screen, 16, 'Your response', curses.A_DIM)
            line(screen, 17, '> ' + answer + '_', curses.color_pair(1))
            if hint < 0 and 'cells' in clues:
                text(screen, 21, 5, 'Wrong answers cost 1 cell. Hints and cancelling are free.')
            if hint >= 0:
                for y, message in enumerate(wrap_lines(hints[hint], 70)[:3], 19):
                    text(screen, y, 5, message)
            screen.refresh()
        key = screen.getch()
        if key == 27:
            return None
        if not ready:
            if key in (ord('q'), ord('Q')):
                return None
            continue
        if key == 9:
            show_notes(screen, clues)
        elif key == curses.KEY_F1:
            hint = min(hint + 1, len(hints) - 1)
        elif key in (10, 13, curses.KEY_ENTER):
            return answer.strip()
        elif key in (curses.KEY_BACKSPACE, 8, 127):
            answer = answer[:-1]
        elif 32 <= key <= 126 and len(answer) < 45:
            answer += chr(key)
```

</details>

**中文**

- 保存 answer 和提示索引 hint；处理 Enter、Esc、Tab、F1、退格及最多 45 个可打印 ASCII 字符。
- Enter 返回去除首尾空白的字符串，Esc 返回 None；正常输入中 Q 是文字。
- 意义：多处文字谜题共用输入编辑与取消约定，缩放时不丢已输入答案。

**English**

- Maintains answer and hint index, handling Enter, Escape, Tab, F1, Backspace, and up to 45 printable ASCII characters.
- Enter returns trimmed text; Escape returns None; Q is ordinary text during normal entry.
- Shared editing and cancellation preserve input across resizing.

#### `notice`

<details>
<summary>查看源代码 / View source — include/interface.py · L186–L198</summary>

```python
def notice(screen, title, clues, messages):
    screen.timeout(-1)
    while True:
        ready = frame(screen, title, clues, 'Enter: continue    Tab: notebook    Esc: back')
        if ready:
            for y, message in enumerate(wrap_lines(messages, CONTENT_WIDTH)[:13], 5):
                line(screen, y, message)
            screen.refresh()
        key = screen.getch()
        if ready and key == 9:
            show_notes(screen, clues)
        if key in (27, ord('q'), ord('Q')) or ready and key in (10, 13, curses.KEY_ENTER):
            return
```

</details>

**中文**

- 将消息换行绘制，等待 Enter 或退出键，也允许打开笔记。
- 意义：统一成功、失败和剧情提示，避免每个关卡重复写确认页面。

**English**

- Wraps and draws messages, waits for acknowledgement or exit, and permits notebook access.
- It provides reusable success, failure, and narrative screens.

### 3.3 `include/expedition.py`

**模块级代码 / Module-level code**

**中文**

- CONDITIONS、MODULES、DESCRIPTIONS 是规则数据；模块名和说明通过同一个索引对应。
- 模块导入界面函数用于奖励选择，其余资源函数不依赖绘制。

**English**

- CONDITIONS, MODULES, and DESCRIPTIONS hold rule data; module names and descriptions share indices.
- UI imports support reward selection, while other resource functions do not draw.

#### `new_run`

<details>
<summary>查看源代码 / View source — include/expedition.py · L16–L18</summary>

```python
def new_run(seed):
    return {'seed': seed, 'cells': 3, 'condition': CONDITIONS[seed % 3],
            'bonus_charge': 0, 'fuse': False, 'modules': []}
```

</details>

**中文**

- 返回包含种子、三格电池、环境条件、额外电量、保险丝和模块列表的新字典；condition 用 seed % 3 选择。
- 意义：每局初始状态明确且不继承上一局资源。

**English**

- Returns a fresh dictionary with the seed, three cells, a condition selected by seed modulo three, bonus charge, fuse, and modules.
- Runs start from explicit defaults without inherited resources.

#### `circuit_charge`

<details>
<summary>查看源代码 / View source — include/expedition.py · L22–L26</summary>

```python
def circuit_charge(clues):
    charge = 420 + clues.get('bonus_charge', 0)
    if clues.get('condition') == 'POWER LEAK':
        charge -= 80
    return charge
```

</details>

**中文**

- 基础电量 420，加上电容奖励；POWER LEAK 再减 80。
- 意义：统一计算初始电量，重试及判断是否已移动时使用相同预算。

**English**

- Starts at 420, adds capacitor bonuses, and subtracts 80 for POWER LEAK.
- Attempts and abandonment checks use the same charge budget.

#### `power_sequence`

<details>
<summary>查看源代码 / View source — include/expedition.py · L30–L33</summary>

```python
def power_sequence(clues):
    if clues.get('condition') == 'INTERFERENCE':
        return (3, 1, 2)
    return (2, 3, 1)
```

</details>

**中文**

- INTERFERENCE 返回 (3,1,2)，其余返回 (2,3,1)。
- 意义：环境条件会影响后续终端顺序；保存读取时也能由当前局重建。

**English**

- Returns (3,1,2) under INTERFERENCE and (2,3,1) otherwise.
- Conditions affect later access, and loading can reconstruct the same sequence.

#### `lose_cell`

<details>
<summary>查看源代码 / View source — include/expedition.py · L37–L43</summary>

```python
def lose_cell(clues):
    """Costs persist through room exits, retries and undo."""
    if clues.get('fuse', False):
        clues['fuse'] = False
        return 'Surge fuse absorbed the loss.'
    clues['cells'] = max(0, clues.get('cells', 3) - 1)
    return f'Emergency cells remaining: {clues["cells"]}.'
```

</details>

**中文**

- 优先消耗 fuse；没有保险丝时将 cells 减一并限制不小于零，返回反馈文字。
- 意义：统一失败成本，避免各关卡对保险丝和电池的处理不同。

**English**

- Consumes an active fuse first; otherwise subtracts one cell with a zero lower bound, returning feedback.
- All puzzles share the same loss rule.

#### `apply_module`

<details>
<summary>查看源代码 / View source — include/expedition.py · L47–L54</summary>

```python
def apply_module(clues, module):
    if module == 0:
        clues['cells'] = min(5, clues.get('cells', 3) + 1)
    elif module == 1:
        clues['bonus_charge'] = clues.get('bonus_charge', 0) + 120
    else:
        clues['fuse'] = True
    clues.setdefault('modules', []).append(MODULES[module])
```

</details>

**中文**

- 模块 0 增加电池且上限为 5；模块 1 增加 120 电量；模块 2 激活一次性保险丝；随后记录模块名称。
- 意义：效果和记录集中更新；保险丝是布尔状态，不会累积多层保护。

**English**

- Module 0 adds a cell up to five; module 1 adds 120 charge; module 2 activates a fuse.
- The module name is recorded.
- Effects and records update together; a Boolean fuse does not stack multiple protections.

#### `reward`

<details>
<summary>查看源代码 / View source — include/expedition.py · L58–L81</summary>

```python
def reward(screen, clues, stage):
    """One two-item offer per completed room. Esc skips it permanently."""
    first = (clues.get('seed', 0) + stage) % 3
    # Once the circuit is repaired, extra circuit charge has no further use.
    offers = (0, 2) if stage == 2 else (first, (first + 1) % 3)
    screen.timeout(-1)
    while True:
        ready = frame(screen, 'SALVAGE / TAKE ONE MODULE', clues,
                      '1/2: install module | Esc/Q: leave the salvage')
        if ready:
            line(screen, 5, 'Supplies for the gate and exit passage.' if stage == 2
                 else 'A maintenance cache contains two usable modules.')
            for index, module in enumerate(offers):
                line(screen, 8 + index * 4, f'[{index + 1}] {MODULES[module]}')
                line(screen, 9 + index * 4, DESCRIPTIONS[module])
            line(screen, 17, 'Leaving this cache forfeits its unclaimed module.')
            line(screen, 18, 'Modules last only for this expedition.')
            screen.refresh()
        key = screen.getch()
        if key in (27, ord('q'), ord('Q')):
            return
        if ready and key in (ord('1'), ord('2')):
            apply_module(clues, offers[key - ord('1')])
            return
```

</details>

**中文**

- 根据种子和关卡索引生成两项奖励；电路完成后固定提供电池或保险丝。
- 按 1/2 安装一项即返回，退出则放弃。
- 意义：给予资源取舍，并避免电路完成后再提供无用途的电容。

**English**

- Offers two modules based on seed and stage; after the circuit it offers a cell or fuse.
- Selecting one installs it and returns; leaving forfeits it.
- The choice creates a resource trade-off without offering a capacitor after its useful stage.

### 3.4 `include/decipher_1.py`

**模块级代码 / Module-level code**

**中文**

- ALPHABET 定义映射表；共用输入、通知及扣资源函数，关卡自身不重新初始化 curses。

**English**

- ALPHABET is the substitution table.
- Shared input, notice, and resource helpers avoid reinitializing curses inside the room.

#### `mirror`

<details>
<summary>查看源代码 / View source — include/decipher_1.py · L10–L18</summary>

```python
def mirror(message):
    result = ''
    for letter in message.upper():
        if letter in ALPHABET:
            position = ALPHABET.index(letter)
            result += ALPHABET[25 - position]
        else:
            result += letter
    return result
```

</details>

**中文**

- 将输入转成大写，对字母执行索引 25-position，其他字符保留。
- 意义：用同一映射完成镜像字母替换，生成题面而不硬编码密文。

**English**

- Uppercases input and maps each alphabet index to 25 minus that index, preserving other characters.
- The symmetric mapping generates the clue rather than storing a hard-coded ciphertext.

#### `check_command`

<details>
<summary>查看源代码 / View source — include/decipher_1.py · L22–L23</summary>

```python
def check_command(answer):
    return ' '.join(answer.upper().split()) == 'PRESS THE BUTTON'
```

</details>

**中文**

- upper、split、join 组合消除大小写和多余空白差异，再与 PRESS THE BUTTON 比较。
- 意义：验证解谜内容，而不是惩罚格式差异。

**English**

- Combines upper, split, and join before comparing with PRESS THE BUTTON.
- Validation accepts harmless case and whitespace differences.

#### `main`

<details>
<summary>查看源代码 / View source — include/decipher_1.py · L27–L52</summary>

```python
def main(screen, clues):
    feedback = ''
    while True:
        answer = read_command(screen, '01 / MIRROR CONSOLE', clues, [
            'Emergency lighting is offline. A mirrored panel reads:', '',
            mirror('PRESS THE BUTTON'), '',
            'Etched above the panel: A ... Z | Z ... A',
            'Decode the message and enter the full English command.', '', feedback,
        ], [
            ['Read the alphabet from opposite ends: A <-> Z.'],
            ['B <-> Y, C <-> X. Decode each letter separately.'],
        ])
        if answer is None:
            return False
        if check_command(answer):
            clues['shift'] = 7
            notice(screen, '01 / EMERGENCY LIGHTING RESTORED', clues, [
                'A service label appears beneath the button:', '',
                'ENCODER OFFSET: +7. Subtract it when decoding.',
                'Keep this offset. Gate codes also need drawer badges.', '',
                'The powered drawer is now available.',
            ])
            return True
        feedback = 'Incorrect command. ' + lose_cell(clues)
        if clues.get('cells', 3) <= 0:
            return False
```

</details>

**中文**

- 反复显示密文、提示和上次反馈；取消返回 False；正确时写入 shift=7 并返回 True；错误调用 lose_cell，电池耗尽退出。
- 意义：把第一关的结果作为后续关卡所需数据，而不只显示一条成功消息。

**English**

- Loops over the clue, hints, and feedback.
- Cancellation returns False; success writes shift=7 and returns True; mistakes call lose_cell and stop on exhaustion.
- Solving produces a reusable clue for later rooms.

### 3.5 `include/decipher_2.py`

**模块级代码 / Module-level code**

**中文**

- 第二关调用 interface 的输入框和通知页面，再调用 expedition 扣除错误答案的资源。
- 它通过 main(screen, clues) 接收当前局数据，成功时把颜色顺序和徽章编号写回 clues。

**English**

- Room two uses interface for input and messages, and expedition for failure costs.
- Its main(screen, clues) receives the current run and adds the colour order and badge numbers to clues on success.

#### `make_badges`

<details>
<summary>查看源代码 / View source — include/decipher_2.py · L8–L11</summary>

```python
def make_badges(seed):
    # Three separate ranges keep all derived terminal codes distinct.
    return {'A': 10 + seed % 20, 'C': 50 + (seed // 20) % 20,
            'V': 80 + (seed // 400) % 20}
```

</details>

**中文**

- 通过 seed 的余数和整除生成 A=10–29、C=50–69、V=80–99。
- 意义：徽章随局变化，且配合 offset=7 时三个终端密码区间不重叠。

**English**

- Uses modulo and integer division to generate A in 10–29, C in 50–69, and V in 80–99.
- Badges vary by run, while the terminal code ranges remain distinct with offset 7.

#### `make_order`

<details>
<summary>查看源代码 / View source — include/decipher_2.py · L15–L17</summary>

```python
def make_order(seed):
    orders = (('A', 'C', 'V'), ('C', 'V', 'A'), ('V', 'A', 'C'))
    return orders[(seed // 3) % 3]
```

</details>

**中文**

- 从三种颜色轮换顺序中用 (seed//3)%3 选一种。
- 意义：同一种子能重建同一电路规则，减少存档需要直接保存的数据。

**English**

- Selects one of three color rotations using (seed//3)%3.
- A seed reproduces the circuit rule, reducing saved data.

#### `encode_word`

<details>
<summary>查看源代码 / View source — include/decipher_2.py · L21–L27</summary>

```python
def encode_word(word='OPEN', shift=7):
    numbers = []
    for letter in word.upper():
        position = ord(letter) - ord('A')  # A=0, B=1, ..., Z=25
        encoded = (position + shift) % 26 + 1
        numbers.append(encoded)
    return numbers
```

</details>

**中文**

- 将字母转成 0–25，加 shift 后对 26 取模，再加 1 得到 1–26 数字。
- 默认 OPEN 编码为 22、23、12、21。
- 意义：把第一关偏移量真正用于第二关，模运算处理字母表边界。

**English**

- Converts letters to 0–25, adds shift modulo 26, then adds one.
- OPEN with shift 7 becomes 22,23,12,21.
- The offset links the rooms, and modular arithmetic handles alphabet boundaries.

#### `check_answer`

<details>
<summary>查看源代码 / View source — include/decipher_2.py · L31–L32</summary>

```python
def check_answer(answer):
    return answer.strip().upper() == 'OPEN'
```

</details>

**中文**

- 去掉首尾空白并转大写，检查是否为 OPEN。
- 意义：将答案判断与界面分离，方便单独检查。

**English**

- Trims and uppercases the answer, then checks for OPEN.
- Validation is separate from the UI and easy to check independently.

#### `main`

<details>
<summary>查看源代码 / View source — include/decipher_2.py · L36–L73</summary>

```python
def main(screen, clues):
    if 'shift' not in clues:
        return False
    feedback = ''
    while True:
        answer = read_command(screen, '02 / LOCKED DRAWER', clues, [
            'The lights reveal a drawer with a powered keyboard.',
            'Its display reads:', '',
            ' - '.join(map(str, encode_word(shift=clues['shift']))), '',
            'A torn paper is tucked underneath. Press F1 to inspect.',
            'Decode the four-letter command.', '', feedback,
        ], [
            ['Torn paper: A=1 | H=8  | O=15',
             '            B=2 | I=9  | P=16',
             '            C=3 | J=10 | Q=17'],
            ['The encoder ADDED the console offset to each letter.',
             'Subtract that offset, then use A=1 ... Z=26.',
             'Wrap values below 1 back around by adding 26.'],
        ])
        if answer is None:
            return False
        if check_answer(answer):
            clues['order'] = make_order(clues.get('seed', 0))
            clues['badges'] = make_badges(clues.get('seed', hash('underground-access') % 8000))
            notice(screen, '02 / DRAWER OPENED', clues, [
                'Inside: a circuit key, fuse diagram and badges.',
                'Badge numbers are saved in ACCESS NOTES (Tab).',
                'Fuse routing: ' + ' > '.join(clues['order']),
                'Repeat this order twice to restore the power.', '',
                'Wrong-colour nodes will short the circuit.',
                'Battery wiring: A=1, C=2, V=3. Reverse the order.',
                'Battery mode: plate a only. Radio needs mains power.',
                'The key fits the circuit terminal and the gate.',
            ])
            return True
        feedback = 'Incorrect command. ' + lose_cell(clues)
        if clues.get('cells', 3) <= 0:
            return False
```

</details>

**中文**

- 先要求 shift 存在，再显示数字谜题；成功时生成 order 与 badges，展示电路和备用电池线路说明；错误扣资源，取消不扣。
- 意义：在此处分出电路和门禁两条可走路径，并提供它们所需线索。

**English**

- Requires shift, displays the numeric puzzle, and writes order and badges on success.
- The notice explains circuit and battery wiring.
- Errors cost resources; cancellation does not.
- This room supplies evidence for both available branches.

### 3.6 `include/decipher_3.py`

**模块级代码 / Module-level code**

**中文**

- WIDTH=24、HEIGHT=14 是逻辑网格，不是终端大小；绘制时每格占两列。
- TARGET=6，CHARGE=420。
- EnergyCircuit 管规则，模块 main 管显示和输入。

**English**

- WIDTH=24 and HEIGHT=14 describe the logical grid, rendered at two columns per cell.
- TARGET is six and CHARGE is 420.
- EnergyCircuit holds rules; module main handles presentation and input.

#### `EnergyCircuit.__init__`

<details>
<summary>查看源代码 / View source — include/decipher_3.py · L17–L26</summary>

```python
    def __init__(self, order, charge=CHARGE, seed=0):
        self.order = tuple(order)
        self.snake = [(6, 7), (5, 7), (4, 7)]
        self.direction = (1, 0)
        self.score = 0
        self.charge = charge
        self.seed = seed
        self.status = 'ready'
        self.nodes = {}
        self.spawn_nodes()
```

</details>

**中文**

- 建立颜色顺序、初始蛇身、向右方向、分数、电量、种子和 ready 状态，再生成节点。
- 意义：一次尝试的数据集中在对象中，重试可直接创建新对象。

**English**

- Creates the color order, starting snake, rightward direction, score, charge, seed, and ready state, then spawns nodes.
- One object owns one attempt, so retrying creates a fresh instance.

#### `EnergyCircuit.expected`

<details>
<summary>查看源代码 / View source — include/decipher_3.py · L29–L31</summary>

```python
    @property
    def expected(self):
        return self.order[self.score % len(self.order)]
```

</details>

**中文**

- 属性返回 order[score % len(order)]。
- 意义：三色顺序自动循环两次，无须维护第二份计数器。

**English**

- The property returns order[score % len(order)].
- The three-color order repeats automatically without another counter.

#### `EnergyCircuit.spawn_nodes`

<details>
<summary>查看源代码 / View source — include/decipher_3.py · L34–L46</summary>

```python
    def spawn_nodes(self):
        x, y = self.snake[0]
        free = []
        for cy in range(1, HEIGHT - 1):
            for cx in range(1, WIDTH - 1):
                distance = abs(cx - x) + abs(cy - y)
                if (cx, cy) not in self.snake and distance > 2:
                    free.append((cx, cy))
        self.nodes = {}
        for index, colour in enumerate(self.order):
            # Spread nodes across the board without needing a random library.
            position = (self.seed + self.score * 53 + index * 41 + 17) % len(free)
            self.nodes[colour] = free.pop(position)
```

</details>

**中文**

- 枚举内部空格，排除蛇身及离蛇头曼哈顿距离不大于 2 的格子，再按种子、分数和颜色索引选点；pop 移除已选格。
- 意义：节点不重叠且不会紧贴蛇头；相同完整状态可重现位置，位置不只由种子决定。

**English**

- Enumerates interior cells, excluding the snake and cells within Manhattan distance two of its head.
- Seed, score, and color index select positions; pop prevents duplicates.
- Nodes avoid immediate proximity and are reproducible from the full state, not the seed alone.

#### `EnergyCircuit.step`

<details>
<summary>查看源代码 / View source — include/decipher_3.py · L49–L79</summary>

```python
    def step(self, direction=None):
        if self.status != 'running':
            return
        if direction is not None and direction != (-self.direction[0], -self.direction[1]):
            self.direction = direction
        self.charge -= 1
        x, y = self.snake[0]
        head = (x + self.direction[0], y + self.direction[1])
        colour = None
        for name, position in self.nodes.items():
            if position == head:
                colour = name
                break
        # The tail moves away unless a node is collected, so its old cell is safe only on non-growing moves.
        body = self.snake if colour else self.snake[:-1]
        if not (0 < head[0] < WIDTH - 1 and 0 < head[1] < HEIGHT - 1) or head in body:
            self.status = 'collision'
        elif colour and colour != self.expected:
            self.status = 'short circuit'
        else:
            self.snake.insert(0, head)
            if colour:
                self.score += 1
                if self.score == TARGET:
                    self.status = 'won'
                else:
                    self.spawn_nodes()
            else:
                self.snake.pop()
        if self.charge <= 0 and self.status == 'running':
            self.status = 'out of charge'
```

</details>

**中文**

- 仅 running 执行；拒绝直接反向，先扣一格电量并计算新头。
- 检测目标节点、墙和身体；未吃节点时排除即将移走的尾格。
- 错误颜色失败；正确颜色加分并长一格，达到六个即胜利，否则重生节点；普通移动移除尾部。
- 最后只在仍 running 且无电时判失败。
- 意义：统一一次状态转移，并允许恰好用最后一点电完成目标。

**English**

- Runs only in running state, rejects reversal, spends one charge, and computes the new head.
- It checks nodes, walls, and body, excluding the departing tail on non-growing moves.
- Wrong colors fail; correct colors grow the snake and score toward six; ordinary movement removes the tail.
- Charge exhaustion applies only if still running, so the last charge can complete the objective.

#### `main`

<details>
<summary>查看源代码 / View source — include/decipher_3.py · L83–L158</summary>

```python
def main(screen, clues):
    if 'order' not in clues:
        return False
    circuit = EnergyCircuit(clues['order'], circuit_charge(clues), clues.get('seed', 0))
    while True:
        ready = frame(screen, '03 / ENERGY CIRCUIT', clues,
                      'Arrows: steer    Space: pause    Tab: notebook    R: retry    Q: back')
        if not ready and circuit.status == 'running':
            circuit.status = 'paused'
        if ready:
            line(screen, 4, f'Nodes {circuit.score}/{TARGET}    Charge {circuit.charge}    Next {circuit.expected}    {circuit.status.upper()}')
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    char = '#' if x in (0, WIDTH - 1) or y in (0, HEIGHT - 1) else '.'
                    text(screen, y + 6, x * 2 + 16, char, curses.A_DIM)
            for colour, (x, y) in circuit.nodes.items():
                text(screen, y + 6, x * 2 + 16, colour, curses.A_BOLD | curses.color_pair({'A': 2, 'C': 1, 'V': 3}[colour]))
            for index, (x, y) in enumerate(circuit.snake):
                text(screen, y + 6, x * 2 + 16, '@' if index == 0 else 'o', curses.color_pair(1))
            if circuit.status == 'ready':
                text(screen, 21, 5, 'Space to begin. Failure or abandoning after movement costs 1 cell.')
            else:
                text(screen, 21, 5, 'Each movement uses one charge. Pause to plan a route.')
            if circuit.status not in ('ready', 'running', 'paused'):
                text(screen, 21, 5, 'Circuit failed. Press R to retry; earlier clues are safe.')
            screen.refresh()
        # One movement every 160 ms, regardless of how fast keys are pressed.
        if circuit.status == 'running':
            curses.napms(160)
            screen.timeout(0)
        else:
            screen.timeout(-1)
        key = screen.getch()
        if key in (27, ord('q'), ord('Q')):
            if circuit.status in ('running', 'paused') and circuit.charge < circuit_charge(clues):
                lose_cell(clues)
            screen.timeout(-1)
            return False
        if key == curses.KEY_RESIZE:
            if circuit.status == 'running':
                circuit.status = 'paused'
            continue
        if not ready:
            continue
        if key == 9:
            if circuit.status == 'running':
                circuit.status = 'paused'
            show_notes(screen, clues)
        elif key in (ord('r'), ord('R')):
            if circuit.status in ('running', 'paused') and circuit.charge < circuit_charge(clues):
                lose_cell(clues)
                if clues.get('cells', 3) <= 0:
                    return False
            circuit = EnergyCircuit(clues['order'], circuit_charge(clues), clues.get('seed', 0))
        elif key == ord(' '):
            if circuit.status in ('ready', 'paused'):
                circuit.status = 'running'
            elif circuit.status == 'running':
                circuit.status = 'paused'
        elif circuit.status == 'running':
            circuit.step(DIRECTIONS.get(key))
            if circuit.status == 'won':
                clues['sequence'] = power_sequence(clues)
                notice(screen, '03 / POWER RESTORED', clues, [
                    'The gate controller returns an archived access log:', '',
                    'TERMINAL HANDSHAKE: ' + ' > '.join(map(str, clues['sequence'])),
                    'ACCESS: each terminal has its own badge formula.',
                    'INTERLOCK: both matching pressure plates must stay on.', '',
                    'The final security room is now accessible.',
                ])
                return True
            # Charge for failure once here; leaving or restarting this failed attempt must not charge again.
            if circuit.status not in ('running', 'won'):
                lose_cell(clues)
                if clues.get('cells', 3) <= 0:
                    return False
```

</details>

**中文**

- 创建电路并绘制网格、节点和蛇；运行时每轮 napms(160) 后非阻塞读键，其他状态阻塞等待。
- Space 切换暂停，Tab 和缩放会暂停，R 重建尝试，Q 返回。
- 已移动的运行/暂停尝试在放弃时扣资源；失败在发生时扣一次，失败后退出不再扣。
- 成功写入 sequence。
- 意义：分开规则与终端循环，避免无限免费重试。
- 160 ms 是每轮休眠，并非严格实时计时器。

**English**

- Creates and renders the circuit.
- Running iterations sleep 160 ms before nonblocking input; other states block.
- Space toggles pause; notes and resizing pause; R retries; Q returns.
- Abandoning an active attempt after movement costs a resource.
- Failure is charged once when it happens, not again on exit.
- Success writes sequence.
- Rules are separate from terminal handling; the sleep is not a precise real-time clock.

### 3.7 `include/decipher_4.py`

**供电模式与 b 的用途 / Power modes and the purpose of b**

小写 b 是箱子 B 对应的压力板。跳过第三关时，备用电池只支持 a，b 暂不工作；完成第三关后，需要 A 压住 a、B 压住 b，门才能保持开启。因此 B/b 不是无用装饰，而是在主电源模式下参与开门。

Lowercase b is the pressure plate for box B. If room 3 is skipped, the backup battery powers only a and b is inactive. After room 3 is repaired, A must stay on a and B on b to keep the doors open. B/b therefore has a purpose in mains-power mode.

**模块级代码 / Module-level code**

**中文**

- MAP 用字符串表示墙、通道、门和出口；START、BOXES、PLATES、TERMINALS、RADIO、ALARM 保存坐标，FORMULAS 保存题面。
- 小写 a/b 是机关，大写 A/B 是箱子；徽章 A/C/V 是另一组数据。

**English**

- MAP stores walls, paths, doors, and exit.
- Coordinate constants locate the player, crates, plates, terminals, radio, and alarm; FORMULAS contains displayed rules.
- Lowercase a/b are plates and uppercase A/B are crates; badges A/C/V are separate data.

#### `terminal_keys`

<details>
<summary>查看源代码 / View source — include/decipher_4.py · L32–L36</summary>

```python
def terminal_keys(clues):
    badges = clues['badges']
    offset = clues['shift']
    return {1: badges['A'] + offset, 2: badges['C'] - offset,
            3: badges['V'] + 2 * offset}
```

</details>

**中文**

- 用徽章和偏移量计算终端 1=A+offset、2=C-offset、3=V+2×offset。
- 意义：最终门禁需要综合前两关线索，三个终端不能共用同一密码。

**English**

- Calculates terminal codes as A+offset, C-offset, and V+2×offset.
- The gate combines earlier evidence and requires distinct credentials.

#### `GatePuzzle.__init__`

<details>
<summary>查看源代码 / View source — include/decipher_4.py · L43–L55</summary>

```python
    def __init__(self, sequence=(2, 1, 3), bypass=False):
        if sorted(sequence) != [1, 2, 3]:
            raise ValueError('Terminal sequence must be a permutation of 1, 2, 3')
        self.bypass = bypass
        self.sequence = tuple(sequence)
        self.player = START
        self.boxes = dict(BOXES)
        self.entered = []
        self.authorized = False
        self.history = []
        self.moves = 0
        self.won = False
        self.radio = 'idle'
```

</details>

**中文**

- 确认 sequence 为 1、2、3 的排列，再初始化供电模式、玩家、箱子副本、验证进度、撤销历史、步数和无线电。
- 意义：保证顺序有效，每次进房或重置都有独立可变状态。
- 默认顺序是 (2,1,3)，正常游戏会显式传入实际顺序。

**English**

- Validates a permutation of 1,2,3 and initializes power mode, player, copied crates, verification, history, moves, and radio.
- Attempts have independent mutable state.
- The default is (2,1,3), but gameplay explicitly passes the actual sequence.

#### `GatePuzzle.powered`

<details>
<summary>查看源代码 / View source — include/decipher_4.py · L58–L65</summary>

```python
    @property
    def powered(self):
        if self.bypass:
            return self.boxes['A'] == PLATES['A']
        for name, position in PLATES.items():
            if self.boxes[name] != position:
                return False
        return True
```

</details>

**中文**

- 备用供电只检查 A 在 a；正常供电检查每个箱子是否在同名机关。
- 意义：直接从位置推导供电，避免另存一个可能过期的 powered 变量。

**English**

- Battery mode checks only A on a; mains mode checks every matching crate and plate.
- Power is derived from positions rather than a separately maintained flag.

#### `GatePuzzle.walkable`

<details>
<summary>查看源代码 / View source — include/decipher_4.py · L68–L76</summary>

```python
    def walkable(self, pos):
        x, y = pos
        if not (0 <= y < len(MAP) and 0 <= x < len(MAP[y])):
            return False
        if MAP[y][x] == '#':
            return False
        if MAP[y][x] == 'D' and not self.powered:
            return False
        return True
```

</details>

**中文**

- 依次检查边界、墙及未供电的门。
- 意义：玩家移动与箱子推动共用地形规则；箱子之间的阻挡由 move 另查。

**English**

- Checks bounds, walls, and unpowered doors.
- Player and crate movement share terrain rules; move separately handles crate collisions.

#### `GatePuzzle.snapshot`

<details>
<summary>查看源代码 / View source — include/decipher_4.py · L79–L81</summary>

```python
    def snapshot(self):
        self.history.append((self.player, dict(self.boxes), list(self.entered),
                             self.authorized, self.moves, self.won, self.radio))
```

</details>

**中文**

- 把玩家、箱子字典副本、已验证列表副本、授权、步数、胜利及无线电压入 history。
- 意义：复制可变容器避免历史随当前状态变化；不保存电池，撤销不退还成本。

**English**

- Pushes player, copied crate and verification containers, authorization, moves, win, and radio state onto history.
- Copies preserve past states; excluding cells prevents refunds through undo.

#### `GatePuzzle.undo`

<details>
<summary>查看源代码 / View source — include/decipher_4.py · L84–L87</summary>

```python
    def undo(self):
        if self.history:
            (self.player, self.boxes, self.entered, self.authorized,
             self.moves, self.won, self.radio) = self.history.pop()
```

</details>

**中文**

- 历史不空时 pop 最后一个快照并恢复各字段。
- 意义：用后进先出结构实现逐步撤销，而不是重建整局。

**English**

- Pops and restores the latest snapshot when available.
- A last-in-first-out history supports stepwise undo without resetting the run.

#### `GatePuzzle.move`

<details>
<summary>查看源代码 / View source — include/decipher_4.py · L90–L123</summary>

```python
    def move(self, direction):
        if self.won:
            return 'Evacuation is complete.'
        dx, dy = direction
        target = (self.player[0] + dx, self.player[1] + dy)
        if not self.walkable(target):
            return 'Blocked by a wall or closed door. H: how to open the doors.'
        box = None
        for name, position in self.boxes.items():
            if position == target:
                box = name
                break
        if box:
            destination = (target[0] + dx, target[1] + dy)
            if not self.walkable(destination) or destination in self.boxes.values():
                return 'The crate cannot move there. U: undo a previous move.'
        if target == EXIT and not (self.powered and self.authorized):
            return 'Exit locked. Keep the plates pressed and unlock all 3 terminals.'
        self.snapshot()
        if box:
            self.boxes[box] = destination
        self.player = target
        self.moves += 1
        if not self.powered:
            self.entered = []
            self.authorized = False
        self.won = self.player == EXIT
        if self.won:
            return 'Exit reached!'
        if self.powered:
            return 'Doors open. Keep the boxes in place. Use terminals 1, 2 and 3.'
        if self.bypass:
            return 'Battery power: use A on a. Plate b needs mains power from room 3.'
        return 'Push box A onto a and box B onto b. You cannot pull boxes.'
```

</details>

**中文**

- 先检查目标格；遇箱子则检查再前方一格能否容纳，禁止推动进入另一箱子。
- 到出口还必须供电且授权。
- 验证通过后才保存快照、移动并加步数；若失电则清空终端认证，到出口置 won。
- 意义：无效行动不污染历史，推箱子、供电和身份验证保持联动。

**English**

- Checks the target, and for a crate checks the next cell and other crates.
- Exit entry requires power and authorization.
- Only a valid action snapshots and moves state.
- Losing power clears verification; reaching the exit sets won.
- Invalid actions do not pollute history, and movement stays linked to access rules.

#### `GatePuzzle.activate`

<details>
<summary>查看源代码 / View source — include/decipher_4.py · L126–L146</summary>

```python
    def activate(self, key, expected_keys):
        if self.won:
            return 'Evacuation is complete.'
        nearby = self.terminal_nearby()
        if nearby is None:
            return 'Stand on or next to a numbered terminal first.'
        if not self.powered:
            return 'The required plates must be powered.'
        if str(key).strip() != str(expected_keys[nearby]):
            return "Wrong code. Combine the badge with this terminal's rule."
        if self.authorized:
            return 'Already verified. Proceed to exit E.'
        self.snapshot()
        if nearby != self.sequence[len(self.entered)]:
            self.entered = []
            return f'Wrong terminal. Start again at terminal {self.sequence[0]}. Tab: order.'
        self.entered.append(nearby)
        self.authorized = len(self.entered) == 3
        if self.authorized:
            return 'All 3 terminals unlocked. Walk to E when ready to leave.'
        return f'Terminal {nearby} accepted ({len(self.entered)}/3).'
```

</details>

**中文**

- 先查附近终端与供电，再比密码；已授权则无需再验证。
- 密码正确后保存快照；终端顺序错误清空 entered，正确则追加，三个都正确后 authorized=True。
- 意义：将密码和顺序作为两层条件。
- 错误密码不会清空进度，本方法也不直接扣电池。

**English**

- Checks nearby terminal, power, and code, then handles existing authorization.
- A correct code snapshots state; wrong order clears entered, while correct order appends and eventually authorizes.
- Code and order are separate requirements.
- Wrong codes do not clear progress, and this method does not charge cells.

#### `GatePuzzle.terminal_nearby`

<details>
<summary>查看源代码 / View source — include/decipher_4.py · L149–L153</summary>

```python
    def terminal_nearby(self):
        for number, position in TERMINALS.items():
            if self.near(position):
                return number
        return None
```

</details>

**中文**

- 遍历终端坐标并调用 near，找到返回编号，否则 None。
- 意义：把距离判断与输入处理分离，只有附近设备可交互。

**English**

- Returns the first nearby terminal number, or None.
- Proximity checks are reusable and interactions remain local.

#### `GatePuzzle.near`

<details>
<summary>查看源代码 / View source — include/decipher_4.py · L156–L157</summary>

```python
    def near(self, position):
        return abs(self.player[0] - position[0]) + abs(self.player[1] - position[1]) <= 1
```

</details>

**中文**

- 判断横向距离加纵向距离是否不大于 1。
- 意义：允许站在设备上或正交相邻格使用，斜对角不算。

**English**

- Tests whether Manhattan distance is at most one.
- A device is reachable from its cell or an orthogonal neighbor, not a diagonal.

#### `GatePuzzle.operate`

<details>
<summary>查看源代码 / View source — include/decipher_4.py · L160–L181</summary>

```python
    def operate(self):
        """E operates the nearby fixture. None means use a security terminal."""
        # Radio states: idle means no call, cut means disconnected, sent means transmitted; undo restores them.
        if self.near(ALARM):
            if self.radio == 'sent':
                return 'F is locked: keep the rescue transmission powered.'
            if self.radio == 'cut':
                return 'The alarm and radio feed are already disconnected.'
            self.snapshot()
            self.radio = 'cut'
            return 'Alarm silenced; O disconnected. No rescue call. U: undo.'
        if self.near(RADIO):
            if self.radio == 'cut':
                return 'O has no power: F cut its shared feed. No rescue contact.'
            if self.bypass or not self.powered:
                return 'Radio needs mains power and both pressure plates.'
            if self.radio == 'sent':
                return 'Rescuers have your location. Complete the relay beyond the gate.'
            self.snapshot()
            self.radio = 'sent'
            return 'Rescue team: "Location received. Reach the relay to guide us in."'
        return None
```

</details>

**中文**

- 靠近 F 可切断共享馈线；已发送求救时不允许再切断。
- 靠近 O 时检查是否断线、是否正常供电以及双机关状态，再写 sent；状态改变前保存快照。
- 没有对应设备返回 None。
- 意义：环境操作影响结局，且离开门禁前可以撤销。

**English**

- Near F, cuts the shared feed unless rescue is already transmitting.
- Near O, checks the feed, mains power, and plates before setting sent.
- Changes are snapshotted; no fixture returns None.
- Physical interactions determine the branch and remain undoable before leaving the gate.

#### `GatePuzzle.fixture_hint`

<details>
<summary>查看源代码 / View source — include/decipher_4.py · L184–L214</summary>

```python
    def fixture_hint(self):
        """Explain equipment consequences without offering an ending menu."""
        if self.bypass:
            consequence = 'No mains power: escape alone through the emergency shaft.'
        elif self.radio == 'sent':
            consequence = 'Rescue contact made. Finish the exit relay to reach the team.'
        else:
            consequence = 'No rescue contact: the powered exit leads to a scanner corridor.'
        if self.near(ALARM):
            if self.radio == 'sent':
                return 'F locked: the alarm feed now powers your rescue call.', consequence
            if self.radio == 'cut':
                return 'F disconnected: alarm silent; O cannot call rescuers.', consequence
            return 'Press E here to cut F: stop the alarm AND disable radio O.', consequence
        if self.near(RADIO):
            if self.radio == 'cut':
                return 'O offline: cutting F also disconnected the rescue radio.', consequence
            if self.bypass:
                return 'O needs mains power. Return to repair the circuit first.', consequence
            if not self.powered:
                return 'O needs both crates on their plates before it can call rescue.', consequence
            if self.radio == 'sent':
                return 'O transmitting: the rescue team has your coordinates.', consequence
            return 'Press E here to use O: send your location to rescuers.', consequence
        if not self.powered:
            task = 'Next: push box A onto a.' if self.bypass else 'Next: push box A onto a and box B onto b.'
        elif not self.authorized:
            task = f'Next: find terminal {self.sequence[len(self.entered)]} and press E beside it.'
        else:
            task = 'Gate unlocked. Visit O for rescue, or walk to exit E.'
        return task, consequence
```

</details>

**中文**

- 根据备用模式、无线电状态和玩家位置返回当前可操作说明及路线后果。
- 意义：让玩家理解切断馈线和求救的影响；只生成文字，不改变状态。

**English**

- Returns contextual instructions and route consequences from power mode, radio state, and location.
- It explains decisions without mutating state.

#### `show_help`

<details>
<summary>查看源代码 / View source — include/decipher_4.py · L218–L277</summary>

```python
def show_help(screen, clues, gate):
    order = ' > '.join(map(str, gate.sequence))
    pages = (
        ('1/3 / MOVE THE BOXES', [
            'Goal: open the doors, unlock 3 terminals, then walk to exit E.', '',
            '@ is you. CAPITAL A/B are boxes. Small a/b are floor plates.',
            'Stand beside a box. Walk INTO it to push it away from you.',
            'You cannot pull a box. Press U if a push puts it in the wrong place.', '',
            'Battery power runs plate a only. Push box A onto a.' if gate.bypass
            else 'Mains power needs BOTH plates: push A onto a and B onto b.',
            'Plate b works after room 3 is repaired; it then needs box B.',
            'Leave the required boxes on their plates to keep the doors open.',
            'D is a closed door. / is an open door.',
        ]),
        ('2/3 / UNLOCK THE TERMINALS', [
            'Use the numbered terminals in this order: ' + order, '',
            'Stand ON or BESIDE a terminal, then press the E key.',
            'Enter its numeric code. Each terminal has a DIFFERENT code.', '',
            'Terminal 1: badge A + offset',
            'Terminal 2: badge C - offset',
            'Terminal 3: badge V + (2 x offset)', '',
            'Tab opens notes: the ACCESS NOTES page lists badge numbers.',
            'Badges are numbers from the drawer, NOT the boxes on this map.',
            'A wrong code or wrong terminal order costs 1 emergency cell.',
        ]),
        ('3/3 / RADIO, ALARM AND EXIT', [
            'O and F are map symbols. Stand nearby and press E to use them.', '',
            'O = rescue radio. It sends your location to a rescue team.',
            'It works only after room 3 is repaired AND both plates are pressed.',
            'Calling rescue leads to an antenna challenge beyond the gate.', '',
            'F = alarm switch. Using it stops the alarm but also disables O.',
            'With room 3 repaired but no call, you escape via a scanner corridor.',
            'If room 3 was skipped, the exit leads to a battery-powered shaft.', '',
            'F and O are optional. Neither replaces the 3 terminal checks.',
            'U undoes actions. Walking onto exit E locks in your escape route.',
        ]),
    )
    page = 0
    screen.timeout(-1)
    while True:
        title, messages = pages[page]
        ready = frame(screen, 'GATE HELP / ' + title, clues,
                      'Left/Right: page    Enter: next/close    H/Esc/Q: close')
        if ready:
            for y, message in enumerate(messages, 5):
                line(screen, y, message)
            screen.refresh()
        key = screen.getch()
        if key in (27, ord('q'), ord('Q')) or ready and key in (ord('h'), ord('H')):
            return
        if not ready:
            continue
        if key in (10, 13, curses.KEY_ENTER):
            if page == len(pages) - 1:
                return
            page += 1
        elif key == curses.KEY_RIGHT:
            page = min(page + 1, len(pages) - 1)
        elif key == curses.KEY_LEFT:
            page = max(0, page - 1)
```

</details>

**中文**

- 按 H 打开三页独立帮助。
- 第一页说明推箱和供电，第二页显示本局的终端顺序并解释密码公式，第三页说明 O、F 和撤离路线。
- 左右键翻页，Enter 继续，H/Esc/Q 关闭。
- 该函数只显示信息，不移动玩家、不扣电池，也不改变无线电状态；尺寸不足时暂停翻页。

**English**

- H opens three help pages: crates and power, the current terminal order and code formulas, then radio/alarm consequences.
- Left/Right changes pages, Enter continues, and H/Esc/Q closes the guide.
- It does not move the player, spend cells, or change radio state.
- Paging pauses when the terminal is too small.

#### `main`

<details>
<summary>查看源代码 / View source — include/decipher_4.py · L281–L391</summary>

```python
def main(screen, clues):
    if 'order' not in clues or 'shift' not in clues or 'badges' not in clues:
        return False
    keys = terminal_keys(clues)
    bypass = 'sequence' not in clues
    # The room uses current power conditions. Leaving lets you repair power.
    # Use a display copy for battery wiring so its sequence is not mistaken for evidence of repaired power.
    display_clues = dict(clues)
    display_clues['emergency'] = bypass
    if bypass:
        numbers = {'A': 1, 'C': 2, 'V': 3}
        sequence = []
        for colour in reversed(clues['order']):
            sequence.append(numbers[colour])
        display_clues['sequence'] = tuple(sequence)
    gate = GatePuzzle(display_clues['sequence'], bypass)
    message = 'Push A onto a and B onto b. H: step-by-step help.'
    if bypass:
        message = 'Battery powers only a. Plate b needs room 3 repaired. H: help.'
    screen.timeout(-1)
    while True:
        display_clues.update(clues)
        ready = frame(screen, '04 / SECURITY INTERLOCK', display_clues,
                      'Arrows: move   E: use   Tab: notes   U: undo   R: reset   H: hint   Q: back')
        if ready:
            required = 1 if bypass else 2
            plates = 0
            for name, position in PLATES.items():
                if name == 'B' and bypass:
                    continue
                if gate.boxes[name] == position:
                    plates += 1
            line(screen, 4, f'Moves {gate.moves} | Plates {plates}/{required} | Terminals {len(gate.entered)}/3')
            # Draw the room, then overlay plates, terminals, crates and player.
            for y, row in enumerate(MAP):
                for x, char in enumerate(row):
                    style = curses.A_DIM
                    if char == 'D':
                        char = '/' if gate.powered else 'D'
                        style = curses.color_pair(2)
                    text(screen, y + 6, x * 3 + 21, char, style)
            for name, (x, y) in PLATES.items():
                text(screen, y + 6, x * 3 + 21, name.lower(), curses.color_pair(1))
            for number, (x, y) in TERMINALS.items():
                colour = 1 if number in gate.entered else 3
                text(screen, y + 6, x * 3 + 21, str(number), curses.color_pair(colour))
            for name, (x, y) in gate.boxes.items():
                text(screen, y + 6, x * 3 + 21, name, curses.color_pair(2) | curses.A_BOLD)
            for symbol, (x, y) in (('O', RADIO), ('F', ALARM)):
                text(screen, y + 6, x * 3 + 21, symbol, curses.color_pair(3))
            x, y = gate.player
            text(screen, y + 6, x * 3 + 21, '@', curses.color_pair(1) | curses.A_BOLD)
            line(screen, 16, '@ you  A/B crates  a/b plates  D doors  E exit  O radio  F alarm')
            number = gate.terminal_nearby()
            context, consequence = gate.fixture_hint()
            if number is not None and not gate.near(ALARM) and not gate.near(RADIO):
                context = f'Press E for terminal {number}. Code = badge ' + FORMULAS[number]
            line(screen, 18, context, curses.color_pair(1) | curses.A_BOLD)
            line(screen, 20, consequence)
            text(screen, 19, 5, message, curses.color_pair(2))
            if gate.near(ALARM) or gate.near(RADIO):
                line(screen, 21, 'U: undo actions step by step. Crossing exit E commits this route.', curses.A_DIM)
            screen.refresh()
        key = screen.getch()
        if key in (27, ord('q'), ord('Q')):
            return False
        if not ready:
            continue
        if key == 9:
            show_notes(screen, display_clues)
        elif key in DIRECTIONS:
            message = gate.move(DIRECTIONS[key])
            if gate.won:
                clues['radio'] = gate.radio
                return True
        elif key in (ord('u'), ord('U')):
            gate.undo()
            message = 'Last valid move or terminal activation undone.'
        elif key in (ord('r'), ord('R')):
            gate = GatePuzzle(display_clues['sequence'], bypass)
            message = 'Room reset. All earlier clues remain in the journal.'
        elif key in (ord('h'), ord('H')):
            show_help(screen, display_clues, gate)
        elif key in (ord('e'), ord('E')):
            result = gate.operate()
            if result is not None:
                message = result
                continue
            number = gate.terminal_nearby()
            if number is None:
                message = 'No device in reach. Move beside a numbered terminal, O or F.'
                continue
            answer = read_command(screen, f'04 / TERMINAL {number} ACCESS', display_clues, [
                f'You are using terminal {number}. Enter a number, not a letter.', '',
                'Code = badge ' + FORMULAS[number],
                f'Badge A: {clues["badges"]["A"]}   C: {clues["badges"]["C"]}   V: {clues["badges"]["V"]}',
                f'Offset from room 1: {clues["shift"]}', '',
                'Terminal order: ' + ' > '.join(map(str, gate.sequence)),
                'Badge letters refer to drawer numbers, not movable boxes.',
                'A wrong code or wrong order costs 1 cell. Esc cancels for free.',
            ], [['Replace the badge letter with its number, then do the calculation.',
                 'For terminal 3, double the offset first, then add badge V.']])
            if answer is not None:
                if gate.powered and not gate.authorized:
                    wrong_code = answer.strip() != str(keys[number])
                    wrong_order = number != gate.sequence[len(gate.entered)]
                    if wrong_code or wrong_order:
                        lose_cell(clues)
                message = gate.activate(answer, keys)
                if clues.get('cells', 3) <= 0:
                    return False
```

</details>

**中文**

- 检查必要线索，计算密码，并以是否存在 sequence 判断备用模式。
- 复制 clues 为 display_clues；备用顺序只写入此副本，避免被误判为已修复电路。
- 循环先画地图，再叠加机关、终端、箱子、设备与玩家；处理移动、撤销、重置和交互；H 打开独立的三页说明。
- 终端输入页面直接列出徽章数字、偏移量和本局顺序，避免混淆箱子与徽章。
- 终端在供电且未授权时输错密码或顺序扣资源；过出口才把 gate.radio 写回共享 clues。
- 意义：临时房间状态和跨关卡事实分开，返回地图重进门禁会重新开始该房间。

**English**

- Checks required clues, computes codes, and chooses battery mode when sequence is absent.
- A display_clues copy holds the battery sequence so it cannot falsely signal restored mains power.
- The loop layers terrain and objects, then handles movement, undo, reset, and devices.
- H opens a separate three-page guide.
- The terminal input screen lists badge numbers, the offset, and the current terminal order.
- Wrong credentials or order cost resources while powered and not authorized.
- Only crossing the exit commits radio to shared clues.
- Temporary room state is separate from persistent run facts; re-entry recreates the gate.

### 3.8 `include/finale.py`

**模块级代码 / Module-level code**

**中文**

- Relay、Corridor、Shaft 共享 title、controls、message、won、draw 和 act 接口，属于鸭子类型，并没有共同自定义父类。
- CORRIDOR 保存地图，SCAN_COLUMNS=(3,5,7,8) 保存扫描列顺序。

**English**

- Relay, Corridor, and Shaft share title, controls, message, won, draw, and act through duck typing, without a custom common superclass.
- CORRIDOR holds terrain and SCAN_COLUMNS=(3,5,7,8) defines the scan sequence.

#### `Relay.__init__`

<details>
<summary>查看源代码 / View source — include/finale.py · L14–L22</summary>

```python
    def __init__(self, seed):
        self.dials = [0, 0, 0]
        self.won = False
        for index in range(3):
            for _ in range(1 + (seed // (4 ** index)) % 3):
                self.turn(index)
        if self.dials == [0, 0, 0]:
            self.turn(0)
        self.message = 'The reply is faint. Align all antennas UP before transmitting.'
```

</details>

**中文**

- 从三个向上的天线开始，用种子控制合法旋转次数打乱，若仍全向上则再转一次。
- 意义：初始状态由合法操作生成，能通过逆向等价旋转解回去，避免生成无解题。

**English**

- Scrambles three upward antennas using seeded legal turns, adding another turn if still solved.
- Constructing the puzzle from legal operations preserves solvability.

#### `Relay.turn`

<details>
<summary>查看源代码 / View source — include/finale.py · L25–L28</summary>

```python
    def turn(self, index):
        self.dials[index] = (self.dials[index] + 1) % 4
        neighbour = (index + 1) % 3
        self.dials[neighbour] = (self.dials[neighbour] + 1) % 4
```

</details>

**中文**

- 把指定天线和下一根天线各顺时针旋转一次，方向用 0–3 加一取模，邻居索引用模 3 循环。
- 意义：一个操作影响两根天线，形成耦合推理。

**English**

- Rotates the selected antenna and its cyclic neighbor modulo four.
- One action affects two dials, creating a coupled puzzle.

#### `Relay.act`

<details>
<summary>查看源代码 / View source — include/finale.py · L31–L43</summary>

```python
    def act(self, action):
        if action in ('1', '2', '3'):
            self.turn(int(action) - 1)
            locked = self.dials.count(0)
            self.message = ('Static only.', 'A voice breaks through.',
                            'The rescue team can almost hear you.',
                            'Clear signal. Press Enter to send the location.')[locked]
        elif action == 'submit':
            if self.dials == [0, 0, 0]:
                self.won = True
            else:
                self.message = f'{self.dials.count(0)}/3 aligned. Each control also turns its neighbour.'
                return 'failure'
```

</details>

**中文**

- 数字键旋转并更新反馈；submit 时只有三个方向都为 0 才获胜，否则返回 failure。
- 意义：旋转免费，错误发送才付出代价；资源扣除交给共享 play。

**English**

- Number actions rotate and update feedback.
- Submission wins only with all zeros; otherwise it returns failure.
- Experimenting is free, while an incorrect transmission is charged by play.

#### `Relay.draw`

<details>
<summary>查看源代码 / View source — include/finale.py · L46–L54</summary>

```python
    def draw(self, screen):
        line(screen, 5, 'Coupled gears: 1 turns 1+2, 2 turns 2+3, 3 turns 3+1.')
        for index, value in enumerate(self.dials):
            x = 14 + index * 22
            style = curses.color_pair(1 if value == 0 else 2)
            text(screen, 9, x, f'ANTENNA {index + 1}')
            text(screen, 11, x + 3, '[ ' + '^>v<'[value] + ' ]', style | curses.A_BOLD)
            text(screen, 14, x + 2, 'LOCKED' if value == 0 else 'DRIFT', style)
        line(screen, 17, 'Target: all ^. Turning is free; a bad transmission costs one cell.')
```

</details>

**中文**

- 画三根天线的方向、是否对齐和耦合规则。
- 意义：将数值状态转换成可读符号，不推进解谜。

**English**

- Draws directions, alignment, and coupling rules.
- Numeric state becomes readable feedback without advancing the puzzle.

#### `Corridor.__init__`

<details>
<summary>查看源代码 / View source — include/finale.py · L76–L81</summary>

```python
    def __init__(self, seed):
        self.start_phase = seed % 4
        self.player = (1, 1)
        self.phase = self.start_phase
        self.won = False
        self.message = 'Power has restarted the scanners. Watch the NEXT sweep.'
```

</details>

**中文**

- 用 seed % 4 设置起始扫描阶段，玩家放在入口，初始化 won 与提示。
- 意义：同一地图可有不同起始节拍，失败后能恢复对应节拍。

**English**

- Sets the initial scan phase from seed modulo four, places the player at the entrance, and initializes feedback.
- The same map can start at different beats and reset consistently.

#### `Corridor.danger`

<details>
<summary>查看源代码 / View source — include/finale.py · L84–L86</summary>

```python
    def danger(self, position, phase):
        x, y = position
        return x == SCAN_COLUMNS[phase] and CORRIDOR[y][x] not in '#C'
```

</details>

**中文**

- 检查位置横坐标是否等于该阶段扫描列，且地形不是墙或掩体 C。
- 意义：集中定义危险规则，绘制预警和实际判定使用同一算法。

**English**

- Checks the phase's scan column while exempting walls and cover C.
- Rendering and detection share one hazard rule.

#### `Corridor.act`

<details>
<summary>查看源代码 / View source — include/finale.py · L89–L109</summary>

```python
    def act(self, action):
        if action == 'wait':
            dx, dy = 0, 0
        elif isinstance(action, tuple):
            dx, dy = action
        else:
            return
        target = (self.player[0] + dx, self.player[1] + dy)
        x, y = target
        if not (0 <= y < len(CORRIDOR) and 0 <= x < len(CORRIDOR[0])) or CORRIDOR[y][x] == '#':
            self.message = 'Wall. No movement or scan tick was spent.'
            return
        self.phase = (self.phase + 1) % 4
        if self.danger(target, self.phase):
            self.player = (1, 1)
            self.phase = self.start_phase
            self.message = 'Detected. Back at the entrance; avoid the marked NEXT sweep.'
            return 'failure'
        self.player = target
        self.won = CORRIDOR[y][x] == 'E'
        self.message = 'Cover shields you from every sweep.' if CORRIDOR[y][x] == 'C' else 'One beat passed. Study the next sweep before moving.'
```

</details>

**中文**

- 将 wait 视为原地行动，方向元组视为移动；越界或撞墙不推进扫描。
- 有效行动先将 phase 加一取模，再检查目标是否危险；被发现则玩家和阶段重置并返回 failure，否则更新位置并检查 E。
- 意义：玩家需要规划“下一次”扫描，失败成本由共享循环处理。

**English**

- Treats wait as staying still and tuples as movement.
- Invalid terrain spends no scan tick.
- Valid actions advance phase before checking the destination; detection resets player and phase and reports failure.
- Otherwise movement can reach E.
- Planning concerns the next sweep, and shared code applies the penalty.

#### `Corridor.draw`

<details>
<summary>查看源代码 / View source — include/finale.py · L112–L129</summary>

```python
    def draw(self, screen):
        line(screen, 4, f'Scan beat {self.phase + 1}/4. Movement and waiting advance one beat.')
        for y, row in enumerate(CORRIDOR):
            for x, tile in enumerate(row):
                pos = (x, y)
                style = curses.A_DIM
                if tile != '#':
                    if self.danger(pos, (self.phase + 1) % 4):
                        tile, style = '!', curses.color_pair(2)
                    elif self.danger(pos, self.phase):
                        tile, style = ':', curses.color_pair(3)
                    elif tile in 'CE':
                        style = curses.color_pair(1)
                if pos == self.player:
                    tile, style = '@', curses.color_pair(1) | curses.A_BOLD
                text(screen, y + 7, x * 3 + 24, tile, style)
        line(screen, 16, '@ you    ! next sweep    : current sweep    C cover    E exit')
        line(screen, 18, 'Time moves only when you act. Detection costs one cell.')
```

</details>

**中文**

- 画地图、当前扫描冒号、下次扫描感叹号、掩体与玩家。
- 意义：明确预告下一步风险，让回合制挑战可规划。

**English**

- Draws terrain, current scans as colons, next scans as exclamation marks, cover, and player.
- Visible forecasts make the turn-based challenge predictable.

#### `Shaft.__init__`

<details>
<summary>查看源代码 / View source — include/finale.py · L138–L142</summary>

```python
    def __init__(self, seed):
        self.target = 1 + seed % 2
        self.won = False
        self.reset()
        self.message = 'One battery, three devices. Scan the ledge before building a path.'
```

</details>

**中文**

- 由种子选择目标桥位 1 或 2，初始化 won 并调用 reset。
- 意义：将固定目标和每次尝试的可变资源分开。

**English**

- Selects bridge target 1 or 2 from the seed, initializes won, and calls reset.
- The fixed target is separate from attempt resources.

#### `Shaft.reset`

<details>
<summary>查看源代码 / View source — include/finale.py · L145–L150</summary>

```python
    def reset(self):
        self.energy = 7
        self.device = 0
        self.bridge = 0
        self.position = 0
        self.scanned = False
```

</details>

**中文**

- 恢复七点电量、未连接设备、桥位 0、码头位置和未扫描状态。
- 意义：重启竖井尝试不改变整局 cells，也不重新生成目标。

**English**

- Restores seven charge, no connected device, bridge zero, dock position, and unscanned status.
- Restarting an attempt does not refill run cells or regenerate the target.

#### `Shaft.act`

<details>
<summary>查看源代码 / View source — include/finale.py · L153–L200</summary>

```python
    def act(self, action):
        if action in ('1', '2', '3'):
            device = int(action)
            if self.position != 0:
                self.message = 'Battery sockets are at the dock. Walk back to reconnect.'
                return
            if device == self.device:
                self.message = 'Already connected. No charge used.'
                return
            self.device = device
            self.energy -= 1
            if device == 1:
                self.scanned = True
                self.message = f'Light reveals ledge {self.target}. The marking is now recorded.'
            elif device == 2:
                self.message = 'Bridge motor online. Space cycles alignment 0 > 1 > 2.'
            else:
                self.message = 'Lift online. Cross the latched bridge, then press Enter.'
        elif action == 'wait':
            if self.device != 2 or self.position != 0:
                self.message = 'Align from the dock with the bridge motor connected.'
                return
            self.bridge = (self.bridge + 1) % 3
            self.energy -= 1
            self.message = 'Alignment set. The mechanical latch holds without power.'
        elif isinstance(action, tuple):
            dx, dy = action
            if dy or dx == 0:
                return
            target = self.position + dx
            if not 0 <= target <= 2:
                return
            if not self.scanned or self.bridge != self.target:
                self.message = 'No safe crossing. Scan the ledge and align the bridge first.'
                return
            self.position = target
            self.message = 'Walking uses no charge. Battery sockets remain at the dock.'
        elif action == 'submit':
            if self.position != 2 or self.device != 3:
                self.message = 'Stand on the lift with its cable connected.'
                return
            self.energy -= 1
            self.won = True
            return
        if self.energy <= 0:
            self.reset()
            self.message = 'Battery depleted. One cell restarts the shaft with 7 charge.'
            return 'failure'
```

</details>

**中文**

- 数字 1/2/3 在码头切换灯、桥电机或升降机，每次实际切换扣一点；灯揭示目标。
- wait 在码头且连接电机时循环桥位并扣电。
- 左右移动需已扫描且桥对齐，不耗电；submit 在升降机位置且已供电时扣一点并获胜。
- 其他耗电动作若耗尽电量则 reset 并返回 failure。
- 意义：把设备分配、信息获取和有限预算组合成顺序规划；桥位在断电后仍保持。

**English**

- At the dock, number actions switch the light, bridge motor, or lift at one charge per actual change; light reveals the target.
- Wait aligns the powered bridge from the dock at a cost.
- Walking requires a scan and correct bridge alignment but is free.
- Submission at the powered lift spends one charge and wins.
- Other charge depletion resets the attempt and reports failure.
- Device allocation and a latched bridge create a resource-planning puzzle.

#### `Shaft.draw`

<details>
<summary>查看源代码 / View source — include/finale.py · L203–L212</summary>

```python
    def draw(self, screen):
        devices = ('none', 'light', 'bridge motor', 'lift')
        line(screen, 5, f'Charge {self.energy}/7    Connected: {devices[self.device]}')
        line(screen, 8, '[1] LIGHT          [2] BRIDGE MOTOR          [3] LIFT')
        line(screen, 10, 'Dock  ----------------  Bridge  ----------------  Lift')
        text(screen, 12, (6, 30, 57)[self.position], '@', curses.color_pair(1) | curses.A_BOLD)
        target = str(self.target) if self.scanned else '? (connect light to inspect)'
        line(screen, 15, f'Bridge alignment: {self.bridge}    Safe ledge: {target}')
        line(screen, 17, 'Connect / align / launch: 1 charge each. Walking and notes are free.')
        line(screen, 18, 'Aligned bridges stay latched even after their power is disconnected.')
```

</details>

**中文**

- 显示剩余电量、供电对象、玩家位置、桥位与已知/未知目标。
- 意义：将隐藏信息与已发现信息区分，并说明各动作的成本。

**English**

- Displays charge, powered device, player, bridge, and known or unknown target.
- It distinguishes discovered information and makes action costs visible.

#### `make_room`

<details>
<summary>查看源代码 / View source — include/finale.py · L216–L221</summary>

```python
def make_room(kind, seed):
    if kind == 'DAWN':
        return Relay(seed)
    if kind == 'SILENT EXIT':
        return Corridor(seed)
    return Shaft(seed)
```

</details>

**中文**

- 按 DAWN、SILENT EXIT 创建 Relay 或 Corridor，其他值返回 Shaft。
- 意义：把结局到对象的选择集中；调用路径应传入合法结局，这个函数本身不拒绝未知字符串。

**English**

- Creates Relay for DAWN, Corridor for SILENT EXIT, otherwise Shaft.
- It centralizes branch construction; callers should supply a valid ending because unknown strings also fall back to Shaft.

#### `play`

<details>
<summary>查看源代码 / View source — include/finale.py · L225–L258</summary>

```python
def play(screen, clues, kind):
    # Keep the room object on return to the map: no free battery refill on Q.
    if 'exit_room' not in clues:
        clues['exit_room'] = make_room(kind, clues.get('seed', 0))
    room = clues['exit_room']
    screen.timeout(-1)
    while clues.get('cells', 3) > 0:
        if room.won:
            return True
        ready = frame(screen, room.title, clues, room.controls)
        if ready:
            room.draw(screen)
            line(screen, 20, room.message, curses.color_pair(2))
            screen.refresh()
        key = screen.getch()
        if key in (27, ord('q'), ord('Q')):
            return False
        if not ready or key == curses.KEY_RESIZE:
            continue
        if key == 9:
            show_notes(screen, clues)
            continue
        # Translate keys into direction tuples or action names; unknown keys do not advance the puzzle.
        action = DIRECTIONS.get(key)
        if key in (10, 13, curses.KEY_ENTER):
            action = 'submit'
        elif key == ord(' '):
            action = 'wait'
        elif key in (ord('1'), ord('2'), ord('3')):
            action = chr(key)
        # Apply reported failures here so all challenges share the same cell and fuse rules.
        if room.act(action) == 'failure':
            lose_cell(clues)
    return False
```

</details>

**中文**

- exit_room 不存在才创建，并保存在 clues 中。
- 循环调用统一的 title、controls、draw、act、won 等接口，将按键转换为方向、submit、wait 或数字；act 返回 failure 才统一扣资源。
- Tab 打开笔记，Q 返回但保留对象。
- 意义：三种类共享行为接口，无须继承共同父类；返回地图不能免费重置最终挑战。

**English**

- Creates exit_room only if absent and stores it in clues.
- The loop uses shared attributes and methods, maps keys to actions, and charges resources only on failure.
- Notes and returning preserve the object.
- The classes share an interface without inheriting a common base class, and leaving cannot reset finale resources for free.

### 3.9 `include/savegame.py`

**模块级代码 / Module-level code**

**中文**

- SAVE_PATH 从当前源文件路径推导项目根目录，因此存档不随启动目录改变。
- 导入 finale 用于按具体类型序列化和重建；没有 eval 或 pickle。

**English**

- SAVE_PATH derives the project root from the source path rather than the current working directory.
- Finale classes support type-specific serialization and reconstruction.
- Neither eval nor pickle is used.

#### `number`

<details>
<summary>查看源代码 / View source — include/savegame.py · L11–L15</summary>

```python
def number(value, low, high):
    result = int(value)
    if not low <= result <= high:
        raise ValueError('Invalid checkpoint value')
    return result
```

</details>

**中文**

- 将字符串转整数并检查上下界，非法时抛 ValueError。
- 意义：集中校验数字字段，异常由上层界面转为提示。

**English**

- Converts a value to an integer and checks bounds, raising ValueError on invalid input.
- Numeric validation is shared and the UI handles errors.

#### `encode`

<details>
<summary>查看源代码 / View source — include/savegame.py · L19–L41</summary>

```python
def encode(clues, solved, selected):
    room = clues.get('exit_room')
    state = '-'
    if isinstance(room, finale.Relay):
        state = room.dials + [int(room.won)]
    elif isinstance(room, finale.Corridor):
        state = [*room.player, room.phase, int(room.won)]
    elif isinstance(room, finale.Shaft):
        state = [room.energy, room.device, room.bridge, room.position,
                 int(room.scanned), int(room.won)]
    if state != '-':
        state = ','.join(map(str, state))
    # Line order: version, seed, cells, bonus charge, fuse, modules, completed rooms,
    # map selection, radio state, ending type, escaped flag, and exit challenge state.
    # A dash marks absent data; parsing converts values and never executes file contents.
    return '\n'.join((
        'UNDERGROUND SAVE 1', str(clues['seed']), str(clues['cells']),
        str(clues['bonus_charge']), str(int(clues['fuse'])),
        '|'.join(clues['modules']) or '-',
        ''.join(str(int(done)) for done in solved), str(selected),
        clues.get('radio', '-'), clues.get('finale_kind', '-'),
        str(int(clues.get('escaped', False))), state,
    )) + '\n'
```

</details>

**中文**

- 将状态编码为固定 12 行文本；布尔值用 0/1，空值用减号，模块用竖线，最终挑战状态按类型用逗号分隔。
- 意义：存档可读、无需额外库，也不保存可执行对象；可从种子重建的线索不重复存储。

**English**

- Encodes twelve text lines using 0/1 Booleans, dash placeholders, pipe-separated modules, and type-specific comma-separated finale state.
- Saves are readable, need no extra library, and contain no executable objects; seed-derived clues need not be duplicated.

#### `decode`

<details>
<summary>查看源代码 / View source — include/savegame.py · L45–L116</summary>

```python
def decode(contents):
    fields = contents.splitlines()
    if len(fields) != 12 or fields[0] != 'UNDERGROUND SAVE 1':
        raise ValueError('Unsupported or incomplete checkpoint')
    seed = number(fields[1], 0, 7999)
    clues = new_run(seed)
    clues['cells'] = number(fields[2], 0, 5)
    clues['bonus_charge'] = number(fields[3], 0, 240)
    clues['fuse'] = bool(number(fields[4], 0, 1))
    clues['modules'] = [] if fields[5] == '-' else fields[5].split('|')
    if len(clues['modules']) > 2 or any(m not in MODULES for m in clues['modules']):
        raise ValueError('Invalid modules')
    if len(fields[6]) != 4 or any(c not in '01' for c in fields[6]):
        raise ValueError('Invalid room progress')
    solved = [c == '1' for c in fields[6]]
    if (solved[1] and not solved[0]) or (any(solved[2:]) and not solved[1]):
        raise ValueError('Missing earlier room')
    selected = number(fields[7], 0, 4)
    # Rebuild fixed clues from this run's seed and completed rooms.
    if solved[0]:
        clues['shift'] = 7
    if solved[1]:
        clues['order'] = decipher_2.make_order(seed)
        clues['badges'] = decipher_2.make_badges(seed)
    if solved[2]:
        clues['sequence'] = power_sequence(clues)
    if fields[8] not in ('-', 'idle', 'sent', 'cut'):
        raise ValueError('Invalid radio state')
    if fields[8] != '-':
        clues['radio'] = fields[8]
    escaped = bool(number(fields[10], 0, 1))
    if not solved[3]:
        if fields[8:10] != ['-', '-'] or escaped or fields[11] != '-':
            raise ValueError('Exit reached before gate')
        return clues, solved, selected
    expected = ('DAWN' if clues.get('radio') == 'sent' else 'SILENT EXIT') if solved[2] else 'LAST LIGHT'
    if fields[9] != expected or fields[11] == '-':
        raise ValueError('Invalid exit passage')
    clues['finale_kind'] = expected
    # Create the matching challenge before restoring mutable fields; code and seed define its fixed layout.
    room = finale.make_room(expected, seed)
    values = fields[11].split(',')
    if isinstance(room, finale.Relay):
        if len(values) != 4:
            raise ValueError('Invalid antenna state')
        room.dials = [number(v, 0, 3) for v in values[:3]]
    elif isinstance(room, finale.Corridor):
        if len(values) != 4:
            raise ValueError('Invalid corridor state')
        x, y = number(values[0], 0, 10), number(values[1], 0, 6)
        if finale.CORRIDOR[y][x] == '#':
            raise ValueError('Player inside wall')
        room.player = (x, y)
        room.phase = number(values[2], 0, 3)
    else:
        if len(values) != 6:
            raise ValueError('Invalid shaft state')
        room.energy = number(values[0], 0, 7)
        room.device = number(values[1], 0, 3)
        room.bridge = number(values[2], 0, 2)
        room.position = number(values[3], 0, 2)
        room.scanned = bool(number(values[4], 0, 1))
    room.won = bool(number(values[-1], 0, 1))
    if isinstance(room, finale.Shaft) and room.energy == 0 and not room.won:
        raise ValueError('Unfinished shaft without power')
    if escaped != room.won:
        raise ValueError('Incomplete ending')
    room.message = 'Progress restored. Continue from where you left off.'
    clues['exit_room'] = room
    if escaped:
        clues['escaped'] = True
    return clues, solved, selected
```

</details>

**中文**

- 先检查行数和格式版本，再检查种子、资源、模块、完成标记及前置关系；根据种子重建线索。
- 门禁未完成时拒绝提前出现的结局数据。
- 已完成门禁时核对分支，创建对应挑战并恢复有范围约束的字段，最后核对 escaped 与 won。
- 意义：先构造并验证一份候选状态再返回，读取失败不会先覆盖当前局。
- 它检查格式和部分一致性，不证明每份存档都可由合法操作达到。

**English**

- Checks line count and version, then ranges, modules, completion flags, and prerequisites.
- It reconstructs clues from the seed, rejects premature finale data, verifies the expected branch, restores typed challenge fields, and checks escaped against won.
- Candidate state is returned only after validation.
- This checks format and selected consistency rules, not full gameplay reachability.

#### `save`

<details>
<summary>查看源代码 / View source — include/savegame.py · L120–L124</summary>

```python
def save(clues, solved, selected):
    contents = encode(clues, solved, selected)
    decode(contents)  # Validate before replacing the previous checkpoint.
    with open(SAVE_PATH, 'w', encoding='utf-8') as checkpoint:
        checkpoint.write(contents)
```

</details>

**中文**

- 先 encode，再 decode 自检，通过后以 UTF-8 写入 progress.sav。
- 意义：在覆盖旧文件前检查序列化状态；写入采用直接覆盖，并不是临时文件加原子替换。

**English**

- Encodes, validates by decoding, then writes UTF-8 to progress.sav.
- State is checked before overwrite, but writing is direct rather than an atomic temporary-file replacement.

#### `load`

<details>
<summary>查看源代码 / View source — include/savegame.py · L128–L133</summary>

```python
def load():
    with open(SAVE_PATH, encoding='utf-8') as checkpoint:
        contents = checkpoint.read(4097)
    if len(contents) > 4096:
        raise ValueError('Checkpoint is too large')
    return decode(contents)
```

</details>

**中文**

- 最多读取 4097 个字符，超过 4096 则拒绝，再交给 decode。
- 意义：限制文本读取量，将文件 I/O 和状态解析分开。
- 这里的限制按文本字符而不是字节计算。

**English**

- Reads up to 4097 text characters, rejects more than 4096, then decodes.
- This limits input size and separates file access from parsing.
- The limit is in characters, not bytes.

### 3.10 `include/archive.py`

**模块级代码 / Module-level code**

**中文**

- ENDINGS 限定三个合法结局；STORY 是三页标题与正文数据。
- Archive 管集合与文件，show_story/show_archive 管界面。

**English**

- ENDINGS defines the three valid outcomes and STORY contains three narrative pages.
- Archive manages records and storage; show_story and show_archive handle presentation.

#### `Archive.__init__`

<details>
<summary>查看源代码 / View source — include/archive.py · L43–L57</summary>

```python
    def __init__(self):
        # Separate from the run checkpoint: loading an old run cannot erase wins.
        self.path = savegame.SAVE_PATH.rsplit('/', 1)[0] + '/endings.sav'
        self.completed = set()
        self.error = ''
        try:
            with open(self.path, encoding='utf-8') as records:
                rows = records.read(1025).splitlines()
            self.completed = set(rows) & set(ENDINGS)
            if any(row not in ENDINGS for row in rows):
                self.error = 'Some archive records could not be read.'
        except FileNotFoundError:
            pass
        except (OSError, UnicodeError):
            self.error = 'Archive could not be read. Check the game folder.'
```

</details>

**中文**

- 读取独立 endings.sav，并与允许的结局集合取交集；文件不存在则视为空收藏，未知记录和读取异常记入 error。
- 意义：用 set 去重，收藏不随当前局重置；异常不会立刻终止游戏。

**English**

- Reads a separate endings.sav and intersects its rows with allowed endings.
- Missing files mean an empty collection; unknown records and read errors populate error.
- A set deduplicates achievements independently of run resets.

#### `Archive.unlocked`

<details>
<summary>查看源代码 / View source — include/archive.py · L60–L62</summary>

```python
    @property
    def unlocked(self):
        return len(self.completed) == len(ENDINGS)
```

</details>

**中文**

- 比较已收集的不同结局数量与 ENDINGS 数量。
- 意义：隐藏剧情要求三种不同结局，同一结局重复通关不增加进度。

**English**

- Compares the count of distinct collected endings with ENDINGS.
- Repeated completion of one route cannot unlock the story.

#### `Archive.record`

<details>
<summary>查看源代码 / View source — include/archive.py · L65–L81</summary>

```python
    def record(self, kind):
        """Return True only when a distinct win completes the collection."""
        if kind not in ENDINGS:
            return False
        was_unlocked = self.unlocked
        if kind in self.completed and not self.error:
            return False
        # Keep the achievement in memory even if writing fails, allowing a later save retry.
        self.completed.add(kind)
        try:
            with open(self.path, 'w', encoding='utf-8') as records:
                records.write(''.join(name + '\n' for name in ENDINGS
                                      if name in self.completed))
            self.error = ''
        except OSError:
            self.error = 'Ending kept this session only. Open Archive to retry saving.'
        return self.unlocked and not was_unlocked
```

</details>

**中文**

- 拒绝未知结局；已有记录且无错误时直接返回。
- 否则将结局加入内存集合并按固定顺序写文件；失败仍保留内存数据和 error。
- 返回值表示本次是否刚解锁全部收藏，不是一般的保存成功标记。
- 意义：支持写入失败后重试，并避免反复自动弹出隐藏剧情。

**English**

- Rejects unknown endings and skips error-free duplicates.
- Otherwise it adds the ending in memory and writes records in fixed order, retaining state and an error on failure.
- Its return value means newly unlocked, not simply saved successfully.
- This supports retries and prevents repeated automatic story popups.

#### `show_story`

<details>
<summary>查看源代码 / View source — include/archive.py · L85–L106</summary>

```python
def show_story(screen, clues):
    page = 0
    screen.timeout(-1)
    while True:
        title, messages = STORY[page]
        ready = frame(screen, title, clues,
                      'Enter/Right: next    Left: previous    Esc/Q: return')
        if ready:
            for row, message in enumerate(messages, 6):
                line(screen, row, message)
            screen.refresh()
        key = screen.getch()
        if key in (27, ord('q'), ord('Q')):
            return
        if not ready:
            continue
        if key in (10, 13, curses.KEY_ENTER, curses.KEY_RIGHT):
            if page == len(STORY) - 1:
                return
            page += 1
        elif key == curses.KEY_LEFT:
            page = max(0, page - 1)
```

</details>

**中文**

- 按 STORY 页码显示标题和文字，左右翻页，最后一页继续则返回；尺寸不足时不翻页。
- 意义：用数据驱动多页叙事，不需要为每页写独立函数。

**English**

- Displays pages from STORY, supports navigation, and exits after the last page; undersized terminals suspend paging.
- Narrative pages are data-driven.

#### `show_archive`

<details>
<summary>查看源代码 / View source — include/archive.py · L110–L131</summary>

```python
def show_archive(screen, clues, collection):
    if collection.error and collection.completed:
        collection.record(next(iter(collection.completed)))
    screen.timeout(-1)
    while True:
        controls = 'Enter: play recovered transmission    Esc/Q: return' if collection.unlocked else 'Esc/Q: return'
        ready = frame(screen, 'EVACUATION ARCHIVE', clues, controls)
        if ready:
            line(screen, 5, f'Recovered records: {len(collection.completed)} / 3')
            for index, name in enumerate(ENDINGS):
                line(screen, 8 + index * 2,
                     '[RECOVERED] ' + name if name in collection.completed else '[MISSING]   Unknown evacuation record')
            line(screen, 16, 'THE FOURTH SIGNAL / UNLOCKED' if collection.unlocked
                 else 'Three different escapes will complete the transmission.')
            line(screen, 18, 'Ending records are saved automatically across expeditions.')
            line(screen, 20, collection.error, curses.color_pair(2))
            screen.refresh()
        key = screen.getch()
        if key in (27, ord('q'), ord('Q')):
            return
        if ready and collection.unlocked and key in (10, 13, curses.KEY_ENTER):
            show_story(screen, clues)
```

</details>

**中文**

- 有未保存错误且有记录时先尝试重写，再显示已收集和缺失结局、错误及解锁状态；已解锁时 Enter 重播故事。
- 意义：收藏既是跨局目标，也是失败写入的重试入口。

**English**

- Retries writing when an error and existing records are present, then shows collected and missing endings, errors, and unlock state.
- Enter replays the unlocked story.
- The archive is both a cross-run goal and a save-retry entry point.

## 4. 关键逻辑拆解示例 / Key logic examples

### 4.1 容器副本与共享状态 / Copies and shared state

```python
display_clues = dict(clues)
display_clues['sequence'] = tuple(sequence)
```

**中文**

- 这是浅拷贝。
- 新增顶层 sequence 不会写入原 clues，因此备用接线不会伪装成完成电路；已有的嵌套对象仍可能共享。
- 门禁没有用这个副本深度修改 badges 等对象。
- 与之不同，给函数直接传 clues 后执行 clues['shift']=7，会修改所有调用方看到的同一个字典。

**English**

- This is a shallow copy.
- Adding a top-level sequence does not modify the original clues, so battery wiring cannot masquerade as restored power.
- Nested objects may still be shared; the gate does not deeply mutate badges through this copy.
- Passing clues directly and assigning clues['shift']=7 updates the original shared dictionary.

### 4.2 电路蛇尾判定 / Circuit tail collision

```python
body = self.snake if colour else self.snake[:-1]
```

**中文**

- 普通移动会移走尾巴，因此新头进入旧尾位置不应算撞自己；吃节点时尾巴不移走，必须把整个蛇身都算作障碍。
- 这个差异保证碰撞判定符合“本次移动之后”的身体状态。

**English**

- On an ordinary move the tail departs, so its previous cell is safe.
- When collecting a node the tail stays, so the full body blocks movement.
- Collision checks account for the resulting body state.

### 4.3 顺序验证 / Sequence validation

```python
nearby != self.sequence[len(self.entered)]
```

**中文**

- entered 长度就是已完成几个终端，因此它同时是下一个目标的索引。
- 只有尚未全部授权时才继续检查；全部完成后先返回，避免访问索引 3 越界。
- 错误顺序清空 entered，要求从头验证。

**English**

- The number of accepted terminals is also the index of the next required terminal.
- Existing authorization is handled first, preventing an out-of-range access after three successes.
- A wrong order clears progress and requires restarting verification.

### 4.4 存档 12 行结构 / Twelve-line checkpoint

| 行 / Line | 内容 / Content |
| --- | --- |
| 1 | 格式版本 / Format version: UNDERGROUND SAVE 1 |
| 2 | 种子 / Seed |
| 3 | 整局电池 / Run cells |
| 4 | 电容额外电量 / Bonus circuit charge |
| 5 | 保险丝布尔值 / Fuse flag |
| 6 | 模块列表 / Module list |
| 7 | 四关完成标记 / Four completion flags |
| 8 | 地图选中项 / Map selection |
| 9 | 无线电状态 / Radio state |
| 10 | 固定结局 / Committed ending |
| 11 | 是否已逃脱 / Escaped flag |
| 12 | 最终挑战可变字段 / Mutable finale state |

**中文**

- 游戏的存档版本字符串、课程容器版本 2026-v03 和 Python 版本是不同概念。
- 普通电路和门禁的未完成内部状态不在此结构中；最终挑战对象的关键字段会保存。

**English**

- The checkpoint format version, course container version 2026-v03, and Python version are separate concepts.
- Unfinished circuit and gate internals are not stored here, but key finale fields are persisted.

## 5. 讲解时需要说准确的边界 / Boundaries to explain accurately

- 中文：第三关是可选房间，不是第四关的必经前置。English: Room three is optional, not a prerequisite for room four.
- 中文：不是所有类都完全不画图；EnergyCircuit 和 GatePuzzle 主要管状态，三个最终挑战类还各自提供 draw。English: Not every class is purely nonvisual: EnergyCircuit and GatePuzzle focus on state, while finale classes also provide draw methods.
- 中文：种子控制部分数值、顺序和节点变化，房间地形不是随机生成的。English: Seeds vary selected values, orders, and node positions; room terrain is not randomly generated.
- 中文：电池是整局失败预算，电路 charge 和竖井 energy 是局部动作预算。English: Cells are the run-wide failure budget; circuit charge and shaft energy are local action budgets.
- 中文：退出关卡不一定恢复原状：电路与门禁重进会重新建立，最终挑战对象保留。English: Re-entry recreates the circuit and gate, but retains the finale object.
- 中文：存档校验不等于防作弊，也不是完整可达性证明；直接写文件也不保证写入中断时旧档完好。English: Validation is neither anti-cheat nor a full reachability proof; direct writes do not guarantee an old save survives interruption.
- 中文：课程要求中的 subclass 是课程班别；这里的三个最终挑战类并非通过继承形成的子类。English: The course’s “subclass” field refers to the class section; the three finale classes are not inheritance-based subclasses of a custom base.

## 6. 常见语法与意义 / Common syntax and purpose

| 写法 / Syntax | 中文 | English |
| --- | --- | --- |
| `dict.get(key, default)` | 键不存在时取默认值，不会把默认值写入字典 | Reads a fallback without inserting it |
| `dict.setdefault(key, value)` | 键不存在才写入，用于固定结局 | Inserts only when absent, used to commit a branch |
| `@property` | 用属性形式读取计算结果，如 powered | Exposes a computed result as an attribute |
| `%` / `//` | 取模与整除，用于循环索引和种子分段 | Modulo and integer division for cycles and seed components |
| `tuple` | 保存固定顺序或坐标 | Holds fixed sequences or coordinates |
| `set` | 自动去重，用于结局收藏 | Deduplicates collected endings |
| `append` / `pop` | 向列表尾部压入/取出，用于撤销栈 | Pushes/pops list items for undo history |
| `isinstance` | 根据最终挑战类型选择存储字段 | Selects serialization fields by challenge type |
| `with open(...)` | 作用域结束时自动关闭文件 | Closes the file when the context exits |
| `try/except` | 将可预期错误转为可处理分支 | Converts anticipated errors into handled branches |
| `continue` / `return` | 分别进入下一轮循环 / 结束当前函数 | Starts the next loop iteration / exits the function |
| `timeout(-1)` / `timeout(0)` | 阻塞等键 / 立即读取，没有键也返回 | Blocking input / immediate polling |

**中文**

- 本说明不修改程序；展开“查看源代码”即可阅读函数源码。预览是本次更新时的快照，代码修改后需同步更新。
- 它是本地学习材料，不加入版本控制。

**English**

- This guide does not modify the program.
- Expand View source to read an embedded snapshot of the function. Previews reflect the code when this guide was updated.
- It is local study material excluded from version control.
