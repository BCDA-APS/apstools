
"""
a read-only TkTkinter.Text widget
"""
# see: https://stackoverflow.com/questions/21873195/readonly-tkinter-text-widget/21882093#21882093

from tkinter import *

# This is the list of all default command in the "Text" tag that modify the text
commandsToRemove = (
    "<Control-Key-h>",
    "<Meta-Key-Delete>",
    "<Meta-Key-BackSpace>",
    "<Meta-Key-d>",
    "<Meta-Key-b>",
    "<<Redo>>",
    "<<Undo>>",
    "<Control-Key-t>",
    "<Control-Key-o>",
    "<Control-Key-k>",
    "<Control-Key-d>",
    "<Key>",
    "<Key-Insert>",
    "<<PasteSelection>>",
    "<<Clear>>",
    "<<Paste>>",
    "<<Cut>>",
    "<Key-BackSpace>",
    "<Key-Delete>",
    "<Key-Return>",
    "<Control-Key-i>",
    "<Key-Tab>",
    "<Shift-Key-Tab>"
)


class TextReadOnly(Text):
    """
    a read-only variant of the TkTkinter.Text widget
    """

    tagInit = False

    def init_tag(self):
        """
        Just go through all binding for the Text widget.
        If the command is allowed, recopy it in the TextReadOnly binding table.
        """
        for key in self.bind_class("Text"):
            if key not in commandsToRemove:
                command = self.bind_class("Text", key)
                self.bind_class("TextReadOnly", key, command)
        TextReadOnly.tagInit = True


    def __init__(self, *args, **kwords):
        Text.__init__(self, *args, **kwords)
        if not TextReadOnly.tagInit:
            self.init_tag()

        # Create a new binding table list, replace the default Text binding table by the TextReadOnly one
        bindTags = tuple(tag if tag!="Text" else "TextReadOnly" for tag in self.bindtags())
        self.bindtags(bindTags)
