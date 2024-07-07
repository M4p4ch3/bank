"""
display/shell/container
"""

from typing import (Any, List)

from bank.display.shell.main import (KeyId, WinId, DisplayerMain)
from bank.display.shell.item_display import DisplayerItem

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

    def get_container_name(self) -> str:
        """Get container name"""
        return ""

    def get_container_item_list(self) -> List[Any]:
        """Get container item list"""
        return []

    def edit_container_item(self, item: Any) -> bool:
        """Edit container item"""
        _ = item
        return False

    def browse_container_item(self, item: Any) -> None:
        """Browse container item"""
        _ = item

    def create_container_item(self) -> Any:
        """Create container item"""
        return Any

    def add_container_item(self, item: Any) -> None:
        """Add container item"""
        _ = item

    def add_container_item_list(self, item_list: List[Any]) -> None:
        """Add container item list"""
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
        """Remove cotnainer item"""
        _ = item

    def highlight_item(self, delta: int) -> None:
        """Highlight item from offset to current"""

        item_list = self.get_container_item_list()

        if self.item_hl is None or len(item_list) == 0 or self.item_hl not in item_list:
            return

        item_hl_idx = item_list.index(self.item_hl) + delta
        if item_hl_idx < 0 or item_hl_idx >= len(item_list):
            return

        self.item_hl = item_list[item_hl_idx]

    def highlight_closest_item(self, item_list: List) -> None:
        """Highlight closest item from list"""

        item_hl_idx = 0
        container_item_list = self.get_container_item_list()
        if self.item_hl in container_item_list:
            item_hl_idx = container_item_list.index(self.item_hl)

        while item_hl_idx >= 0 and self.item_hl in item_list:
            # Highligh previous item
            item_hl_idx -= 1
            if item_hl_idx >= 0:
                self.item_hl = container_item_list[item_hl_idx]

        while item_hl_idx < len(container_item_list) and self.item_hl in item_list:
            # Highligh next item
            item_hl_idx += 1
            if item_hl_idx < len(container_item_list):
                self.item_hl = container_item_list[item_hl_idx]

        if self.item_hl in item_list:
            self.item_hl = None

    def toogle_item_sel(self) -> None:
        """Toogle selection of highlighted item"""

        if self.item_hl is None:
            return

        if self.item_hl not in self.item_sel_list:
            self.item_sel_list.append(self.item_hl)
        else:
            self.item_sel_list.remove(self.item_hl)

    def select_all(self) -> None:
        """Select all items"""
        self.item_sel_list.clear()
        item_list = self.get_container_item_list()
        for item in item_list:
            self.item_sel_list.append(item)

    def copy(self) -> None:
        """Copy selected or highlited item(s)"""

        if len(self.item_sel_list) > 0:
            item_list = self.item_sel_list
        elif self.item_hl is not None:
            item_list = [self.item_hl]
        else:
            return

        self.disp.item_list_clipboard.set(item_list)

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

        if self.item_hl in item_list:
            self.highlight_closest_item(item_list)

        self.remove_container_item_list(item_list, force=True)

        self.item_sel_list.clear()

    def paste(self) -> None:
        """
        Paste item(s)
        """

        item_list = self.disp.item_list_clipboard.get()
        if item_list is None or len(item_list) == 0:
            return

        self.add_container_item_list(item_list)

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

            self.highlight_closest_item(item_list)

            self.remove_container_item_list(item_list, force=True)

            self.item_sel_list.clear()

    def remove_item(self) -> None:
        """Remove highlighted or selected item"""

        if len(self.item_sel_list) != 0:
            item_list = self.item_sel_list
        elif self.item_hl is not None:
            item_list = [self.item_hl]
        else:
            return

        self.highlight_closest_item(item_list)

        ret = self.remove_container_item_list(item_list)
        if ret == RetCode.OK:
            self.item_sel_list.clear()

    def save(self) -> None:
        """Save"""

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
        """Display container info"""

    def display_container_item_list(self, hl_changed: bool, focus_changed: bool) -> None:
        """
        Display list of items (statements or operations) in container

        Args:
            hl_changed (bool): Is highlighted item updated
            focus_changed (bool): Is focused item updated
        """

        item_list: List[Any] = self.get_container_item_list()

        win_left = self.disp.win_list[WinId.LEFT]
        win_left_h: int = win_left.getmaxyx()[0]

        # Number of displayed items
        item_disp_nb: int = win_left_h - 5
        if len(item_list) < item_disp_nb:
            item_disp_nb = len(item_list)

        if self.item_hl is None or self.item_hl not in item_list:
            if len(item_list) != 0:
                self.item_hl = item_list[0]

        if self.item_hl and self.item_hl in item_list:

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
        win_left.addstr(win_y, win_x, self.item_disp.SEPARATOR)
        win_y += 1

        # Item header
        win_left.addstr(win_y, win_x, self.item_disp.HEADER)
        win_y += 1

        # Item separator or missing
        if self.item_focus_idx == 0:
            win_left.addstr(win_y, win_x, self.item_disp.SEPARATOR)
        else:
            win_left.addstr(win_y, win_x, self.item_disp.MISSING)
        win_y += 1

        # Item list
        item_idx = 0
        for item_idx in range(self.item_focus_idx, self.item_focus_idx + item_disp_nb):

            if item_idx >= len(item_list):
                break

            item = item_list[item_idx]

            disp_flag = A_NORMAL
            if self.item_hl and item == self.item_hl:
                disp_flag += A_STANDOUT
            if item in self.item_sel_list:
                disp_flag += A_BOLD

            self.item_disp.set_item(item)
            self.item_disp.display_item_line(win_left, win_y, win_x, disp_flag)
            # self.display_item_line(item, win_left, win_y, win_x, disp_flag)
            win_y += 1

        # Item separator or missing
        if item_idx == 0 or item_idx == len(item_list) - 1:
            win_left.addstr(win_y, win_x, self.item_disp.SEPARATOR)
        else:
            win_left.addstr(win_y, win_x, self.item_disp.MISSING)
        win_y += 1

        ope_disp_ratio = 0
        if len(item_list) != 0:
            ope_disp_ratio = item_disp_nb / len(item_list)

        # Slider
        (win_y, win_x) = (3, win_left.getyx()[1])
        for _ in range(0, int(self.item_focus_idx * ope_disp_ratio)):
            win_left.addstr(win_y, win_x, " ")
            win_y += 1
        for _ in range(int(self.item_focus_idx * ope_disp_ratio),
                       int((self.item_focus_idx + item_disp_nb) * ope_disp_ratio)):
            win_left.addstr(win_y, win_x, " ", A_STANDOUT)
            win_y += 1
        for _ in range(int((self.item_focus_idx + item_disp_nb) * ope_disp_ratio),
                       int((len(item_list)) * ope_disp_ratio)):
            win_left.addstr(win_y, win_x, " ")
            win_y += 1

        win_left.refresh()

    def draw_win_main(self):
        """Draw main window"""
        win_main = self.disp.win_list[WinId.MAIN]
        win_main_w = win_main.getmaxyx()[1]
        win_main.clear()
        win_main.border()
        win_main.addstr(0, int((win_main_w - len(self.title))/2), f" {self.title} ", A_STANDOUT)
        win_main.addstr(0, 2, f" {self.subtitle} ", A_BOLD)
        win_main.keypad(1)
        win_main.refresh()

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

        self.draw_win_main()
        self.display_container_info()
        self.display_container_item_list(False, False)

        win_main = self.disp.win_list[WinId.MAIN]

        while True:

            hl_changed = False
            focus_changed = False

            key = win_main.getch()
            # self.disp.add_log(str(key))

            if key in [KeyId.UP]:
                self.highlight_item(-1)
                hl_changed = True

            elif key in [KeyId.DOWN]:
                self.highlight_item(1)
                hl_changed = True

            elif key in [KeyId.PAGE_UP]:
                self.item_focus_idx -= 3
                focus_changed = True

            elif key in [KeyId.PAGE_DOWN]:
                self.item_focus_idx += 3
                focus_changed = True

            elif key in [KeyId.SPACE]:
                self.toogle_item_sel()

            elif key in [KeyId.CTRL_A]:
                self.select_all()

            elif key in [KeyId.CTRL_C]:
                self.copy()

            elif key in [KeyId.CTRL_X]:
                self.cut()
                self.disp.win_list[WinId.LEFT].clear()

            elif key in [KeyId.CTRL_V]:
                self.paste()

            elif key in [KeyId.CTRL_R]:
                self.rappr()
                self.disp.win_list[WinId.LEFT].clear()

            elif key in [KeyId.CTRL_E]:
                # Edit highlighted item
                self.edit_container_item(self.item_hl)
                self.disp.win_list[WinId.LEFT].clear()
                hl_changed = True

            elif key in [KeyId.ENTER]:
                # Open highlighted item
                self.browse_container_item(self.item_hl)
                self.disp.win_list[WinId.LEFT].clear()
                hl_changed = True
                self.draw_win_main()

            elif key in [KeyId.INS, KeyId.PLUS]:
                # Add new item
                item = self.create_container_item()
                if item is not None:
                    self.add_container_item(item)
                    self.disp.win_list[WinId.LEFT].clear()

            elif key in [KeyId.DEL, KeyId.MINUS]:
                self.remove_item()
                self.disp.win_list[WinId.LEFT].clear()

            elif key in [KeyId.CTRL_S]:
                self.save()

            elif key in [KeyId.ESC, KeyId.BACKSPACE]:
                ret = self.exit()
                if ret == RetCode.OK:
                    self.disp.cont_disp_last = self
                    break

            elif key in [KeyId.CTRL_P]:
                raise KeyboardInterrupt

            # else:
            #     debug_key_str = f"key = {key} ({int(key)})"
            #     print(debug_key_str)
            #     win_main.addstr(0, 0, debug_key_str)

            # item_list = self.get_container_item_list()

            # if self.item_hl is None:
            #     if len(item_list) != 0:
            #         self.item_hl = item_list[0]

            self.display_container_info()
            self.display_container_item_list(hl_changed, focus_changed)
