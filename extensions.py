import keyboard, time, tkinter as tk
from extensions_libs import addons
from importlib import reload


class Extensions(tk.Toplevel):
    """ frame with minor features """

    def __init__(self, master, driver, cfg={}, **kw):
        kw["text"] = "Extensions"
        tk.Toplevel.__init__(self, master, cfg, **kw)

        self.driver = driver
        
        self.create_widgets()

    
    def create_widgets(self):
        reload(addons)
        reload(stats)

        buttons_frame = tk.Frame(self)
        buttons_frame.grid(row=0, column=0, padx=5, sticky="N")

        addons_frame = addons.Addons(buttons_frame, driver=self.driver)
        addons_frame.grid(row=0, column=0)
    
    def create_extension_frame(self, extension):
        if self.extension:
            self.extension.destroy()
            self.update()
   
        self.extension = extension
        extension.grid(row=0, column=1)

if __name__ == "__main__":
    import workhelper