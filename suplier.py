import copy, re, json, logging, time, pyperclip, tkinter as tk
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from googletrans import Translator

import extended_tk as extk

class Suplier(tk.Toplevel):
    def __init__(self, master, driver, cfg={}, **kw):
        kw["text"] = "saved suplier"
        tk.Toplevel.__init__(self, master, cfg, **kw)

        self.driver = driver        
        self.create_widgets()
    

    def create_widgets(self):
        driver = self.driver
        labels = self.labels = {}
        optionMenu = self.OptionMenu = {}
        entries = self.entries = {}
        # url
        self.url_entry = extk.Entry(self, state="readonly", textvariable=tk.StringVar(), width=25, bd=0, justify="left")
        url = driver.current_url.split("?")[0].replace(".ru", ".com")
        self.url_entry.textvariable.set(url[:8] + url[url.find("aliexpress"):])
        self.url_entry.grid(row=0, columnspan=10, sticky="w"+"e")
        self.url_entry.bind('<Button-1>', lambda event: pyperclip.copy(self.url_entry.textvariable.get()))
        # price widgets
        self.create_price_widgets()
        # create options label frame
        self.options_frame = tk.LabelFrame(self, text="options", padx=5, pady=5)
        self.options_frame.grid(row=2, columnspan=10, sticky="n"+"s"+"w"+"e")
        # options
        html = driver.page_source
        search = re.compile('(\[{"isShowTypeColor".*\]),"skuPriceList"').search(html)
        orders = json.loads(search.group(1) if search else "[]")
        self.options_sku = options_sku = []
        selected_options = []
        # options sku
        for order in orders:
            for skuPropertyValue in order["skuPropertyValues"]:
                sku = {}
                sku["propertyValueDisplayName"] = skuPropertyValue["propertyValueDisplayName"]
                sku["skuPropertyValue"] = skuPropertyValue["propertyValueId"]
                sku["order"] = order["order"]
                sku["skuPropertyName"] = order["skuPropertyName"]
                options_sku.append(sku)
        # selected options
        sku_buttons = driver.find_elements(By.CLASS_NAME, "sku-property-item")
        for button in sku_buttons:
            if "selected" in button.get_attribute("class"):
                selected_options.append(options_sku[sku_buttons.index(button)])
        # create entries
        for order in orders:
            row = len(labels) * 2
            language = re.compile('"language":"(\w*)","locale"').findall(driver.page_source)[0]
            # options names
            skuPropertyName = Translator().translate(order["skuPropertyName"], src=language).text
            labels[order["order"]] = tk.Label(self.options_frame, text=skuPropertyName.lower() + ":")
            labels[order["order"]].grid(row=row, sticky="w")
            # sku names
            sku_names = [sku["propertyValueDisplayName"] for sku in options_sku if sku["order"] == order["order"]]
            optionMenu[order["order"]] = extk.OptionMenu(self.options_frame, tk.StringVar(), *sku_names)
            optionMenu[order["order"]].grid(row=row + 1, sticky="w" + "e")
            # sku values
            entries[order["order"]] = extk.Entry(self.options_frame, textvariable=tk.StringVar(), width=15, bg="#f0f0f0", bd=1, justify="center")
            entries[order["order"]].grid(row=row + 1, column=1, sticky="w"+"e")
            # relation vars
            var1 = optionMenu[order["order"]].textvariable
            var2 = entries[order["order"]].textvariable
            optionMenu[order["order"]].textvariable.trace("w", lambda *args, var1=var1, var2=var2: self.relation(var1, var2))
        for selected in selected_options:
            optionMenu[selected["order"]].textvariable.set(selected["propertyValueDisplayName"]) 
    def create_price_widgets(self):
        driver = self.driver
        # price
        self.price_entry = extk.Entry(self, state="readonly", textvariable=tk.StringVar(), width=10, bd=0, justify="left")
        self.price_entry.grid(row=1, pady=5, sticky="w"+"e")
        self.total_entry = extk.Entry(self, textvariable=tk.StringVar(), bg="#f0f0f0", width=5, bd=1, justify="center")
        self.total_entry.grid(row=1, column=1, sticky="w"+"e")
        try:
            product_price_element = driver.find_element(By.CLASS_NAME, "product-price-value")
            self.price_entry.textvariable.set("%s" % extk.string_to_float(product_price_element.text))        
        except:
            logging.info("no price in the window: %s" % driver.current_url.split("?")[0])
        try:
            shipping_price_element = driver.find_element(By.CLASS_NAME, "product-shipping-price")
            product_price = self.price_entry.get()
            shipping_price = extk.string_to_float(shipping_price_element.text)
            self.price_entry.textvariable.set("%s + %s" % (product_price, shipping_price) if shipping_price else product_price)         
        except:
            logging.info("no shipping in the window: %s" % driver.current_url.split("?")[0])
        try:
            self.total_entry.textvariable.set("%.2f" % eval(self.price_entry.get()))
        except SyntaxError:
            logging.warning("price error in the window: %s" % driver.current_url.split("?")[0])
    def paste(self):
        driver = self.driver
        entries = self.entries
        labels = self.labels

        try:
            WebDriverWait(driver, 0.1).until(EC.visibility_of_element_located((By.CLASS_NAME, "modal-dialog.modal-lg"))) # open or no suplier window
        except TimeoutException:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, ".option-suppliers-block.flow-content-block > div.flow-add-new")
                driver.execute_script("arguments[0].click()", self.find_nearest_element(elements))
            except IndexError:
                logging.info("no suplier frames in the window: %s" % driver.current_url.split("?")[0])
                return
        try: driver.execute_script("arguments[0].click()", driver.find_element(By.XPATH, "//td[text() = 'AliExpress']")) # check "aliexpress"
        except NoSuchElementException: pass

        # entering values
        url_element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[formcontrolname='externalProductReference']")))
        url_element.send_keys(Keys.CONTROL + "a")
        url_element.send_keys(self.url_entry.textvariable.get())

        nes_entries = driver.find_elements(By.CSS_SELECTOR, "input.form-control.margin-bottom")
        for i in range(len(entries) - len(nes_entries)//2):
            plus_element = driver.find_element(By.CSS_SELECTOR, "i.fa.fa-plus")
            driver.execute_script("arguments[0].click()", plus_element)
        for index, key in enumerate(labels):
            nes_entries = driver.find_elements(By.CSS_SELECTOR, "input.form-control.margin-bottom")
            nes_entries[index*2].send_keys(Keys.CONTROL + "a")
            nes_entries[index*2].send_keys(labels[key]["text"].replace(":", ""))
            nes_entries[index*2].send_keys(Keys.RETURN)
        for index, key in enumerate(entries):
            nes_entries = driver.find_elements(By.CSS_SELECTOR, "input.form-control.margin-bottom")
            nes_entries[index*2 + 1].send_keys(Keys.CONTROL + "a")
            nes_entries[index*2 + 1].send_keys(entries[key].textvariable.get())
            nes_entries[index*2 + 1].send_keys(Keys.RETURN)
        driver.execute_script("arguments[0].click()", driver.find_element(By.CSS_SELECTOR, "button[type='submit']"))
        WebDriverWait(driver, 5).until(EC.invisibility_of_element((By.CSS_SELECTOR, "button[type='submit']")))
        # change price
            # price entry
        costs = driver.find_elements(By.CSS_SELECTOR, "div.costs-block > div")
        adds_new = [costs[i] for i in range(0, len(costs), 2) if costs[i].get_attribute("class") == "flow-add-new"]
        if not adds_new:
            return
        driver.execute_script("arguments[0].click()", adds_new[0])
            # dropbox of price entry
        try:
            element = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "select")))
            dropbox = Select(element)
            dropbox.select_by_visible_text("Euro")
            # price of price entry
            price_element = driver.find_element(By.CSS_SELECTOR, "input[formcontrolname='value']")
            price_element.send_keys(self.total_entry.get())
            driver.execute_script("arguments[0].click()", driver.find_element(By.CSS_SELECTOR, "button[type='submit']"))
        except TimeoutException: return
    def relation(self, var1, var2):
        options_sku = self.options_sku
        entries = self.entries
        sku_name = var1.get()
        sku = [option for option in options_sku if sku_name in option.values()][0]        
        var2.set("sku-%s-%s" % (sku["order"], sku["skuPropertyValue"]))

        # price
        html = self.driver.page_source
        search = re.compile('(\[{"skuAttr".*?\}\}\])').search(html)
        prices = json.loads(search.group(1) if search else "[]")
        options_price = {}
        # options price
        for price in prices:
            try:
                options_price.update({price["skuPropIds"] : price["skuVal"]["skuActivityAmount"]["value"]})
            except KeyError:
                options_price.update({price["skuPropIds"] : price["skuVal"]["skuAmount"]["value"]})
        # formating price
        orders = [key for key in entries]
        skuIds = ",".join([entries[order].get().split("-")[-1] for order in orders])
        try:
            price = options_price[skuIds]
        except KeyError:
            return
            
        new_price = self.price_entry.get().split(" + ")
        new_price[0] = str(price)
        self.price_entry.textvariable.set(" + ".join(new_price))
        self.total_entry.textvariable.set("%.2f" % eval(self.price_entry.get()))
    
    def find_nearest_element(self, elements):
        
        height = self.driver.get_window_size()["height"]
        pageYOffset = self.driver.execute_script("return window.pageYOffset")
        screen_middle = height / 2 + pageYOffset

        return sorted(elements, key=lambda element: abs(screen_middle - element.location["y"]))[0]


if __name__ == "__main__":
    import workhelper