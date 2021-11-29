"""
a read-only TkTkinter.Text widget
"""
# see: https://stackoverflow.com/a/11612656/1046449

from tkinter import Text
from idlelib.redirector import WidgetRedirector


class TextReadOnly(Text):
    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)
        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register(
            "insert", lambda *args, **kw: "break"
        )
        self.delete = self.redirector.register(
            "delete", lambda *args, **kw: "break"
        )
