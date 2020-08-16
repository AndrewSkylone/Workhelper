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

import extended_tk, calculator, suplier, statistics, extensions as ext #user libs
  
class Workhelper(tk.Tk):
    """ Main program frame """

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

        create_calculator_button = tk.Button(buttons_frame, text="price calculator", width=16, command=self.create_calculator_frame)
        create_calculator_button.grid(row=0, column=0, columnspan=2, sticky="w"+"e")

        create_suplier_button = tk.Button(buttons_frame, text="suplier", command=self.create_suplier_frame)
        create_suplier_button.grid(row=1, column=0, sticky="w"+"e")

        create_statistics_button = tk.Button(buttons_frame, text="statistics", command=self.create_statistics_frame)
        create_statistics_button.grid(row=2, column=0, sticky="w"+"e")

        tk.Label(buttons_frame).grid(row=3, column=0, sticky="w"+"e") #empty space
        button_extension = tk.Button(buttons_frame, text="extensions", command=self.create_extensions_frame)
        button_extension.grid(row=4, column=0, sticky="w"+"e")        

    def create_calculator_frame(self):    
        calculator.Calculator(driver=driver)

    def create_suplier_frame(self):
        suplier.Suplier(driver=driver)

    def create_statistics_frame(self):
        statistics.Statistics(driver=driver)         

    def create_extensions_frame(self):
        reload(ext) #delete after debelopment!            
        ext.Extensions(driver=driver)

    def on_closing(self):
        driver.quit()
        self.destroy()

def create_profile_chrome_driver() -> webdriver:
    """ Create chrome webdriver with default user profile """
    
    os.chdir(sys.path[0])
    executable_path = os.path.join("chromedriver","chromedriver.exe")

    chrome_options = Options()
    chrome_options.add_argument(r"user-data-dir=C:\Users\andre\AppData\Local\Google\Chrome\User Data")
    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "none"

    return webdriver.Chrome(desired_capabilities=caps, executable_path=executable_path, options=chrome_options)


if __name__ == "__main__":
    driver = create_profile_chrome_driver()
    driver.get("https://nesky.hktemas.com/order-margins")
    frame = Workhelper()

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%I:%M:%S') 
    #disable logging from another libs
    for key in logging.Logger.manager.loggerDict:
        logging.getLogger(key).setLevel(logging.CRITICAL)

    frame.mainloop()