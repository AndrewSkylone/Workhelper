import keyboard, pyperclip, re, tkinter as tk
import webbrowser

class Addons(tk.LabelFrame):
    def __init__(self, master, driver, cfg={}, **kw):
        kw["text"] = "addons"
        tk.LabelFrame.__init__(self, master, cfg, **kw)

        self.driver = driver
        self.hotkeys = []
        
        self.create_widgets()

    
    def create_widgets(self):
        self.open_links_button = tk.Button(self, text="open links", command=self.open_links)
        self.open_links_button.grid(row=0, column=0, sticky="w")
        self.hotkeys.append(keyboard.add_hotkey('ctrl + alt + q', self.open_links))
    
    def open_links(self):
        links = re.findall('https://nesky.hktemas.com\S*', pyperclip.paste())
        for link in links:
            webbrowser.open_new_tab(link)