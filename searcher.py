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


class Searcher_GUI(extk.Toplevel):
    """ Mainframe, add new tags for generating. Inheritance Singleton template """

    def __init__(self, master, _driver, cnf={}, **kw):
        super().__init__(master, cnf, **kw)

        self.title("Searcher")

        global driver
        driver = _driver

        self.searcher = Searcher()
        self.ali_entries = []
        self.ali_labels = []
        self.button_frame = None
        self.generators_frame = None
        self.tags_frame = None

        self.create_widgets()

    def create_widgets(self):
        self.create_buttons()
        self.create_generators()
        self.create_nes_tags_widgets()

    def create_buttons(self):
        self.button_frame = tk.Frame(self)
        self.button_frame.grid(row=0, column=0, sticky="w")

        self.add_button = tk.Button(self.button_frame, text="add tags", command=self.add_tags)
        self.add_button.grid(row=0, column=0)
        hotkeys.append(keyboard.add_hotkey('alt + a', self.add_tags))

        self.search_button = tk.Button(self.button_frame, text="search all", command=self.search_all_tags)
        self.search_button.grid(row=0, column=1)

        self.reset_button = tk.Button(self.button_frame, text="reset search", command=self.reset_search)
        self.reset_button.grid(row=0, column=2)

    def create_generators(self):
        self.generators_frame = tk.Frame(self)
        self.generators_frame.grid(row=1, column=0, sticky="w")

    def create_nes_tags_widgets(self):
        self.tags_frame = tk.Frame(self)
        self.tags_frame.grid(row=2, column=0, sticky="w")

        self.nes_lable = tk.Label(self.tags_frame, text="NES", width=7)
        self.nes_lable.grid(row=0, column=0)

        self.nes_entry = extk.Entry(self.tags_frame, textvariable=tk.StringVar())
        self.nes_entry.grid(row=0, column=1, pady=5, sticky="w"+"e")
        self.nes_entry.bind("<Return>", self.on_tags_entries_changed)

    def destroy(self):
        for hotkey in hotkeys:
            keyboard.remove_hotkey(hotkey)
        hotkeys.clear()

        super().destroy()

    def create_ali_tags_widgets(self, tags=""):
        ali_label = tk.Label(self.tags_frame, text="Ali")
        ali_label.grid(row=len(self.ali_labels) + 3, column=0, pady=2, sticky="w"+"e")
        self.ali_labels.append(ali_label)
        ali_label.bind("<Button-3>", self.destroy_ali_tag_widgets)

        ali_entry = extk.Entry(self.tags_frame, textvariable=tk.StringVar(),
                                width=max(len(tags), TAGS_ENTRIES_WIDTH))
        ali_entry.grid(row=len(self.ali_entries) + 3, column=1, pady=2, sticky="w"+"e")
        ali_entry.textvariable.set(tags)
        ali_entry.bind("<Return>", self.on_tags_entries_changed)
        self.ali_entries.append(ali_entry)

    def add_tags(self):
        """ Create new fields with tags or rewrite tags in empty fields """

        entries = self.ali_entries

        driver.switch_to.window("active")

        if "nesky.hktemas.com" in driver.current_url:
            tags = self.searcher.download_nes_tags()
            self.nes_entry.textvariable.set(tags)
            self.nes_entry.configure(width=max(len(tags), TAGS_ENTRIES_WIDTH))

        elif "aliexpress" in driver.current_url:
            tags = self.searcher.download_ali_tags()
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

    def destroy_ali_tag_widgets(self, event):
        widget = event.widget
        index = self.ali_labels.index(widget)

        self.ali_labels[index].destroy()
        self.ali_labels.remove(self.ali_labels[index])
        self.ali_entries[index].destroy()
        self.ali_entries.remove(self.ali_entries[index])

        self.on_tags_entries_changed()

    def reset_search(self):
        self.generators_frame.destroy()
        self.tags_frame.destroy()
        self.ali_entries.clear()
        self.ali_labels.clear()

        self.create_generators()
        self.create_nes_tags_widgets()
        self.searcher = Searcher()

    def search_all_tags(self):
        pass

    def on_tags_entries_changed(self, event=None):
        print("entries changed")

class Searcher(object):
     
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

    def __init__(self, master, generator, cfg={}, **kw):
        tk.LabelFrame.__init__(self, master, cfg, **kw)

        self.generator = generator

        self.create_widgets()

    def create_widgets(self):
        # searhing tags
        self.search_lable = tk.Label(self, text="0")
        self.search_lable.grid(row=1, column=0, pady=5)

        self.search_entry = extk.Entry(self, textvariable=tk.StringVar(), width=TAGS_ENTRIES_WIDTH)
        self.search_entry.grid(row=1, column=1)
        self.search_entry.textvariable.trace("w", self.update_tags_size)

    def update_tags_size(self):
        pass

    def generate_tags(self):
        pass


class Generator(object):
    """ Generator bisiness-logical. Implement abstract factory template. """

    def __init__(self):
        pass

    def search_tags(self):
        request = self.search_entry.textvariable.get().replace(" ", "-")
        driver.execute_script(
            "open('https://aliexpress.com/af/%s.html')" % request)

    def generate_tags(self, *args):
        entries = self.ali_entries
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
