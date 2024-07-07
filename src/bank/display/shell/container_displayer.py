
from bank.display.shell.main_displayer import MainDisplayer

class ContainerDisplayer():

    def __init__(self, disp: MainDisplayer) -> None:
        pass

    def show(self):
        pass

    def list(self):
        pass

    def prompt(self):
        return ""

    def browse(self):
        _exit = False
        while not _exit:
            input_str = self.prompt()
            if input_str == "":
                pass
            elif input_str == "echo":
                print("echo")
            elif input_str == "show":
                self.show()
            elif input_str == "list":
                self.list()
            elif input_str == "exit":
                _exit = True
            else:
                print("Unknown command")
