# For automation: Put these files in the Windows Start-up folder.
# Win+R then type "shell:startup" adn drag these files in there.
# ^^^ Actually dont do this?
import os, _thread, time, datetime
# 
import tkinter as tk
from tkinter import messagebox
import tkinter.filedialog as tkf
import tkinter.ttk as ttk
import psutil
import file_management


time_passed_in_program = file_management.open_to('program_time_info.json')
settings_save = file_management.open_to('settings.json')
if settings_save["app_theme"] == "melancholic":
    app_background = "#8e82fe"
    viewer_pane_background = "#ccccff"
    action_pane_background = "#b8b8f2"
    remove_button_background = "#b8b8f2"
    label_foreground = "#462d86"
    label_background = "#242b2e"
elif settings_save["app_theme"] == "dark":
    app_background = "#292936"
    viewer_pane_background = "#46455c"
    action_pane_background = "#3a394f"
    remove_button_background = "#ad0505"
    label_foreground = "White"
    label_background = "#242b2e"
else:
    messagebox.showerror("ERROR", '"app_theme" in "settings.json" is missing or incorrect')

def time_format(seconds):
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    if hour == 0:
        return f"{int(minutes)}m {int(seconds)}s"
    else:
        return f"{int(hour)}h {int(minutes)}m {int(seconds)}s"
    
def date_format(date):
    months = {"01": "January", "02": "Feburary", "03": "March", "04": "April", "05": "May", "06": "June", "07": "July", "08": "August", "09": "September", "10": "October", "11": "November", "12": "December"}
    format = date.split("-")
    return f"{months[format[1]]} {int(format[2])}, {format[0]}"

def find_path(name):
    for pid in psutil.pids():
        try:
            if psutil.Process(pid).name() == name:
                return psutil.Process(pid).exe().replace("\\", "/")
        except psutil.NoSuchProcess:
            print("find_path Error: NoSuchProcess")

class TkinterApp(tk.Tk):
    def __init__(self) -> None:
        tk.Tk.__init__(self)
        self.title("Sonny")
        self.geometry('720x450')
        self.resizable(0, 0)
        self.iconbitmap("sonny.ico")
        self.configure(background=app_background)

        self.game_name_var = tk.StringVar()
        self.game_exe_var = tk.StringVar()
        self.game_path_var = tk.StringVar()

        self.update_game_list()

        menu = tk.Menu(self)
        menu_config = tk.Menu(menu, tearoff=False)
        menu_config.add_command(label='Add Game', command=lambda:self.open_dialog_findfile())
        menu_theme = tk.Menu(menu, tearoff=False)
        menu_theme.add_command(label='Melancholic', command=lambda:self.change_theme("melancholic"))
        menu_theme.add_command(label='Dark', command=lambda:self.change_theme("dark"))
        menu_help = tk.Menu(menu, tearoff=False)
        menu_help.add_command(label='About', command=lambda:self.about_section())
        menu.add_cascade(label='Configure', menu=menu_config)
        menu.add_cascade(label='Theme', menu=menu_theme)
        menu.add_cascade(label='Help', menu=menu_help)
        self.config(menu=menu)

        self.rowconfigure(0, minsize=75, weight=0)
        self.columnconfigure(1, minsize=50, weight=1)

        self.current_game_time = tk.StringVar()
        self.current_game_state = tk.StringVar()
        self.current_game_state.set("MEOW")
        self.current_playtime = tk.Label(textvariable=self.current_game_state, font=(None, 15), background=app_background, foreground=label_foreground)
        self.current_playtime.grid(column=0, row=0, columnspan=2, padx=15, sticky="w")
        self.current_playtime = tk.Label(textvariable=self.current_game_time, font=(None, 15), background=app_background, foreground=label_foreground)
        self.current_playtime.grid(column=0, row=0, columnspan=2, padx=15, sticky="e")

        self.is_program_opened = False
        self.apps_currently_running = []
        self.update()

    def change_theme(self, theme):
        settings_save["app_theme"] = theme
        file_management.write_to("settings.json", settings_save)
        messagebox.showinfo("Important", "You will need to restart the app for theme changes to take place.")

    def check_for_program(self):
        while 1:
            for programs in psutil.process_iter(): # Cycles through the processes
                for program_name in file_management.get_program_info(): # Cycles through the programs
                    # If the program listed is found and running, it'll get the create time
                    # and the current time to find the differnce in both to get how long it
                    # has been running. After that it'll add it to the time info json.
                    while programs.name() == program_name[2] and (program_name[1] + f"/{program_name[2]}") == find_path(program_name[2]):
                        os.chdir(file_management.app_file_path)
                        self.is_program_opened = True
                        time_passed_in_program[program_name[1] + f"/{program_name[2]}"] = time.time() - programs.create_time()
                        self.current_game_state.set(f'Playing "{program_name[0]}"')
                        self.current_game_time.set(f"{time_format(time.time() - programs.create_time())}")
                    if self.is_program_opened == True:
                        self.is_program_opened = False
                        file_management.TIME_INFO_DEFAULT[program_name[1] + "/" + program_name[2]][0] += time_passed_in_program[program_name[1] + f"/{program_name[2]}"]
                        file_management.TIME_INFO_DEFAULT[program_name[1] + "/" + program_name[2]][1] += 1
                        file_management.TIME_INFO_DEFAULT[program_name[1] + "/" + program_name[2]][2] = str(datetime.date.today())
                        file_management.write_to("program_time_info.json", file_management.TIME_INFO_DEFAULT)
                        self.current_game_state.set(f'Last Played "{program_name[0]}"')
                        self.current_game_time.set(f"{time_format(file_management.TIME_INFO_DEFAULT[program_name[1] + '/' + program_name[2]][0])}\n{time_format(time.time() - programs.create_time())}")

    def open_dialog_findfile(self):
        self.game_exe_var.set("")
        os.chdir(file_management.app_file_path)
        path = tkf.askopenfilename(filetypes=[("Executables", "*.exe")])
        self.game_exe_var.set(path.split('/')[-1])
        self.game_path_var.set("/".join(path.split('/')[0:-1]))
        #print(path.split('/')[-1], "/".join(path.split('/')[0:-1]))
        if path != "":
            self.add_game_func()

    def add_game_func(self):        
        top = tk.Toplevel(self)
        top.geometry("250x250")
        top.title("Add Game")
        top.iconbitmap("sonny.ico")
        top.resizable(0, 0)
        top.rowconfigure(0, minsize=50, weight=0)
        top.columnconfigure(1, minsize=50, weight=1)
        tk.Label(top, text="Name").grid(column=0, row=0)
        tk.Label(top, text="Path").grid(column=0, row=1, padx=5)
        tk.Entry(top, textvariable=self.game_name_var).grid(column=1, row=0)
        tk.Label(top, textvariable=self.game_exe_var).grid(column=1, row=1)
        tk.Button(top, text='Submit', command=lambda:self.sumbit_game_manager(top, "add")).grid(column=0, row=5, columnspan=2)
    
    def about_section(self):        
        top = tk.Toplevel(self)
        top.title("About")
        top.iconbitmap("sonny.ico")
        top.geometry("250x250")
        top.resizable(0, 0)
        top.rowconfigure(0, minsize=50, weight=0)
        top.columnconfigure(1, minsize=50, weight=1)
        tk.Label(top, text="Sonny", font=(None, 30)).pack()
        tk.Label(top, text="Version 1.0.0").pack()

    def sumbit_game_manager(self, window, action):
        if action == "add":
            new_line = False
            with open("search_for_programs.txt", "r") as fp:
                lines = fp.readlines()
            for num, line in enumerate(lines):
                if "\n" in lines[num]: # Dont write \n
                    print("There is a new line char")
                    new_line = False
                else: # Do write \n
                    print("There is NOT a new line char")
                    new_line = True
            with open("search_for_programs.txt", "r") as fp:
                f = open("search_for_programs.txt", "a")
                if new_line == True:
                    f.write("\n")
                f.write(f"{self.game_name_var.get()},{self.game_path_var.get()},{self.game_exe_var.get()}")
                f.close()
            file_management.title_init(self.game_path_var.get() + "/" + self.game_exe_var.get())
            self.update_game_list()
            window.destroy()
        if action == "remove":
            with open("search_for_programs.txt", "r") as fp:
                lines = fp.readlines()
            with open("search_for_programs.txt", "w") as fp:
                for line in lines:
                    if "\n" in line.split(",")[2]:
                        if line.split(",")[2][0:-1] != self.game_exe_var.get():
                            fp.write(line)
                    else:
                        if line.split(",")[2] != self.game_exe_var.get():
                            fp.write(line)
            self.update_game_list()

    def update_game_list(self):
        if len(file_management.get_program_info()) == 0:
            lo_list = tk.Label(text="No Games Added", font=(None, 10))
            lo_list.grid(column=0, row=1, columnspan=3)
        else:
            def start_game():
                try:
                    os.chdir(self.game_path)
                    os.startfile(self.game_exe)
                    print(f"STARTING {self.game_exe}")
                except:
                    messagebox.showerror("Path not found", f"The path for {self.game_exe} is incorrect!")

            def _on_mousewheel(canvas, event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            def onFrameConfigure(canvas):
                '''Reset the scroll region to encompass the inner frame'''
                canvas.configure(scrollregion=canvas.bbox("all"))
            
            text_length = (720 // 25) - 3

            # VEIWER PANE FOR GAME INFORMATION ----------------------------------
            viewer_pane = tk.Frame(master=self, relief="flat", background=viewer_pane_background)
            viewer_pane.grid(row=1, column=1, sticky="nsew")
            viewer_pane.columnconfigure(0, weight=1)

            game_title_var = tk.StringVar()
            self.game_path = ""
            self.game_exe = ""
            game_playtime_var = tk.StringVar()
            game_timesplayed_var = tk.StringVar()
            game_lastplayed_var = tk.StringVar()
            game_title_var.set("Welcome to Sonny")
            tk.Label(viewer_pane, textvariable=game_title_var, font=(None, 18), background=viewer_pane_background, foreground=label_foreground).grid(row=0, column=0, columnspan=2, padx=5, pady=5)
            #tk.Label(viewer_pane, text="①②③", font=(None, 16), background=viewer_pane_background, foreground=label_foreground).grid(row=1, column=0, columnspan=2, sticky="we", padx=5)
            tk.Label(viewer_pane, text="Playtime", font=(None, 16), background=viewer_pane_background, foreground=label_foreground).grid(row=1, column=0, columnspan=2, sticky="w", padx=5)
            tk.Label(viewer_pane, textvariable=game_playtime_var, font=(None, 16), background=viewer_pane_background, foreground=label_foreground).grid(row=1, column=0, columnspan=2, sticky="e", padx=5)
            tk.Label(viewer_pane, text="Times Played", font=(None, 16), background=viewer_pane_background, foreground=label_foreground).grid(row=2, column=0, columnspan=2, sticky="w", padx=5)
            tk.Label(viewer_pane, textvariable=game_timesplayed_var, font=(None, 16), background=viewer_pane_background, foreground=label_foreground).grid(row=2, column=0, columnspan=2, sticky="e", padx=5)
            tk.Label(viewer_pane, text="Last Played", font=(None, 16), background=viewer_pane_background, foreground=label_foreground).grid(row=3, column=0, columnspan=2, sticky="w", padx=5)
            tk.Label(viewer_pane, textvariable=game_lastplayed_var, font=(None, 16), background=viewer_pane_background, foreground=label_foreground).grid(row=3, column=0, columnspan=2, sticky="e", padx=5)
            tk.Button(viewer_pane, text="Play", relief="flat", command=lambda:start_game(), background=app_background, foreground=label_foreground).grid(row=4, column=0, padx=5, pady=5, sticky="we")
            tk.Button(viewer_pane, text="Remove", command=lambda:self.sumbit_game_manager(self, "remove"), relief="flat", background=remove_button_background, foreground=label_foreground).grid(row=4, column=1, padx=5, pady=5)

            # UPDATE ACTION PANE ----------------------------------
            def list_action_pane_update(game):
                game_title_var.set(f"{game[0]}")
                self.game_path = game[1]
                self.game_exe = game[2]
                self.game_exe_var.set(self.game_exe)
                game_playtime_var.set(f"{time_format(file_management.TIME_INFO_DEFAULT[game[1]+'/'+game[2]][0])}")
                if file_management.TIME_INFO_DEFAULT[game[1]+'/'+game[2]][1] == 1:
                    game_timesplayed_var.set(f"{file_management.TIME_INFO_DEFAULT[game[1]+'/'+game[2]][1]} Time")
                else:
                    game_timesplayed_var.set(f"{file_management.TIME_INFO_DEFAULT[game[1]+'/'+game[2]][1]} Times")
                if file_management.TIME_INFO_DEFAULT[game[1]+'/'+game[2]][2] != "Never":
                    game_lastplayed_var.set(date_format(file_management.TIME_INFO_DEFAULT[game[1]+'/'+game[2]][2]))
                else:
                    game_lastplayed_var.set(file_management.TIME_INFO_DEFAULT[game[1]+'/'+game[2]][2])
            list_action_pane_update(file_management.get_program_info()[0])

            # ACTION PANE FOR GAME BUTTONS ----------------------------------
            action_pane = tk.Frame(master=self, relief="flat", background=action_pane_background)
            action_pane.grid(row=1, column=0, sticky="nsew")
            action_pane.grid_rowconfigure(0, weight=1)
            action_pane.grid_columnconfigure(0, weight=1)
            # Add a canvas in action_pane
            canvas = tk.Canvas(action_pane, background=action_pane_background, width=207)
            canvas.grid(row=0, column=0, sticky="news")
            # Linked scrollbar to the action_pane
            vsb = tk.Scrollbar(action_pane, orient="vertical", command=canvas.yview)
            canvas.configure(yscrollcommand=vsb.set)
            vsb.grid(row=0, column=1, sticky='ns')
            # Create a frame to contain the buttons
            button_frame = tk.Frame(canvas, background=action_pane_background)
            canvas.create_window((0, 0), window=button_frame, anchor='w')

            button_frame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))
            canvas.bind_all("<MouseWheel>", lambda event, canvas=canvas: _on_mousewheel(canvas, event))
            # Get all the Game names for buttons
            for game in file_management.get_program_info():
                if game != "":
                    if len(game[0]) >= text_length:
                        tk.Button(button_frame, text=f"{game[0][0:text_length]}...", font=("Consolas", 10), command=lambda game_name=game:list_action_pane_update(game_name), relief="flat", background=action_pane_background, foreground=label_foreground).grid(sticky="we")
                    else:
                        tk.Button(button_frame, text=f"{game[0][0:text_length]}", font=("Consolas", 10), command=lambda game_name=game:list_action_pane_update(game_name), relief="flat", background=action_pane_background, foreground=label_foreground).grid(sticky="we")
            
            # ROW AND COLUMN CONFIGS ----------------------------------
            self.rowconfigure(1, weight=1)
            self.columnconfigure(0)


if __name__ == "__main__":
    app = TkinterApp()
    try:
        _thread.start_new_thread(app.check_for_program, ())
    except Exception as E:
        print(f"Error: {E}")
    app.mainloop()