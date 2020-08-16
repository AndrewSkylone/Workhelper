import re, pyperclip, copy, os, time, shelve, math, tkinter as tk
from datetime import *
from importlib import reload

import configuration
import extended_tk as extk


DATE_INDEX = 3
reload(configuration)
config = configuration.graphic

class Graphic(tk.Toplevel):
    def __init__(self, master, cnf={}, **kw):
        tk.Toplevel.__init__(self, master, cnf, **kw)

        self.screen_w = self.winfo_screenwidth()
        self.screen_h = self.winfo_screenheight()
        self.geometry("+%d+%d" % (self.screen_w / 3, self.screen_h / 3))
        self.title(master.title())

        self.create_widgets()
        self.update_scale()       


    def create_widgets(self):
        proportion = self.screen_w / self.screen_h
        self.start_width = self.screen_w / (proportion + 2)

        self.graphic = tk.Canvas(self, width=self.start_width, height=self.start_width)
        self.graphic.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        self.graphic.bind("<Configure>", self.update_graphic)


        frame = tk.LabelFrame(self, text="time working", padx=5)
        frame.pack(side=tk.TOP, fill=tk.X)

        total_lable = tk.Label(frame, text="Total time: ")
        total_lable.grid(row=0, column=0, sticky="w")
        self.total_entry = Etk.Entry(frame, state="readonly", textvariable=tk.StringVar(), bd=0)
        self.total_entry = mod.Entry(frame, state="readonly", textvariable=tk.StringVar(), bd=0)
        self.total_entry.grid(row=0, column=1, sticky="w")

        breaks_lable = tk.Label(frame, text="Without breaks: ")
        breaks_lable.grid(row=1, column=0, sticky="w")
        self.breaks_entry = Etk.Entry(frame, state="readonly", textvariable=tk.StringVar(), bd=0)        
        self.breaks_entry = mod.Entry(frame, state="readonly", textvariable=tk.StringVar(), bd=0)        
        self.breaks_entry.grid(row=1, column=1, sticky="w")

        self.breaks_scale = tk.Scale(frame, orient=tk.HORIZONTAL, command=self.on_scale)
        self.breaks_scale.grid(row=2, column=0, columnspan=2, sticky="w" + "e")

        self.breaks_menu = tk.Menubutton(frame, text="breaks", relief=tk.RAISED)
        self.breaks_menu.menu = tk.Menu(self.breaks_menu, tearoff=0)
        self.breaks_menu["menu"] = self.breaks_menu.menu
        self.breaks_menu.grid(row=3, column=0, columnspan=2, pady=10, sticky="w" + "e")

    def on_stats_update(self):
        self.update_graphic()
        self.update_scale()

    def update_scale(self):
        def update_data():
            max_break = 0
            total = 0
            previous = datetime.strptime(stats[0][DATE_INDEX], r"%Y-%m-%d %H:%M:%S")

            for row in stats:
                current = datetime.strptime(row[DATE_INDEX], r"%Y-%m-%d %H:%M:%S")
                secdelta = datetime.timestamp(current) - datetime.timestamp(previous)
                if current.day == previous.day:
                    max_break = max(secdelta // 60, max_break)
                    total += secdelta               
                previous = current  

            hours, remainder = divmod(total, 3600)
            minutes, seconds = divmod(remainder, 60) 

            self.total_entry.textvariable.set("%02d:%02d" % (hours, minutes))        
            scale.configure(to=max_break)
            scale.set(max_break)

        scale = self.breaks_scale
        stats = self.master.stats

        update_data()

    def update_graphic(self, event=None):
        def point_enter(event):
            point = graphic.find_closest(event.x, event.y)
            x1, y1, x2, y2 = graphic.coords(point)
            date, orders = coord_to_values(y=(y1 + y2) / 2 - pady)

            graphic.create_text(padx + scale_line, (y1 + y2) / 2 , text=orders, font=text_font, anchor="w", tags="pointInfo")
            graphic.create_text(padx + scale_line, pady / 2, text=sorted_stats[orders - 1][1], font=text_font, anchor="w", tags="pointInfo")
            graphic.create_text((x1 + x2) / 2, height - pady - scale_line, text=date.time(), font=text_font, anchor="s", tags="pointInfo")
            graphic.tag_lower("pointInfo")
        def point_leave(event):            
            graphic.delete("pointInfo")
        def coord_to_values(x=0, y=0):
            orders = round(total - y / (lengthY / total))
            date = datetime.strptime(sorted_stats[orders - 1][DATE_INDEX], r"%Y-%m-%d %H:%M:%S")
            return date, orders
        def values_to_coord(date=None, orders=None):
            delta = datetime.timestamp(date) - datetime.timestamp(first_date)
            x = padx + delta * (lengthX / secdelta) 
            y = pady + lengthY - orders * (lengthY / total) 
            return x, y
        def create_arrows():
            graphic.create_line(padx, pady, padx, height-pady, arrow=tk.FIRST, width=line_width)
            graphic.create_line(padx, height-pady, width-padx, height-pady, arrow=tk.LAST, width=line_width)
        def create_scale():
            # orders scaleY
            total_text = graphic.create_text(padx / 2, pady, text=total, font=text_font)
            text_height = graphic.bbox(total_text)[3] - graphic.bbox(total_text)[1]
            min_interval = text_height * 2
            ratio = lengthY / total
            interval = math.ceil(min_interval / ratio) * ratio
            amount = math.ceil(lengthY / interval)
            for i in range(1, amount):
                graphic.create_line(padx - scale_line / 2, i * interval + pady,
                                    padx + scale_line / 2, i * interval + pady, width=line_width)
                orders = coord_to_values(y=i * interval)[1]
                graphic.create_text(padx / 2, i * interval + pady, font=text_font, text=orders)

            # dates scaleX
            date_text = graphic.create_text(width - padx, height - pady / 2.5, text=last_date.date(), font=text_font)
            bounds = graphic.bbox(date_text)
            text_width = bounds[2] - bounds[0]
            text_height = bounds[3] - bounds[1]
            graphic.create_text(width - padx, bounds[1] - 5 * scaleY, text=last_date.time(), font=text_font)
            amountX = int(lengthX / (text_width * 1.1))
            intervalX = lengthX / amountX

            for i in range(amountX):
                graphic.create_line(padx + i * intervalX, height - pady + scale_line / 2,
                                    padx + i * intervalX, height - pady - scale_line / 2, width=line_width)     
                date = first_date + timedelta(seconds=int(secdelta / amountX * i))                
                graphic.create_text(i * intervalX + padx, bounds[1] - 5 * scaleY, text=date.time(), font=text_font)
                graphic.create_text(i * intervalX + padx, height - pady / 2.5, font=text_font, text=date.date())
        def draw_points():
            points = []
            radius = point_radius

            for i, row in enumerate(sorted_stats):
                date = datetime.strptime(row[DATE_INDEX], r"%Y-%m-%d %H:%M:%S")
                x, y = values_to_coord(date=date, orders=i + 1)
                point = graphic.create_oval(x-radius, y-radius, x+radius, y+radius, fill="green", outline="green", tags="point",
                                            activeoutline="red", activewidth=line_width * 5)
                points.append(point)

            graphic.tag_bind("point", "<Enter>", point_enter)    
            graphic.tag_bind("point", "<Leave>", point_leave)    

            return points
        def draw_route(points):
            lastX = graphic.coords(points[0])[2]
            lastY = graphic.coords(points[0])[3] - point_radius

            for point in points[1:]:
                x1, y1, x2, y2 = graphic.coords(point)
                x = (x1 + x2) / 2
                y = (y1 + y2) / 2
                graphic.create_line(lastX, lastY, x, y, fill="green", width=line_width, tags="routes")
                lastX, lastY = x, y
            graphic.tag_lower("routes")
            
        total = len(self.master.stats)
        graphic = self.graphic
        start_width = start_height = self.start_width
        width = graphic.winfo_width()
        height = graphic.winfo_height()

        scaleX = width / start_width
        scaleY = height / start_height
        scale = min(scaleX, scaleY)
        padx, pady = 30 * scaleX, 40 * scaleY
        lengthX = width - 2 * padx
        lengthY = height - 2 * pady

        scale_line = 5 * scaleX
        point_radius = ((height / total) ** 0.2) * scale
        line_width = 1.0 * scale
        text_font = config["text font"][0], int(config["text font"][1] * scale)

        sorted_stats = sorted(self.master.stats, key=lambda row: row[DATE_INDEX])
        first_date = datetime.strptime(sorted_stats[0][DATE_INDEX], r"%Y-%m-%d %H:%M:%S")
        last_date = datetime.strptime(sorted_stats[-1][DATE_INDEX], r"%Y-%m-%d %H:%M:%S")
        secdelta = datetime.timestamp(last_date) - datetime.timestamp(first_date)

        graphic.delete("all")
        create_arrows()
        create_scale()
        graphic.points = draw_points()
        draw_route(points=graphic.points)

        
    def on_scale(self, value):
        menu = self.breaks_menu.menu   
        menu.delete(0, "end")
        sorted_stats = sorted(self.master.stats, key=lambda row: row[DATE_INDEX])
        breaks = []
        total = 0
        exclude_sec = int(value) * 60
        previous = datetime.strptime(sorted_stats[0][DATE_INDEX], r"%Y-%m-%d %H:%M:%S")

        for row in sorted_stats:
            current = datetime.strptime(row[DATE_INDEX], r"%Y-%m-%d %H:%M:%S")
            secdelta = datetime.timestamp(current) - datetime.timestamp(previous)
            if current.day == previous.day:
                if secdelta < exclude_sec:
                    total += secdelta
                else:
                    breaks.append({"date" : previous, "break" : timedelta(seconds=secdelta)})   
            previous = current  

        hours, remainder = divmod(total, 3600)
        minutes, seconds = divmod(remainder, 60)         
        self.breaks_entry.textvariable.set("%02d:%02d" % (hours, minutes))  
        self.breaks_menu["text"] = "breaks: %d" % len(breaks)

        for break_ in breaks:
            menu.add_command(label="%s %16s" % (break_["date"], break_["break"]))






        
