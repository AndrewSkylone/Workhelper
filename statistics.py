import re, pyperclip, os, time, shelve, tkcalendar, tkinter as tk
from datetime import datetime, timedelta
from importlib import reload

from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

import extended_tk as extk
from statistics_libs import table


class Statistics(extk.Toplevel):

    instance = None
    
    def __init__(self, master, driver, **kw):
        extk.Toplevel.__init__(self, master, **kw)

        if Statistics.instance:
            Statistics.instance.destroy()
        Statistics.instance = self

        self.title("Statistics")

        self.FILE_PATH = os.path.join("statistics_libs", "statistics")
        self.driver = driver
        self.user = ""
        self.user_stats = []
        self.table = None
        self.graphic = None

        self.create_widgets()


    def create_widgets(self):
        self.status_entry = extk.Entry(self, state="readonly", textvariable=tk.StringVar(), bd=0, justify="left")
        self.status_entry.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="w" + "e")

        users = [""] + sorted(shelve.open(self.FILE_PATH).keys())
        self.users_optionMenu = extk.OptionMenu(self, tk.StringVar(), *users)
        self.users_optionMenu.grid(row=1, column=0, sticky="w" + "e")
        self.users_optionMenu.textvariable.trace("w", self.update_stats)

        self.date_button = tk.Button(self, command=self.create_calendar)
        self.date_button.grid(row=1, column=1, sticky="w" + "e")

        read_table_button = tk.Button(self, text="read table", command=self.read_table)
        read_table_button.grid(row=1, column=2, sticky="w" + "e")

        self.delete_user_button = tk.Button(self, text="delete user", command=self.delete_user)
        self.delete_user_button.grid(row=1, column=3, sticky="w" + "e")

        table_button = tk.Button(self, text="table", command=self.create_table)
        table_button.grid(row=2, column=0, sticky="w" + "e")

        graphic_button = tk.Button(self, text="graphic") #, command=self.create_graphic)
        graphic_button.grid(row=2, column=1, sticky="w" + "e")

        self.stats_text = tk.Text(self, width=40, height=-1, padx=5, state=tk.DISABLED)
        self.stats_text.grid(row=3, columnspan=4, padx=5, pady=5, sticky="w")

    def destroy(self):
        Statistics.instance = None
        extk.Toplevel.destroy(self)

    def create_calendar(self):
        clicks = 0
        first, last = None, None
        def date_set(event):
            nonlocal clicks, first, last
            clicks += 1
            if clicks % 2 == 1:
                first = cal.selection_get()
            if clicks % 2 == 0:
                last = cal.selection_get()
                if first < last:
                    self.date_button["text"] = first.strftime(r"%d.%m.%Y") + " - " + last.strftime(r"%d.%m.%Y")
                    top.destroy()
                    self.update_stats()
            
        top = tk.Toplevel()
        top.geometry(("+%d+%d") % (self.winfo_rootx(), self.winfo_rooty()))
        today = datetime.today()
        cal = tkcalendar.Calendar(top, lfont="Arial 12", selectemode="days", year=today.year, month=today.month, day=today.day)
        cal.bind("<<CalendarSelected>>", date_set)
        cal.grid()
        top.grab_set() 
    

    def create_table(self):
        if not self.user_stats:
            return            
        reload(table)

        self.table = table.Table(master=self, stats=self.user_stats)


    def read_table(self):
        def read_stats():
            table_xpath = "//tabset/div/tab[2]/div/div[4]/table/tbody"
            table_element = driver.find_element(By.XPATH, table_xpath)
            WebDriverWait(driver, 5).until(EC.visibility_of_all_elements_located((By.XPATH, "//tabset/div/tab[2]/div/div[4]/table/tbody/tr")))
            pages_element = driver.find_element(By.CSS_SELECTOR, "pre.card.card-block.card-header")
            pages = re.search('Page: (\d+) / (\d+)', pages_element.text)
            first, last = int(pages.group(1)), int(pages.group(2))

            if first != 1:
                text = table_element.text
                first_button = driver.find_element(By.LINK_TEXT, "First")
                driver.execute_script("arguments[0].click()", first_button)
                WebDriverWait(driver, 3).until_not(EC.text_to_be_present_in_element((By.XPATH, "//tabset/div/tab[2]/div/div[4]/table/tbody"), text))

            stats = []
            for index in range(last):
                text = table_element.text
                for row_text in text.split("\n"):
                    res = re.search("(\d+) (.*?) (\d+) (\d+-\d+-\d+ \d+:\d+:\d+)", row_text)
                    stats.append([res.group(i) for i in range(1, 5)])
                # move to next page
                next_button = driver.find_element(By.LINK_TEXT, "Next")
                driver.execute_script("arguments[0].click()", next_button)
                if index != last - 1:
                    WebDriverWait(driver, 3).until_not(EC.text_to_be_present_in_element((By.XPATH, "//tabset/div/tab[2]/div/div[4]/table/tbody"), text))
            return stats
        def fix_dates(**kw):
            dates = self.period_dates(dates_str=kw["dates"])
            stats = kw["stats"]

            for date in dates:
                DATE_INDEX = 3
                indexes = set()
                for i in range(len(stats)):
                    if date in stats[i][DATE_INDEX]:
                        indexes.add(i)

                if indexes:
                    buged = indexes ^ set(range(min(indexes), max(indexes) + 1))
                    for i in buged:
                        stats[i][DATE_INDEX] = stats[i-1][DATE_INDEX]
        def save_stats(user, stats, dates): 
            DATE_INDEX = 3
            sorted_stats = {}
            dates = self.period_dates(dates_str=dates)

            for row in stats:
                date = row[DATE_INDEX].split()[0]
                sorted_stats.setdefault(date, []).append(row)
            
            with shelve.open(self.FILE_PATH, writeback=True) as stats_file:
                stats_file.setdefault(user, {})                
                for date in dates:
                    stats_file[user][date] = sorted_stats.get(date, [])

        driver = self.driver
        driver.switch_to.window("active")

        self.users_optionMenu.textvariable.set("")
        self.date_button["text"] = ""

        select = Select(driver.find_element(By.CSS_SELECTOR, "select[class='form-control']"))
        date_element = driver.find_element(By.CSS_SELECTOR, ".selectiongroup > input")
        self.user = select.first_selected_option.text
        dates = date_element.get_attribute("value")

        self.update_status(text="%s %s reading..." % (self.user, dates))

        try:
            period_stats = read_stats()
        except:
            self.update_status(text="reading error", color="red")
            return

        fix_dates(dates=dates, stats=period_stats)
        save_stats(user=self.user, stats=period_stats, dates=dates)
    
        self.date_button["text"] = dates
        self.update_users()
        self.widget_set(widget=self.users_optionMenu, text=self.user)  
        

    def widget_set(self, widget, text):
        widget.textvariable.set(text)
        self.update()


    def delete_user(self):      
        answer = tk.messagebox.askyesno(title="Delete user and data", message="Are you sure?")
        if not answer: return

        with shelve.open(self.FILE_PATH, writeback=True) as stats_file:
            user = self.users_optionMenu.textvariable.get()
            try:
                del(stats_file[user])
            except KeyError:
                tk.messagebox.showerror(title="Error", message="no user %s in database" % user)
            else:
                tk.messagebox.showinfo(title="Error", message="user %s deleted from database" % user)
                self.update_users()
                self.widget_set(widget=self.users_optionMenu, text="")
    

    def update_stats(self, *args):
        self.user = self.users_optionMenu.textvariable.get()
        button_dates = self.date_button["text"]
        self.user_stats.clear()
        if not self.user or not button_dates:
            self.update_counts()
            return
        
        dates = self.period_dates(dates_str=self.date_button["text"])
        with shelve.open(self.FILE_PATH, writeback=True) as stats_file:
            for date in dates:
                try:
                    self.user_stats += stats_file[self.user][date]
                    self.update_status(text="%s %s data loaded" % (self.user, button_dates), color="green")
                except (TypeError, KeyError):
                    date = datetime.strptime(date, r"%Y-%m-%d")
                    self.update_status(text="%s %s no data" % (self.user, date.strftime(r"%d.%m.%Y")), color="red")
                    self.user_stats = []
                    return
                finally:
                    self.update_counts()


    def update_counts(self):
        def count_stats(stats):
            counts = {}
            for row in stats:
                counts.setdefault(row[MESSAGE_INDEX], 0)
                counts[row[MESSAGE_INDEX]] += 1
            return counts

        MESSAGE_INDEX = 1
        counted_stats = count_stats(stats=self.user_stats)
    
        self.update_table(start=1.0, end=tk.END, text="")
        self.stats_text.configure(height=len(counted_stats))

        sorted_keys = sorted(counted_stats, key=lambda k: counted_stats[k], reverse=True)
        for key in sorted_keys:
            self.update_table(end=tk.END, text=key.ljust(self.stats_text["width"] - 5, " "))
            self.update_table(end=tk.END, text=str(counted_stats[key]).rjust(5, " "))


    def update_users(self):
        users = [""] + sorted(shelve.open(self.FILE_PATH).keys())
        menu = self.users_optionMenu["menu"]        
        menu.delete(0, "end")
        for string in users:
            menu.add_command(label=string, command=lambda value=string:
                            self.users_optionMenu.textvariable.set(value))


    def update_status(self, text, color="black"):
        self.status_entry.configure(fg=color)
        self.status_entry.textvariable.set(text)
        self.update()
    
    def update_table(self, start=1.0, end=tk.END, text=""):
        self.stats_text.configure(state=tk.NORMAL)
        if text:
            self.stats_text.insert(end, text)
        else:
            self.stats_text.delete(start, end)
        self.stats_text.configure(state=tk.DISABLED)

    
    def period_dates(self, **kw):
        dates = kw["dates_str"]
        period = []
        first = datetime.strptime(dates.split(" - ")[0], r"%d.%m.%Y")
        last = datetime.strptime(dates.split(" - ")[1], r"%d.%m.%Y")
        days = re.search("(\d+) day", str(last - first)).group(1)
        
        for day in range(int(days)):
            date = first + timedelta(days=day)
            period.append(date.strftime(r"%Y-%m-%d"))
        return period

if __name__ == "__main__":
    import workhelper