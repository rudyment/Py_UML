config_extension_def = """
[IDLE2HTML]
enable=1

[IDLE2HTML_cfgBindings]
umlcreate= <Control-Key-y>

"""
import umlGenerator as generator
import tkinter as tk
import importlib
from tkinter import END


class DrawUML:
    """ Třída extenze IDLE pro UML diagramy
    """
    menudefs = [('edit', [('Generate UML', '<<umlcreate>>')])]

    def __init__(self, editwin):
        importlib.reload(tk)
        self.editwin = editwin
        self.nodes = []
        self.canvas = ""
        self.window = ""

    def umlcreate_event(self, event):
        """ Metoda vyvolána virtuální událostí z IDLE.
        Vytvoří okno
        """
        # Zjistíme jestli v okně IDLE je nějaký kód
        if self.editwin.text is not None:
            text = self.editwin.text
            try:
                code_text = text.get('1.0', text.index(END))
            except:
                code_text = ""
        generator.run(code_text)

