"""
display/curses/container
"""

# import curses
from curses import (A_NORMAL, A_BOLD, A_STANDOUT)
from typing import (Any, List)

from bank.display.my_curses.main import (NoOverrideError, WinId, DisplayerMain)
from bank.display.my_curses.item_display import DisplayerItem

from bank.utils.return_code import RetCode

class DisplayerContainer():
    """
    Curses container (account, statement) display
    """

    def __init__(self, disp: DisplayerMain, item_disp: DisplayerItem) -> None:

        # Main display
        self.disp = disp

        # Item display
        self.item_disp = item_disp

        self.title = ""
        self.subtitle = ""

        # Highlighted item
        self.item_hl: Any = None

        # Selected item list
        self.item_sel_list: List[Any] = []

        # Focused item index
        self.item_focus_idx: int = 0

    def raise_no_override(self, method: str = "") -> None:
        """
        Raise method not overriden exception

        Args:
            method_name (str, optional): Method name. Defaults to "".
        """

        raise NoOverrideError(
            base_class="DisplayerContainer",
            derived_class=type(self).__name__,
            method=method)

    def get_container_name(self) -> str:
        """
        Get container name
        """

        self.raise_no_override("get_container_name")
        return ""

    def get_container_item_list(self) -> List[Any]:
        """
        Get container item list
        """

        self.raise_no_override("get_container_item_list")
        return []

    def edit_container_item(self, item: Any) -> bool:
        """
        Edit container item
        """

        self.raise_no_override("edit_container_item")
        _ = item
        return False

    def browse_container_item(self, item: Any) -> None:
        """
        Browse container item
        """

        self.raise_no_override("browse_container_item")
        _ = item

    def create_container_item(self) -> Any:
        """
        Create container item
        """

        self.raise_no_override("create_container_item")
        return Any

    def add_container_item(self, item: Any) -> None:
        """
        Add container item

        Args:
            item (Any): Item
        """

        self.raise_no_override("add_container_item")
        _ = item

    def add_container_item_list(self, item_list: List[Any]) -> None:
        """
        Add container item list

        Args:
            item_list (List[Any]): Item list
        """

        self.raise_no_override("add_container_item_list")
        _ = item_list

    def remove_container_item_list(self, item_list: List[Any], force: bool = False) -> RetCode:
        """
        Remove item list
        """

        if len(item_list) == 0:
            # No item to remove
            return RetCode.OK

        if force:
            # Dont ask confirm
            return RetCode.OK

        msg = f"Remove {len(item_list)} items"

        choice_list = [
            "Cancel",
            "Remove"
        ]

        choice_idx = self.disp.display_choice_menu("REMOVE ITEMS", msg, choice_list)

        # Default : Cancel
        ret = RetCode.CANCEL
        if choice_idx == 1:
            # Remove items
            ret = RetCode.OK

        return ret

    def remove_container_item(self, item: Any) -> None:
        """
        Remove cotnainer item

        Args:
            item (Any): Item
        """

        self.raise_no_override("remove_container_item")
        _ = item

    def copy(self) -> None:
        """
        Copy selected or highlited item(s)
        """

        if len(self.item_sel_list) > 0:
            item_list = self.item_sel_list
        elif self.item_hl is not None:
            item_list = [self.item_hl]
        else:
            return

        self.disp.item_list_clipboard.set(item_list)

    def highlight_closest_item(self, item_list: List) -> None:
        """
        Highlist closes item
        """

        container_item_list = self.get_container_item_list()
        item_hl_idx = container_item_list.index(self.item_hl)

        while item_hl_idx >= 0 and self.item_hl in item_list:
            # Highligh previous item
            item_hl_idx -= 1
            self.item_hl = container_item_list[item_hl_idx]

        while item_hl_idx < len(container_item_list) and self.item_hl in item_list:
            # Highligh next item
            item_hl_idx += 1
            self.item_hl = container_item_list[item_hl_idx]

        if self.item_hl in item_list:
            self.item_hl = None

    def cut(self) -> None:
        """
        Cut selected or highlited item(s)
        """

        if len(self.item_sel_list) > 0:
            item_list = self.item_sel_list
        elif self.item_hl is not None:
            item_list = [self.item_hl]
        else:
            return

        self.disp.item_list_clipboard.set(item_list)

        # If highlighted item in buffer
        if self.item_hl in item_list:
            self.highlight_closest_item(item_list)

        # Remove items list
        for item in item_list:
            self.remove_container_item(item)

        self.item_sel_list.clear()

    def paste(self) -> None:
        """
        Paste item(s)
        """

        item_list = self.disp.item_list_clipboard.get()
        if item_list is None or len(item_list) == 0:
            return

        # Add item list
        for item in item_list:
            self.add_container_item(item)

        self.item_hl = item_list[0]

    def rappr(self) -> None:
        """
        Rappr selected or highlited item(s)
        """

        if len(self.item_sel_list) > 0:
            item_list = self.item_sel_list
        elif self.item_hl is not None:
            item_list = [self.item_hl]
        else:
            return

        if self.disp.cont_disp_last is not None:

            self.disp.cont_disp_last.add_container_item_list(item_list)
            self.disp.cont_disp_last.save()
            self.remove_container_item_list(item_list, force=True)

            # TODO to improve
            self.item_sel_list.clear()
            # if self.item_hl in item_list:
            #     self.item_hl = None
            #     if len(self.disp.get_container_item_list()) > 0:
            #         self.item_hl = self.get_container_item_list()[0]
            self.item_hl = self.get_container_item_list()[0]

    def save(self) -> None:
        """
        Save
        """

        self.raise_no_override("save")

    def exit(self) -> RetCode:
        """
        Exit
        """

        choice_list = [
            "Cancel",
            "Save and exit",
            "Exit discarding changes"
        ]

        choice_idx = self.disp.display_choice_menu("EXIT", "Unsaved changes", choice_list)

        # Default : Cancel
        ret = RetCode.CANCEL
        if choice_idx == 1:
            ret = RetCode.EXIT_SAVE
        elif choice_idx == 2:
            ret = RetCode.EXIT_NO_SAVE

        return ret

    def display_container_info(self) -> None:
        """
        Display container info
        """

        self.raise_no_override("display_container_info")

    def display_container_item_list(self, hl_changed: bool, focus_changed: bool) -> None:
        """
        Display list of items (statements or operations) in container

        Args:
            hl_changed (bool): Is highlighted item updated
            focus_changed (bool): Is focused item updated
        """

        item_list: List[Any] = self.get_container_item_list()

        # Left window
        win = self.disp.win_list[WinId.LEFT]
        win_h: int = win.getmaxyx()[0]

        # Number of displayed items
        item_disp_nb: int = win_h - 4
        if len(item_list) < item_disp_nb:
            item_disp_nb = len(item_list)

        if hl_changed:
            # Highlighted item updated

            # Fix focus

            item_hl_idx = item_list.index(self.item_hl)

            # While highlited item above focus
            while (item_hl_idx < self.item_focus_idx and
                self.item_focus_idx >= 0):

                # Move focus up
                self.item_focus_idx -= 1

            # While highlited item below focus
            while (item_hl_idx > self.item_focus_idx + item_disp_nb - 1 and
                self.item_focus_idx < len(item_list) - item_disp_nb):

                # Move focus down
                self.item_focus_idx += 1

        # Else, if focus updated
        elif focus_changed:

            # Fix focus

            if self.item_focus_idx < 0:
                self.item_focus_idx = 0
            elif self.item_focus_idx > len(item_list) - item_disp_nb:
                self.item_focus_idx = len(item_list) - item_disp_nb

            # Fix highlighted item

            item_hl_idx = item_list.index(self.item_hl)

            if item_hl_idx < self.item_focus_idx:

                # Highlight first displayed item
                item_hl_idx = self.item_focus_idx
                self.item_hl = item_list[item_hl_idx]

            elif item_hl_idx > self.item_focus_idx + item_disp_nb - 1:

                # Highlight last displayed item
                item_hl_idx = self.item_focus_idx + item_disp_nb - 1
                self.item_hl = item_list[item_hl_idx]

        (win_y, win_x) = (0, 0)

        # Item separator
        win.addstr(win_y, win_x, self.item_disp.SEPARATOR)
        win_y += 1

        # Item header
        win.addstr(win_y, win_x, self.item_disp.HEADER)
        win_y += 1

        # TODO merge to common case
        if len(item_list) == 0:
            win.addstr(win_y, win_x, self.item_disp.SEPARATOR)
            win_y += 1
            win.addstr(win_y, win_x, self.item_disp.SEPARATOR)
            win_y += 1
            win.refresh()
            return

        # Item separator or missing
        if self.item_focus_idx == 0:
            win.addstr(win_y, win_x, self.item_disp.SEPARATOR)
        else:
            win.addstr(win_y, win_x, self.item_disp.MISSING)
        win_y += 1

        # Item list
        for item_idx in range(self.item_focus_idx, self.item_focus_idx + item_disp_nb):

            if item_idx >= len(item_list):
                break

            item = item_list[item_idx]

            disp_flag = A_NORMAL
            if item == self.item_hl:
                disp_flag += A_STANDOUT
            if item in self.item_sel_list:
                disp_flag += A_BOLD

            self.item_disp.set_item(item)
            self.item_disp.display_item_line(win, win_y, win_x, disp_flag)
            # self.display_item_line(item, win, win_y, win_x, disp_flag)
            win_y += 1

        # Item separator or missing
        if item_idx == len(item_list) - 1:
            win.addstr(win_y, win_x, self.item_disp.SEPARATOR)
        else:
            win.addstr(win_y, win_x, self.item_disp.MISSING)
        win_y += 1

        if len(item_list) != 0:
            ope_disp_ratio = item_disp_nb / len(item_list)

        # Slider
        (win_y, win_x) = (3, win.getyx()[1])
        for _ in range(0, int(self.item_focus_idx * ope_disp_ratio)):
            win.addstr(win_y, win_x, " ")
            win_y += 1
        for _ in range(int(self.item_focus_idx * ope_disp_ratio),
                       int((self.item_focus_idx + item_disp_nb) * ope_disp_ratio)):
            win.addstr(win_y, win_x, " ", A_STANDOUT)
            win_y += 1
        for _ in range(int((self.item_focus_idx + item_disp_nb) * ope_disp_ratio),
                       int((len(item_list)) * ope_disp_ratio)):
            win.addstr(win_y, win_x, " ")
            win_y += 1

        win.refresh()

    def browse_container(self):
        """
        Browse container
        """

        # Init
        item_list: List[Any] = self.get_container_item_list()
        self.item_focus_idx: int = 0
        self.item_hl = None
        if len(item_list) != 0:
            self.item_hl = item_list[0]
        self.item_sel_list = []

        # Main window
        win = self.disp.win_list[WinId.MAIN]
        win_w = win.getmaxyx()[1]
        win.clear()
        win.border()
        win.addstr(0, int((win_w - len(self.title))/2), f" {self.title} ", A_STANDOUT)
        win.addstr(0, 2, f" {self.subtitle} ", A_BOLD)
        win.keypad(1)
        win.refresh()

        self.display_container_info()
        self.display_container_item_list(False, False)

        while True:

            hl_changed = False
            focus_changed = False

            # key = win.getkey()
            key = win.getch()
            # win.addstr(0, 0, f"\"{key}\"")
            # win.refresh()

            # Highlight previous item
            if key in ["KEY_UP", 259]:
                if self.item_hl is None or self.item_hl not in item_list:
                    continue
                ope_hl_idx = item_list.index(self.item_hl) - 1
                if ope_hl_idx < 0:
                    ope_hl_idx = 0
                    continue
                self.item_hl = item_list[ope_hl_idx]
                hl_changed = True

            # Highlight next item
            elif key in ["KEY_DOWN", 258]:
                if self.item_hl is None or self.item_hl not in item_list:
                    continue
                ope_hl_idx = item_list.index(self.item_hl) + 1
                if ope_hl_idx >= len(item_list):
                    ope_hl_idx = len(item_list) - 1
                    continue
                self.item_hl = item_list[ope_hl_idx]
                hl_changed = True

            # Focus previous item
            elif key in ["KEY_PPAGE", 339]:
                if self.item_hl is None:
                    continue
                self.item_focus_idx -= 3
                focus_changed = True

            # Focus next item
            elif key in ["KEY_NPAGE", 338]:
                if self.item_hl is None:
                    continue
                self.item_focus_idx += 3
                focus_changed = True

            # Trigger item selection
            elif key in [" ", 32]:
                if self.item_hl is None:
                    continue
                if self.item_hl not in self.item_sel_list:
                    self.item_sel_list.append(self.item_hl)
                else:
                    self.item_sel_list.remove(self.item_hl)

            # Copy item(s)
            # ctrl c
            elif key in [-1]:
                self.copy()

            # Cut item(s)
            # ctrl x
            elif key == 24:
                self.cut()
                self.disp.win_list[WinId.LEFT].clear()

            # Paste item(s)
            # ctrl v
            elif key in [22]:
                self.paste()

            # Rappr ope
            # ctrl r
            elif key == 18:
                self.rappr()

            # Edit highlighted item
            # ctrl e
            elif key == 5:
                self.edit_container_item(self.item_hl)
                self.disp.win_list[WinId.LEFT].clear()
                hl_changed = True

            # Open highlighted item
            # enter
            elif key in ["\n", 10]:
                self.browse_container_item(self.item_hl)
                self.disp.win_list[WinId.LEFT].clear()
                hl_changed = True

            # Add new item
            # insert, +
            elif key in ["KEY_IC", "+", 331, 43]:
                item = self.create_container_item()
                if item is not None:
                    self.add_container_item(item)
                self.disp.win_list[WinId.LEFT].clear()

            # Remove item(s)
            # del, -
            elif key in ["KEY_DC", "-", 330, 45]:

                ret = RetCode.CANCEL

                item_list = []
                if len(self.item_sel_list) != 0:
                    item_list = self.item_sel_list
                elif self.item_hl is not None:
                    item_list = [self.item_hl]

                if len(item_list) > 0:

                    self.highlight_closest_item(item_list)

                    ret = self.remove_container_item_list(item_list)
                    if ret == RetCode.OK:
                        self.item_sel_list.clear()

                    self.disp.win_list[WinId.LEFT].clear()

            # Save
            # ctrl s
            elif key == 19:
                self.save()

            # Exit
            # esc, backspace
            elif key in ['\x1b', 27, 8]:
                ret = self.exit()
                if ret == RetCode.OK:
                    self.disp.cont_disp_last = self
                    break

            # signal exit
            # ctrl p
            elif key == 16:
                raise KeyboardInterrupt

            item_list = self.get_container_item_list()

            if self.item_hl is None:
                if len(item_list) != 0:
                    self.item_hl = item_list[0]

            self.display_container_info()
            self.display_container_item_list(hl_changed, focus_changed)
