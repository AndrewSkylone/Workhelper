import copy, re, keyboard, tkinter as tk
from tkinter import ttk
from importlib import reload

from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from googletrans import Translator

import extended_tk as extk #user modules
reload(extk)


TAGS_ENTRIES_WIDTH = 50


class Searcher(extk.Toplevel):
    def __init__(self, master, driver, cfg={}, **kw):
        extk.Toplevel.__init__(self, master, cfg, **kw)
        self.title("Searcher")

        self.driver = driver
        self.entries = []
        self.labels = []

        self.driver = driver
        self.entries = [] # [extkEntry()]
        self.labels = [] # [tk.Labels()]
        self.hotkeys = []

        self.create_widgets()
        self.add_tags()
    
    def create_widgets(self):
        # button panel
        self.button_frame = tk.Frame(self)
        self.button_frame.grid(row=0, column=0, sticky="w")

        self.add_button = tk.Button(self.button_frame, text="add tags", command=self.add_tags)
        self.add_button.grid(row=0, column=0)
        self.hotkeys.append(keyboard.add_hotkey('alt + a', self.add_tags))

        self.search_button = tk.Button(self.button_frame, text="search tags", command=self.search_tags)
        self.search_button.grid(row=0, column=1)

        self.clear_button = tk.Button(self.button_frame, text="clear frame", command=self.destroy)
        self.clear_button.grid(row=0, column=2)

        # searhing tags 
        self.search_lable = tk.Label(self, text="0")
        self.search_lable.grid(row=1, column=0, pady=5)

        self.search_entry = extk.Entry(self, textvariable=tk.StringVar())
        self.search_entry = extk.Entry(self, textvariable=tk.StringVar(), width=TAGS_ENTRIES_WIDTH)
        self.search_entry.grid(row=1, column=1)
        self.search_entry.textvariable.trace("w", self.update_tags_size)

        # nes tags
        self.nes_lable = tk.Label(self, text="NES")
        self.nes_lable.grid(row=2, column=0)

        self.nes_entry = extk.Entry(self, textvariable=tk.StringVar())
        self.nes_entry.grid(row=2, column=1, pady=5, sticky="w"+"e")
        self.nes_entry.textvariable.trace("w", self.generate_tags)


    def add_tags(self):
        driver = self.driver
        entries = self.entries

        driver.switch_to.window("active")

        if "nesky.hktemas.com" in driver.current_url:
            try:
                tags_element = driver.find_element(By.CSS_SELECTOR, "div.titles>span")
            except NoSuchElementException:
                tk.messagebox.showerror("404", "No title found")
            else:
                self.nes_entry.textvariable.set(tags_element.text)

        elif "aliexpress" in driver.current_url:
            tags_element = driver.find_element(By.CLASS_NAME, "product-title-text")
            language = re.compile('"language":"(\w*)","locale"').findall(driver.page_source)[0]
            text = Translator().translate(tags_element.text, src=language).text
            # insert in empty tag or create new fields
            if all(entry.get() for entry in entries):
                self.create_ali_tags(tags=text)
            else:
                for entry in entries: 
                    if not entry.get():
                        entry.textvariable.set(text)
                        break                
        else:
            tk.messagebox.showerror("404", "No title found")
            return      
        self.generate_tags()
    
    def search_tags(self):
        driver = self.driver
        request = self.search_entry.textvariable.get().replace(" ", "-")
        driver.execute_script("open('https://aliexpress.com/af/%s.html')" % request)
    
    def generate_tags(self, *args):
        entries = self.entries
        nes_entry = self.nes_entry

        nes_tags = nes_entry.textvariable.get().split()
        tags = set(tag.lower() for tag in nes_tags)

        for entry in entries:
            ali_tags = set(tag.lower() for tag in entry.get().split())
            # tags = tags or ali_tags & ali_tags or tags
            tags = tags & ali_tags 

        
        self.search_entry.textvariable.set(" ".join(tags))
        self.update_tags_size()

    def update_tags_size(self, *args):
        self.search_lable["text"] = len(self.search_entry.get())

    def create_ali_tags(self, **args):
        ali_label = tk.Label(self, text="Ali")
        ali_label.grid(row=len(self.labels) + 3, column=0, pady=2, sticky="w"+"e")
        self.labels.append(ali_label)
        ali_label.bind("<Button-3>", self.delete_ali_tags)
        ali_label.bind("<Button-1>", self.translate_tags)

        ali_entry = extk.Entry(self, textvariable=tk.StringVar())
        ali_entry.grid(row=len(self.entries) + 3, column=1, pady=2, sticky="w"+"e")
        ali_entry.textvariable.set(args["tags"])
        ali_entry.textvariable.trace("w", self.generate_tags)
        self.entries.append(ali_entry)

    def delete_ali_tags(self, event):
        widget = event.widget
        index = self.labels.index(widget)

        self.labels[index].destroy()
        self.labels.remove(self.labels[index])
        self.entries[index].destroy()
        self.entries.remove(self.entries[index])

        self.generate_tags()

    def translate_tags(self, event):
        label = event.widget
        index = self.labels.index(label)
        translated_tags = Translator().translate(self.entries[index].textvariable.get()).text
        self.entries[index].textvariable.set(translated_tags)

    def destroy(self):
        for hotkey in self.hotkeys:
            keyboard.remove_hotkey(hotkey)
            self.hotkeys.remove(hotkey)
        tk.LabelFrame.destroy(self)


if __name__ == "__main__":
    import workhelper