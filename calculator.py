import copy, re, json, pyperclip, logging, tkinter as tk

from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

import configuration
import extended_tk as extk


config = configuration.__dict__["calculator"]

class Calculator(tk.Toplevel):
    def __init__(self, master, driver, cfg={}, **kw):
        kw["text"] = "calculation"
        tk.Toplevel.__init__(self, master, cfg, **kw)
        
        self.driver = driver
        self.buttons = {} 
        self.entries = {} 
        self.options_readonly = {}
        self.options_entry = {} 

        self.create_widgets()
    # main functions    
    def create_widgets(self):
        buttons = self.buttons
        entries = self.entries 
        driver = self.driver
        html = driver.page_source
        # price label
        entries["product price label"] = extk.Entry(self, state="readonly", textvariable=tk.StringVar(), width=5, bd=0, justify="left")
        entries["product price label"].textvariable.set("price: ")
        entries["product price label"].grid(row=0, sticky="w"+"e")
        # price entry
        entries["product price"] = extk.Entry(self, textvariable=tk.StringVar(), width=6, justify="center")
        entries["product price"].grid(row=0, column=1, sticky="w"+"e")
        entries["product price"].bind("<Return>", self.total_copy)
        try:
            product_price_element = driver.find_element(By.CLASS_NAME, "product-price-value")
            entries["product price"].textvariable.set("%s" % extk.string_to_float(product_price_element.text))        
        except:
            logging.info("no price in the window: %s" % driver.current_url.split("?")[0])
        # shipping label
        entries["shipping label"] = extk.Entry(self, state="readonly", textvariable=tk.StringVar(), width=10, bd=0, justify="right")
        entries["shipping label"].textvariable.set("ships: ")
        entries["shipping label"].grid(row=0, column=2, sticky="w"+"e")
        # shipping entry
        entries["shipping price"] = extk.Entry(self, textvariable=tk.StringVar(), width=7, justify="center")
        entries["shipping price"].grid(row=0, column=3, sticky="w"+"e")
        entries["shipping price"].bind("<Return>", self.total_copy)
        try:
            shipping_price_element = driver.find_element(By.CLASS_NAME, "product-shipping-price")
            entries["shipping price"].textvariable.set("%s" % extk.string_to_float(shipping_price_element.text))        
        except:
            logging.info("no shipping in the window: %s" % driver.current_url.split("?")[0])
        # options and recalculate buttons
        buttons["options"] = tk.Button(self, text="options", command=lambda: self.options_rec())
        buttons["options"].grid(row=1, column=0, sticky="w"+"e")
        buttons["all"] = tk.Button(self, text="all", command=lambda: self.recalculate_all())
        buttons["all"].grid(row=1, column=1, pady=3, sticky="w"+"e")
        # total label
        entries["total label"] = extk.Entry(self, state="readonly", textvariable=tk.StringVar(), width=10, bd=0, justify="right")
        entries["total label"].textvariable.set("total: ")
        entries["total label"].grid(row=1, column=2, sticky="w"+"e")
        # total entry
        entries["total price"] = extk.Entry(self, textvariable=tk.StringVar(), width=7, justify="center")
        entries["total price"].grid(row=1, column=3, sticky="w"+"e")
        entries["total price"].bind("<Return>", self.options_enter_pressed)
        self.total_copy()
        # options labels and entries
        if "aliexpress" in driver.current_url:
            self.options_aliexpress()        
        if "nesky" in driver.current_url:
            self.options_nes()
    def options_rec(self):
        readonlies = self.options_readonly
        entries = self.options_entry
        driver = self.driver        
        driver.switch_to.window("active")

        entity_elements = driver.find_elements(By.CSS_SELECTOR, ".option-block > div:nth-child(2) > span")
        entities = [element.text for element in entity_elements]
        updates = driver.find_elements(By.CSS_SELECTOR, ".option-block > div.edit-buttons > i.fa.fa-pencil")
        entries = dict([(readonly.textvariable.get(), entry.get()) for readonly, entry in zip(readonlies.values(), entries.values())])
        # entering price
        for index in range(len(entities)):
            if entries.get(entities[index]):
                driver.execute_script("var element = arguments[0]; element.scrollIntoView(); element.click()", updates[index])
                base_price = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[formcontrolname='base_price']")))
                base_price.send_keys(Keys.CONTROL + "a")
                base_price.send_keys(extk.round_string(string=entries.get(entities[index])))
                driver.execute_script("arguments[0].click()", driver.find_element(By.CSS_SELECTOR, "button[type='submit']"))
                WebDriverWait(driver, 5).until(EC.invisibility_of_element((By.CSS_SELECTOR, "button[type='submit']")))
        # recalculate 
        recalculates = driver.find_elements(By.CSS_SELECTOR, "span[title='Recalculate']")
        recalculated = 0
        for index in range(len(entities)):
            if entries.get(entities[index]):
                driver.execute_script("arguments[0].click()", recalculates[index])
                recalculated += 1
        logging.info("recalculated: %d/%d" % (recalculated, len(recalculates)))
    def recalculate_all(self):
        readonlies = self.options_readonly
        entries = self.options_entry
        driver = self.driver
        driver.switch_to.window("active")

        #variables    
        updates = driver.find_elements(By.CSS_SELECTOR, ".option-block > div.edit-buttons > i.fa.fa-pencil")
        counts = min(len(updates), len(readonlies))
        for index in range(counts):
            if entries["%d entry" % index].get():
                driver.execute_script("var element = arguments[0]; element.scrollIntoView(); element.click()", updates[index])
                base_price = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[formcontrolname='base_price']")))
                base_price.send_keys(Keys.CONTROL + "a")
                base_price.send_keys(extk.round_string(string=entries["%d entry" % index].get()))
                driver.execute_script("arguments[0].click()", driver.find_element(By.CSS_SELECTOR, "button[type='submit']"))   
                WebDriverWait(driver, 5).until(EC.invisibility_of_element((By.CSS_SELECTOR, "button[type='submit']")))
        # recalculate
        recalculates = driver.find_elements(By.CSS_SELECTOR, "span[title='Recalculate']")
        recalculated = 0
        for index in range(counts):
            if entries["%d entry" % index].get():
                driver.execute_script("arguments[0].click()", recalculates[index])
                recalculated += 1
        logging.info("recalculated: %d/%d" % (recalculated, len(recalculates)))
    # service functions
    def create_option_entries(self, text="", price="", event=None):
        readonlies = self.options_readonly
        entries = self.options_entry
        row = len(readonlies) # or len(entries) the same
        # readonly options
        readonlies["%d suplier " % row] = extk.Entry(self.options_frame, state="readonly", textvariable=tk.StringVar(), width=15, bd=0, justify="left")
        readonlies["%d suplier " % row].textvariable.set(text or "%d price" % (row + 1))
        readonlies["%d suplier " % row].grid(row=row, column=0, sticky="w"+"e")
        # entry options
        entries["%d entry" % row] = extk.Entry(self.options_frame, textvariable=tk.StringVar(), width=15, justify="center")
        entries["%d entry" % row].grid(row=row, column=1, pady=2, sticky="w"+"e")
        entries["%d entry" % row].insert(0, price)
        # binds
        entries["%d entry" % row].bind('<Return>', lambda event: self.options_enter_pressed(event=event))
    def options_aliexpress(self):
        rec_entries = self.entries
        options_readonly = self.options_readonly
        options_entry = self.options_entry
        driver = self.driver
        
        try: driver.current_url
        except NoSuchWindowException:
            logging.warning("window closed"); return
        # variables
        html = driver.page_source
        search = re.compile('(\[{"isShowTypeColor".*\]),"skuPriceList"').search(html)
        orders = json.loads(search.group(1) if search else "[]")
        search = re.compile('(\[{"skuAttr".*?\}\}\])').search(html)
        prices = json.loads(search.group(1) if search else "[]")
        options_sku = []
        options_price = []
        selected_options = []
        # options sku
        for order in orders:
            for skuPropertyValue in order["skuPropertyValues"]:
                options_sku.append({skuPropertyValue["propertyValueDisplayName"] : skuPropertyValue["propertyValueId"]})
        # options price
        for price in prices:
            try:
                options_price.append({price["skuPropIds"] : price["skuVal"]["skuActivityAmount"]["value"]})
            except KeyError:
                options_price.append({price["skuPropIds"] : price["skuVal"]["skuAmount"]["value"]})
        options_price = extk.price_sort(orders, options_price)
        # selected options
        sku_buttons = driver.find_elements(By.CLASS_NAME, "sku-property-item")
        for button in sku_buttons:
            if "selected" in button.get_attribute("class"):
                selected_options.append(options_sku[sku_buttons.index(button)])
        # destroy old frame and create new
        if getattr(self, "options_frame", None):
            self.options_frame.destroy()
            options_readonly.clear()
            options_entry.clear()
        self.options_frame = tk.LabelFrame(self, text="options", padx=5, pady=5)
        self.options_frame.grid(row=3, columnspan=10, sticky="n"+"s"+"w"+"e")
            # create options entry
        for amount in copy.deepcopy(options_price):
            skuIds, price = amount.popitem()
            for selected in selected_options:
                selected_sku = str(list(selected.values())[0])
                if selected_sku in skuIds:
                    skuIds = skuIds.replace("," + selected_sku, "").replace(selected_sku + ",", "")
                else:
                    skuIds = "empty"
            if skuIds != "empty":
                # display price
                product = int(price.replace(".", ""))
                shipping = rec_entries["shipping price"].get() or "0"
                shipping = int(shipping.replace(",", "").replace(".", ""))
                price = int((product + shipping) * config["factor"])
                # replace sku value to sku name
                skuNames = extk.skuValues_to_names(skuValues=skuIds, options_sku=options_sku)

                self.create_option_entries(text = skuNames, price=price)
    def options_nes(self):
        driver = self.driver
        # destroy old frame and create new
        if getattr(self, "options_frame", None):
            self.options_frame.destroy()
            self.options_readonly.clear()
            self.options_entry.clear()
        self.options_frame = tk.LabelFrame(self, text="options", padx=5, pady=5)
        self.options_frame.grid(row=3, columnspan=10, sticky="n"+"s"+"w"+"e")

        entity_elements = driver.find_elements(By.CSS_SELECTOR, ".option-block > div:nth-child(2) > span")
        entities = [element.text for element in entity_elements]
        for entity in entities:
            self.create_option_entries(text=entity)
    def total_copy(self, event=None):
        rec_entries = self.entries
        
        product_price = rec_entries["product price"].get() or "0"
        shipping_price = rec_entries["shipping price"].get() or "0"
        product = int(product_price.replace(",", "").replace(".", ""))
        shipping = int(shipping_price.replace(",", "").replace(".", ""))
        total = int((product + shipping) * config["factor"])
        total_str = str(total or "")

        rec_entries["total price"].textvariable.set(total_str)
        pyperclip.copy(total_str)               
    def options_enter_pressed(self, event):
        entries = self.options_entry
        for name in entries:
            text = event.widget.get()
            entries[name].textvariable.set(text)

if __name__ == "__main__":
    import workhelper