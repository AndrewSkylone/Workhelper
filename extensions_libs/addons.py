import keyboard, pyperclip, re, tkinter as tk
import webbrowser
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


class Addons(tk.LabelFrame):
    """ Have little features for simple working """

    def __init__(self, master, driver, cfg={}, **kw):
        kw["text"] = "addons"
        tk.LabelFrame.__init__(self, master, cfg, **kw)

        self.driver = driver
        self.hotkeys = []
        
        self.create_widgets()

    
    def create_widgets(self):
        self.open_copied_links_button = tk.Button(self, text="open copied links", command=self.open_copied_links)
        self.open_copied_links_button.grid(row=0, column=0, sticky="w")

        self.open_margin_links_button = tk.Button(self, text="open margin links", command=self.open_margin_links)
        self.open_margin_links_button.grid(row=0, column=1, sticky="w")

        self.hotkeys.append(keyboard.add_hotkey('ctrl + alt + q', self.open_copied_links))
    
    def open_copied_links(self):
        links = re.findall('https://nesky.hktemas.com\S*', pyperclip.paste())
        for link in links:
            webbrowser.open_new_tab(link)
    
    def open_margin_links(self):
        for element in self.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']"):
            self.driver.execute_script("arguments[0].click()", element)
        for element in self.driver.find_elements(By.CSS_SELECTOR, "a[target='_blank']"):
            element.send_keys(Keys.CONTROL, Keys.ENTER)

        self.driver.switch_to.window(self.driver.window_handles[1])