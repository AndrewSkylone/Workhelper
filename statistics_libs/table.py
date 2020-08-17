import re, pyperclip, copy, os, time, shelve, tkcalendar, math, tkinter as tk
from importlib import reload
from datetime import *
import webbrowser
from tkinter import ttk

from selenium.common.exceptions import *

import configuration
import extended_tk as extk
from statistics_libs import graphic


reload(configuration)
config = configuration.__dict__["table"]
MESSAGE_INDEX = 1
DATE_INDEX = 3

class Table(tk.Toplevel):
    def __init__(self, master, stats, cnf={}, **kw):
        tk.Toplevel.__init__(self, master, cnf, **kw) 
        self.title(master.user + " " + master.date_button["text"])
        self.resizable(False, False)

        self.stats_backup = copy.deepcopy(stats)
        self.stats = copy.deepcopy(stats)
        self.displayed = {} # {option_name : tk.String}

        self.create_widgets()
        self.update_page(page=1)
        self.update_table()


    def create_widgets(self):
        # menubar
        self.menubar = self.create_menubar(master=self)
        self.config(menu=self.menubar)
        # table
        self.table = self.create_table()        
        self.table.grid(row=0, rowspan=10, columnspan=3)

        # navigate buttons
        buttons = {"First" : 0, "Previous" : 1, "Next" : 3, "Last" : 4} # {label : column}
        buttons_frame = tk.Frame(self, padx=10)
        buttons_frame.grid(row=11, column=0, pady=10, sticky="w" + "n")

        for label, column in buttons.items():
            button = tk.Button(buttons_frame, text=label, font=config["button font"],
                                        command=lambda label=label: self.update_page(label=label))
            button.grid(row=0, column=column, sticky="w"+"e")

        self.page_entry = Etk.Entry(buttons_frame, textvariable=tk.StringVar(), width=5, font=config["entry font"], justify="center")
        self.page_entry.bind("<Return>", lambda e: self.update_page(label="Entered"))
        self.page_entry.grid(row=0, column=2, sticky="w"+"e")

        self.pages_entry = Etk.Entry(buttons_frame, state="readonly", textvariable=tk.StringVar(), bd=0, justify="left")
        self.pages_entry.grid(row=1, column=0, columnspan=2, pady=4, sticky="w")

        self.total_entry = Etk.Entry(buttons_frame, state="readonly", textvariable=tk.StringVar(), bd=0, justify="left")
        self.page_entry = mod.Entry(buttons_frame, textvariable=tk.StringVar(), width=5, font=config["entry font"], justify="center")
        self.page_entry.bind("<Return>", lambda e: self.update_page(label="Entered"))
        self.page_entry.grid(row=0, column=2, sticky="w"+"e")

        self.pages_entry = mod.Entry(buttons_frame, state="readonly", textvariable=tk.StringVar(), bd=0, justify="left")
        self.pages_entry.grid(row=1, column=0, columnspan=2, pady=4, sticky="w")

        self.total_entry = mod.Entry(buttons_frame, state="readonly", textvariable=tk.StringVar(), bd=0, justify="left")
        self.total_entry.grid(row=2, column=0, columnspan=2, sticky="w")

        # functions buttons
        buttons_frame = tk.Frame(self, padx=10)
        buttons_frame.grid(row=11, column=2, pady=10, sticky="e")

        convert_button = tk.Button(buttons_frame, text="convert time", font=config["button font"], command=self.convert_time)
        convert_button.grid(row=0, column=3, padx=3, pady=3, sticky="w"+"e")

        reset_button = tk.Button(buttons_frame, text="reset table", font=config["button font"], command=lambda :self.reset_all())
        reset_button.grid(row=1, column=4, padx=3, pady=3, sticky="w"+"e")

        graphic_button = tk.Button(buttons_frame, text="graphic", font=config["button font"], command=self.create_graphic)
        graphic_button.grid(row=0, column=4, padx=3, pady=3, sticky="w"+"e")

        # search entry      

        self.search_entry = Etk.Entry(buttons_frame, font=config["entry font"], fg="grey", justify="center")

        self.search_entry = mod.Entry(buttons_frame, font=config["entry font"], fg="grey", justify="center")

        self.search_entry.grid(row=0, column=0, columnspan=2, padx=3, pady=3, sticky="w"+"e")
        self.search_entry.insert(0, "Search") 
        self.search_entry.bind("<FocusIn>", self.search_events)
        self.search_entry.bind("<FocusOut>", self.search_events)
        self.search_entry.bind("<Return>", self.display_filter)
    

    def create_menubar(self, master=None, **options):
        menubar = tk.Menu(master=self, **options)
        menubar.vars = {"Same" : tk.StringVar()}

        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save")
        filemenu.add_command(label="Save as...")
        menubar.add_cascade(label="File", menu=filemenu)

        displaymenu = tk.Menu(menubar, tearoff=0)

        messagemenu = tk.Menu(displaymenu, tearoff=1)
        messagemenu.add_checkbutton(label="Same", variable=menubar.vars["Same"],
                                        onvalue="", offvalue=True, command=self.display_filter)
        messagemenu.add_separator()
        messages = sorted(set([row[1] for row in self.stats]))
        for message in messages:
            menubar.vars[message] = tk.StringVar()
            messagemenu.add_checkbutton(
                            label=message, variable=menubar.vars[message],
                                onvalue="", offvalue=message, command=self.display_filter)
        displaymenu.add_cascade(label="Messages", menu=messagemenu)

        daysmenu = tk.Menu(displaymenu, tearoff=1)
        days = sorted(set([row[3][:11] for row in self.stats]))
        for day in days:
            menubar.vars[day] = tk.StringVar()
            daysmenu.add_checkbutton(
                            label=day, variable=menubar.vars[day],
                                onvalue="", offvalue=day, command=self.display_filter)
        displaymenu.add_cascade(label="Days", menu=daysmenu)

        menubar.add_cascade(label="Display", menu=displaymenu)

        return menubar


    def create_table(self):
        click_posx = None
        def open_selected(event):
            SITE_LINK = "https://nesky.hktemas.com/"
            links = {"Viewed Order" : SITE_LINK + "orders/",
                    "Added Memo" : SITE_LINK + "orders/",
                    "Updated Bucket" : SITE_LINK + "orders/",
                    "Viewed Product Flow" : SITE_LINK + "product-flow/",
                    "Viewed Order Flow" : SITE_LINK + "order-item-flow-page/",
                    "Pressed Reprocess" : SITE_LINK + "order-item-flow-page/",
                    "Updated Price using Base Price" : SITE_LINK + "order-item-flow-page/"}

            selected = table.selection()
            for iid in selected:
                item = table.item(iid)
                message = item["values"][1]
                target = item["values"][2]
                try:
                    webbrowser.open_new_tab("%s%s" % (links[message], target))
                    table.selection_toggle(iid)
                except KeyError:
                    pass

        def toggle_selected(event):
            nonlocal click_posx
            click_posx = event.x
            table.selection_toggle(table.selection())

        def copy_value(event):
            column = int(table.identify_column(click_posx)[1:]) - 1
            item = table.item(table.selection()[0])
            pyperclip.copy(item["values"][column])

        table = ttk.Treeview(self, height=15, show="headings")

        table["columns"] = (0, 1, 2, 3)
        table.column(0, width=75)
        table.column(1, width=400)
        table.column(2, width=100)
        table.column(3, width=200)

        table.heading(0, text="№")
        table.heading(1, text="Message", command=lambda: self.sort_by(column=1))
        table.heading(2, text="Target", command=lambda: self.sort_by(column=2))
        table.heading(3, text="Updated at", command=lambda: self.sort_by(column=3))

        for i in range(15):
            table.insert("", "end", iid=i, tags="all")
        table.tag_configure("all", font=("Arial", 11))
        table.tag_bind("all", "<Return>", open_selected)
        table.tag_bind("all", "<Button-1>", toggle_selected)
        table.tag_bind("all", "<Control-c>", copy_value)

        return table


    def create_graphic(self):
        def on_closing():
            self.new_graphic.destroy()
            del(self.new_graphic)

        reload(graphic) #delete after debelopment!

        if not hasattr(self, "new_graphic"):
            self.new_graphic = graphic.Graphic(master=self)
            self.new_graphic.protocol("WM_DELETE_WINDOW", on_closing)
        else:    
            on_closing()


    def display_filter(self, event=None):
        def filter_same():
            stats_backup = copy.deepcopy(stats)
            for i, row1 in enumerate(stats_backup):
                for row2 in stats_backup[i+1:]:
                    if row1[1] == row2[1] and row1[2] == row2[2]:
                        try:
                            stats.remove(row2)
                        except ValueError:
                            continue
        
        stats = copy.deepcopy(self.stats_backup)

        for label, variable in self.menubar.vars.items():
            if not variable.get():
                continue

            if label == "Same":
                filter_same()
                continue

            for row in copy.deepcopy(stats):
                if row[MESSAGE_INDEX] == label:
                    stats.remove(row)
                elif row[DATE_INDEX][:11] == label:
                    stats.remove(row)

        search = self.search_entry.get()
        if search and search != "Search":
            results = []
            for row in stats:
                for col in range(4):
                    if search in row[col]:
                        results.append(row)
                        break
            stats = results
        
        self.stats = stats        
        self.update_page(page=1)
        self.on_stats_update()
        

    def update_table(self):
        page = int(self.page_entry.textvariable.get())
        index = (page - 1) * 15

        for iid in range(15):
            self.table.item(iid, value=[" "] * 4)
        for i, row in enumerate(self.stats[index:index+15]):
            self.table.item(i, values=row)

        self.table.selection_remove(self.table.get_children())
        

    def update_page(self, page=None, label=None):
        page = page or int(self.page_entry.get())
        pages = math.ceil(len(self.stats) / 15)

        if page < 1 or page > 48:
            return
        if label == "First":
            page = 1
        if label == "Previous" and page > 1:
            page -= 1
        if label == "Next" and page < pages:
            page += 1
        if label == "Last":
            page = pages
        
        self.page_entry.textvariable.set(page)
        self.pages_entry.textvariable.set("Page: %s / %s" % (page, pages))
        self.total_entry.textvariable.set("Total items: %s" % len(self.stats))
        self.update_table()

    def on_stats_update(self):
        if hasattr(self, "new_graphic"):
            self.new_graphic.on_stats_update()        

    def reset_all(self, **kw):       
        if not kw.get("stats", True):
            self.stats = copy.deepcopy(self.stats_backup)
        if not kw.get("page", True):
            self.page_entry.insert(0, 1)
        if not kw.get("filter", True):
            for var in self.menubar.vars.values():
                var.set("")
        if not kw.get("search", True):
            self.search_entry.delete(0, tk.END)

        if not kw:
            self.stats = copy.deepcopy(self.stats_backup)
            self.search_entry.delete(0, tk.END)
            self.page_entry.insert(0, 1)
            for var in self.menubar.vars.values():
                var.set("")
            
        self.display_filter()
        self.update_page()


    def sort_by(self, column):
        if column == 1:
            self.stats.sort(key = lambda row: (row[column], row[column + 1], row[column + 2]))
        elif column == 2:
            self.stats.sort(key = lambda row: (row[column], row[column - 1], row[column + 1]))
        else:
            self.stats.sort(key = lambda row: row[column])            
        self.update_page()
        
    
    def convert_time(self):
        stats = self.stats
        is_converted = not stats[0] in self.stats_backup
        DIFFERENCE = is_converted and -config["time difference"] or config["time difference"]

        for row in stats:
            date = datetime.strptime(row[DATE_INDEX], r"%Y-%m-%d %H:%M:%S")
            converted = date + DIFFERENCE
            row[DATE_INDEX] = converted.strftime(r"%Y-%m-%d %H:%M:%S")

        self.update_table()
        self.on_stats_update()
    

    def search_events(self, event):
        entry = self.search_entry

        if entry.get() == "Search" and event.type.name == "FocusIn":
            entry.delete(0, tk.END)
            entry.config(fg="black")

        elif not entry.get() and event.type.name == "FocusOut":
            entry.config(fg="grey")
            entry.insert(0, "Search")

        