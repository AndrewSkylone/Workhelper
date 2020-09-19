import keyboard, time, tkinter as tk
from extensions_libs import addons
from importlib import reload

import extended_tk as extk
import extensions_libs.snipper.snipper as snipper


class Extensions(extk.Toplevel):
    """ frame with minor features """
    def __init__(self, master, driver, cfg={}, **kw):
        extk.Toplevel.__init__(self, master, cfg, **kw)

        self.driver = driver
        
        self.create_widgets()

    
    def create_widgets(self):
        reload(addons)
        reload(snipper)

        addons_frame = addons.Addons(self, driver=self.driver)
        addons_frame.grid(row=1, column=0)

        buttons_frame = tk.Frame(self)
        buttons_frame.grid(row=0, column=0, padx=5, pady=5, sticky="N")

        snipper_button = tk.Button(buttons_frame, text="snippets", command=lambda: snipper.Snipper_TopLevel(self))
        snipper_button.grid(row=0, column=0)
        

if __name__ == "__main__":
    import workhelper