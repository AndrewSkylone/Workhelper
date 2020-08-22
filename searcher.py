import copy
import re
import keyboard
import tkinter as tk
from tkinter import ttk
from importlib import reload

from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from googletrans import Translator

import extended_tk as extk  # user modules
reload(extk)


driver = None
hotkeys = []
TAGS_ENTRIES_WIDTH = 50


class Searcher(extk.Toplevel):
    """ Mainframe, add new tags for generating. Inheritance Singleton template """

    def __init__(self, master, _driver, cnf={}, **kw):
        super().__init__(master, cnf, **kw)

        self.title("Searcher")

        global driver
        driver = _driver

        self.service = Searcher_service()
        self.entries = []
        self.labels = []

        self.create_widgets()

    def create_widgets(self):
        # buton panel
        self.button_frame = tk.Frame(self)
        self.button_frame.grid(row=0, column=0, sticky="w")

        self.add_button = tk.Button(self.button_frame, text="add tags", command=self.add_tags)
        self.add_button.grid(row=0, column=0)
        hotkeys.append(keyboard.add_hotkey('alt + a', self.add_tags))

        self.search_button = tk.Button(self.button_frame, text="search all", command=self.search_all_tags)
        self.search_button.grid(row=0, column=1)

        self.reset_button = tk.Button(self.button_frame, text="reset search", command=self.reset_search)
        self.reset_button.grid(row=0, column=2)

        # nes tags
        self.tags_frame = tk.Frame(self)
        self.tags_frame.grid(row=1, column=0, sticky="w")

        self.nes_lable = tk.Label(self.tags_frame, text="NES", width=7)
        self.nes_lable.grid(row=0, column=0)

        self.nes_entry = extk.Entry(self.tags_frame, textvariable=tk.StringVar())
        self.nes_entry.grid(row=0, column=1, pady=5, sticky="w"+"e")

    def destroy(self):
        for hotkey in hotkeys:
            keyboard.remove_hotkey(hotkey)
        hotkeys.clear()

        super().destroy()

    def add_tags(self):
        """ Create new fields with tags or rewrite tags in empty fields """

        entries = self.entries

        driver.switch_to.window("active")

        if "nesky.hktemas.com" in driver.current_url:
            tags = self.service.download_nes_tags()
            self.nes_entry.textvariable.set(tags)
            self.nes_entry.configure(width=max(len(tags), TAGS_ENTRIES_WIDTH))

        elif "aliexpress" in driver.current_url:
            tags = self.service.download_ali_tags()
            if all(entry.get() for entry in entries):
                self.create_ali_tags_widgets(tags=tags)
            else:
                for entry in entries:
                    if not entry.get():
                        entry.textvariable.set(tags)
                        break
        else:
            tk.messagebox.showerror("404", "No tags found")
            return

        self.on_tags_entries_changed()

    def create_ali_tags_widgets(self, tags=""):
        ali_label = tk.Label(self.tags_frame, text="Ali")
        ali_label.grid(row=len(self.labels) + 3, column=0, pady=2, sticky="w"+"e")
        self.labels.append(ali_label)
        ali_label.bind("<Button-3>", self.destroy_ali_tags_widgets)

        ali_entry = extk.Entry(self.tags_frame, textvariable=tk.StringVar())
        ali_entry.grid(row=len(self.entries) + 3, column=1, pady=2, sticky="w"+"e")
        ali_entry.textvariable.set(tags)
        ali_entry.textvariable.trace("w", self.on_tags_entries_changed)
        self.entries.append(ali_entry)

    def destroy_ali_tags_widgets(self, event):
        widget = event.widget
        index = self.labels.index(widget)

        self.labels[index].destroy()
        self.labels.remove(self.labels[index])
        self.entries[index].destroy()
        self.entries.remove(self.entries[index])

        self.on_tags_entries_changed()

    def reset_search(self):
        pass

    def search_all_tags(self):
        pass

    def on_tags_entries_changed(self):
        pass

class Searcher_service(object):
     
    def download_nes_tags(self) -> "string":
        try:
            tags_element = driver.find_element(By.CSS_SELECTOR, "div.titles>span")
        except NoSuchElementException:
            return ""
        else:
            return tags_element.text

    def download_ali_tags(self) -> "string":
        try:
            tags_element = driver.find_element(By.CLASS_NAME, "product-title-text")
        except NoSuchElementException:
            return ""
        else:
            result = re.search('"language":"(\w*)","locale"', driver.page_source)
            language = result.group(1)
            return Translator().translate(tags_element.text, src=language).text

class Generator_GUI(tk.LabelFrame):
    """ Abstract factory frame for different frames generators """

    def __init__(self, master, cfg={}, **kw):
        tk.LabelFrame.__init__(self, master, cfg, **kw)

        self.service = Generator_service()

        self.create_widgets()

    def create_widgets(self):
        # searhing tags
        self.search_lable = tk.Label(self, text="0")
        self.search_lable.grid(row=1, column=0, pady=5)

        self.search_entry = extk.Entry(
            self, textvariable=tk.StringVar(), width=TAGS_ENTRIES_WIDTH)
        self.search_entry.grid(row=1, column=1)
        self.search_entry.textvariable.trace("w", self.update_tags_size)

    def update_tags_size(self):
        pass

    def generate_tags(self):
        pass


class Generator_service(object):
    """ Generator bisiness-logical. Implement abstract factory template. """

    def __init__(self):
        pass

    def search_tags(self):
        request = self.search_entry.textvariable.get().replace(" ", "-")
        driver.execute_script(
            "open('https://aliexpress.com/af/%s.html')" % request)

    def generate_tags(self, *args):
        entries = self.entries
        nes_entry = self.nes_entry

        nes_tags = nes_entry.textvariable.get().split()
        tags = set(tag.lower() for tag in nes_tags)

        for entry in entries:
            ali_tags = set(tag.lower() for tag in entry.get().split())
            tags = tags & ali_tags

        self.search_entry.textvariable.set(" ".join(tags))
        self.update_tags_size()

    def update_tags_size(self, *args):
        self.search_lable["text"] = len(self.search_entry.get())


if __name__ == "__main__":
    import workhelper
