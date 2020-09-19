import tkinter as tk
import copy

class Entry(tk.Entry):
    def __init__(self, master, cfg={}, **kw):
        self.textvariable = kw.get("textvariable", None)
        tk.Entry.__init__(self, master, **kw)
        
        self.bind('<Button-3>', lambda event: self.button_pressed(event))

    def button_pressed(self, event):
        event.widget.delete(0, tk.END)
        event.widget.focus()


class OptionMenu(tk.OptionMenu):
    def __init__(self, master, textvariable, *values):
        self.textvariable = textvariable
        tk.OptionMenu.__init__(self, master, textvariable, *values)


class Toplevel(tk.Toplevel):
    """ Singleton """

    def __init__(self, master, cnf={}, **kw):
        tk.Toplevel.__init__(self, master, cnf, **kw)

        self.__class__.instance = self
      
        mouseX, mouseY = self.get_mouse_position()
        self.geometry(f"+{mouseX}+{mouseY}")
        self.resizable(False, False)
    
    def get_mouse_position(self):
        return self.master.winfo_pointerx(), self.master.winfo_pointery()
    
    def __new__(cls, *args, **kwargs):
        if hasattr(cls, "instance"):
            cls.instance.destroy()
        return tk.Toplevel.__new__(cls)

    


#TODO move this features into their modules
def price_sort(orders, prices):
    if not orders: return []
    skuIds = [str(x["propertyValueId"]) for x in orders[0]["skuPropertyValues"]]

    for order in orders[1:]: 
        temp = []
        for index in range(len(skuIds)):
            for sku in order["skuPropertyValues"]:
                temp.append(skuIds[index] + "," + str(sku["propertyValueId"]))
        skuIds = temp
    price_sorted = []
    for skuId in skuIds:
        for price in prices:
            key = list(price.keys())[0]
            if skuId == key:
                price_sorted.append({skuId : "%.2f" % price[key]})
    return price_sorted

def string_to_float(string):
    new_string = "".join([s for s in string if s.isdigit() or s == "," or s =="."])
    new_string = new_string.replace(",", ".")
    dot_index = new_string.index(".")

    return new_string[:dot_index+3]
def round_string(string):
    digit = int(string) - int(string) % 50 + 49
    number = int(string) - int(string) % 10 + 9
    return str(digit) if int(string) > 499 else str(number)


def skuValues_to_names(skuValues, options_sku):
    reversed_sku = {}
    skuValues = skuValues.split(",")
    for option_sku in copy.deepcopy(options_sku):
        sku_name, sku_value = option_sku.popitem()
        reversed_sku[str(sku_value)] = sku_name

    return ",".join([reversed_sku[skuValue] for skuValue in skuValues])


if __name__ == "__main__":
    import workhelper