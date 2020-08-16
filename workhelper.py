import os, logging, keyboard, sys, pyperclip, time, threading
from importlib import reload
import tkinter as tk
from tkinter.messagebox import showerror

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import *

import extended_tk, calculator, suplier, extensions as ext #user libs
  
class Workhelper(tk.Tk):
    """ Main window frame """

    def __init__(self, master=None, **options):
        tk.Tk.__init__(self, master, **options)

        self.resizable(False, False)
        self.title("WorkHelper")
        self.geometry("+%d+%d" % (100, 700))
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.driver = self.create_profile_chrome_driver()

        self.create_widgets()

    def create_widgets(self) -> None:
        """ Create widget buttons """

        buttons_frame = tk.Frame()
        buttons_frame.grid()

        button_open = tk.Button(buttons_frame, text="open links", width=16, command=self.open_links)
        button_open.grid(row=0, column=0, columnspan=2, sticky="w"+"e")

        button_calculation = tk.Button(buttons_frame, text="calculation", command=self.calculation)
        button_calculation.grid(row=1, column=0, columnspan=2, sticky="w"+"e")

        button_save = tk.Button(buttons_frame, text="save", command=self.save_suplier)
        button_save.grid(row=2, column=0, sticky="w"+"e")

        button_paste = tk.Button(buttons_frame, text="paste", command=self.paste_suplier)
        button_paste.grid(row=2, column=1, sticky="w"+"e")

        button_clear = tk.Button(buttons_frame, text="clear frames", command=self.clear_frames)
        button_clear.grid(row=3, column=0, columnspan=2, sticky="w"+"e")

        tk.Label(buttons_frame).grid(row=4, column=0, columnspan=2, sticky="w"+"e") #empty space
        button_extension = tk.Button(buttons_frame, text="extensions", command=self.extensions)
        button_extension.grid(row=5, column=0, columnspan=2, sticky="w"+"e")        

    def open_links(self):
        driver.switch_to.window("active")

        for element in driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']"):
            driver.execute_script("arguments[0].click()", element)
        for element in driver.find_elements(By.CSS_SELECTOR, "a[target='_blank']"):
            element.send_keys(Keys.CONTROL, Keys.ENTER)

        driver.switch_to.window(driver.window_handles[1])


    def calculation(self, hotkey=False):    
        if frames.get("calculation") and hotkey:
            frames["calculation"].destroy()
            del(frames["calculation"])
            driver.switch_to.window("active")
            frames["calculation"] = calculator.Calculator(frame, driver=driver, padx=5)
            frames["calculation"].grid(row=0, column=3, rowspan=15, sticky="n"+"s")

        elif frames.get("calculation") and not hotkey:
            frames["calculation"].destroy()
            del(frames["calculation"])

        else:
            driver.switch_to.window("active")
            frames["calculation"] = calculator.Calculator(frame, driver=driver, padx=5)
            frames["calculation"].grid(row=0, column=3, rowspan=15, sticky="n"+"s") 

    def save_suplier(self, hotkey=False):
        if frames.get("suplier") and hotkey:
            frames["suplier"].destroy()
            del(frames["suplier"])        
            driver.switch_to.window("active")
            frames["suplier"] = suplier.Suplier(frame, driver=driver, padx=5)
            frames["suplier"].grid(row=0, column=2, rowspan=15, sticky="n"+"s")
        
        elif frames.get("suplier") and not hotkey:
            frames["suplier"].destroy()
            del(frames["suplier"])
        
        else:
            driver.switch_to.window("active")
            frames["suplier"] = suplier.Suplier(frame, driver=driver, padx=5)
            frames["suplier"].grid(row=0, column=2, rowspan=15, sticky="n"+"s")

    def paste_suplier(self):
        driver.switch_to.window("active")

        if not frames.get("suplier"): return
        frames["suplier"].paste()

    def clear_frames(self):
        for frame in frames:
            frames[frame].destroy()
        frames.clear()
            

    def extensions(self, hotkey=False):
        reload(ext) #delete after debelopment!
            
        if frames.get("extensions"):
            frames["extensions"].destroy()
            del(frames["extensions"])
        else:
            frames["extensions"] = ext.Extensions(frame, driver=driver, padx=5)
            frames["extensions"].grid(row=0, column=1, rowspan=15, sticky="n"+"s")


    def on_closing(self):
        driver.quit()
        frame.destroy()

    def create_profile_chrome_driver(self) -> webdriver:
        """ Create chrome webdriver with default user profile """
        
        os.chdir(sys.path[0])
        executable_path = os.path.join("chromedriver","chromedriver.exe")

        chrome_options = Options()
        chrome_options.add_argument(r"user-data-dir=C:\Users\andre\AppData\Local\Google\Chrome\User Data")
        caps = DesiredCapabilities().CHROME
        caps["pageLoadStrategy"] = "none"

        return webdriver.Chrome(desired_capabilities=caps, executable_path=executable_path, options=chrome_options)


if __name__ == "__main__":
    workhelper = workhelper()
    workhelper.driver.get("https://nesky.hktemas.com/order-margins")

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%I:%M:%S') 
    #disable logging from another libs
    for key in logging.Logger.manager.loggerDict:
        logging.getLogger(key).setLevel(logging.CRITICAL)

    workhelper.mainloop()