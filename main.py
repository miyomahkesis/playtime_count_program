# For automation: Put these files in the Windows Start-up folder.
# Win+R then type "shell:startup" adn drag these files in there.
# ^^^ Actually dont do this?
import os, subprocess, _thread, datetime
import tkinter as tk
from tkinter import messagebox
import tkinter.filedialog as tkf
from psutil import process_iter
import time, file_management


time_passed_in_program = file_management.open_to('program_time_info.json')
settings_save = file_management.open_to('settings.json')
if settings_save["app_theme"] == "melancholic":
    app_background = "#8e82fe"
    viewer_pane_background = "#ccccff"
    action_pane_background = "#b8b8f2"
    remove_button_background = "#8d88c2"
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
        menu.add_cascade(label='Configure', menu=menu_config)
        menu.add_cascade(label='Theme', menu=menu_theme)
        self.config(menu=menu)

        self.rowconfigure(0, minsize=75, weight=0)
        self.columnconfigure(1, minsize=50, weight=1)

        self.current_game_time = tk.StringVar()
        self.current_game_state = tk.StringVar()
        self.current_game_state.set("Play a game to begin.")
        self.current_playtime = tk.Label(textvariable=self.current_game_state, font=(None, 15), background=app_background, foreground=label_foreground)
        self.current_playtime.grid(column=0, row=0, columnspan=2, padx=15, sticky="w")
        self.current_playtime = tk.Label(textvariable=self.current_game_time, font=(None, 15), background=app_background, foreground=label_foreground)
        self.current_playtime.grid(column=0, row=0, columnspan=2, padx=15, sticky="e")

        self.is_program_opened = False
        self.update()

    def change_theme(self, theme):
        settings_save["app_theme"] = theme
        file_management.write_to("settings.json", settings_save)
        messagebox.showinfo("Important", "You will need to restart the app for theme changes to take place.")

    def check_for_program(self):
        while 1:
            for programs in process_iter(): # Cycles through the processes
                for program_name in file_management.get_program_info(): # Cycles through the programs
                    # If the program listed is found and running, it'll get the create time
                    # and the current time to find the differnce in both to get how long it
                    # has been running. After that it'll add it to the time info json.
                    while programs.name() == program_name[2] and programs.is_running() == True:
                        os.chdir(file_management.app_file_path)
                        self.is_program_opened = True
                        time_passed_in_program[program_name[2]] = time.time() - programs.create_time()
                        self.current_game_state.set(f'Playing "{program_name[0]}"')
                        self.current_game_time.set(f"{time_format(time.time() - programs.create_time())}")
                    if self.is_program_opened == True:
                        self.is_program_opened = False
                        file_management.TIME_INFO_DEFAULT[program_name[2]][0] += time_passed_in_program[program_name[2]]
                        file_management.TIME_INFO_DEFAULT[program_name[2]][1] += 1
                        file_management.TIME_INFO_DEFAULT[program_name[2]][2] = str(datetime.date.today())
                        file_management.write_to("program_time_info.json", file_management.TIME_INFO_DEFAULT)
                        self.current_game_state.set(f'Last Played "{program_name[0]}"')
                        self.current_game_time.set(f"{time_format(file_management.TIME_INFO_DEFAULT[program_name[2]][0])}\n{time_format(time.time() - programs.create_time())}")

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
        top.rowconfigure(0, minsize=50, weight=0)
        top.columnconfigure(1, minsize=50, weight=1)
        tk.Label(top, text="Name").grid(column=0, row=0)
        tk.Label(top, text="Path").grid(column=0, row=1, padx=5)
        tk.Entry(top, textvariable=self.game_name_var).grid(column=1, row=0)
        tk.Label(top, textvariable=self.game_exe_var).grid(column=1, row=1)
        tk.Button(top, text='Submit', command=lambda:self.sumbit_game_manager(top, "add")).grid(column=0, row=5, columnspan=2)

    def sumbit_game_manager(self, window, action):
        if action == "add":
            f = open("search_for_programs.txt", "a")
            f.write("\n")
            f.write(f"{self.game_name_var.get()},{self.game_path_var.get()},{self.game_exe_var.get()}")
            f.close()
            file_management.title_init(self.game_exe_var.get())
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
                            print(line.split(",")[2] != self.game_exe_var.get(), line.split(",")[2])
                    else:
                        if line.split(",")[2] != self.game_exe_var.get():
                            fp.write(line)
                            print(line.split(",")[2] != self.game_exe_var.get(), line.split(",")[2])
            self.update_game_list()

    def update_game_list(self):
        if len(file_management.get_program_info()) == 0:
            lo_list = tk.Label(text="No Games Added", font=(None, 10))
            lo_list.grid(column=0, row=1, columnspan=3)
        else:
            text_length = (720 // 25) - 3
            
            action_pane = tk.Frame(master=self, relief="flat", background=action_pane_background, width=1000)
            viewer_pane = tk.Frame(master=self, relief="flat", background=viewer_pane_background)
            canvas = tk.Canvas(action_pane, height=10, background="Black")
            canvas.grid(row=0, column=0, sticky="news")
            button_frame = tk.Frame(canvas, relief=tk.RAISED, background=action_pane_background)
            button_frame.grid(row=0, column=0, sticky="nw")

            vsb = tk.Scrollbar(action_pane, orient="vertical", command=canvas.yview, background=app_background)
            #vsb.grid(row=0, column=1, sticky='ns')
            canvas.create_window((4, 4), window=button_frame)
            button_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.configure(yscrollcommand=vsb.set, scrollregion=canvas.bbox("all"))
            
            def start_game():
                try:
                    os.chdir(self.game_path)
                    os.startfile(self.game_exe)
                    print(f"STARTING {self.game_exe}")
                except:
                    messagebox.showerror("Path not found", f"The path for {self.game_exe} is incorrect!")

            game_title_var = tk.StringVar()
            self.game_path = ""
            self.game_exe = ""
            game_playtime_var = tk.StringVar()
            game_timesplayed_var = tk.StringVar()
            game_lastplayed_var = tk.StringVar()
            game_title_var.set("Welcome to Sonny")
            viewer_pane.columnconfigure(0, weight=1)
            tk.Label(viewer_pane, textvariable=game_title_var, font=(None, 18), background=viewer_pane_background, foreground=label_foreground).grid(row=0, column=0, columnspan=2, padx=5, pady=5)
            tk.Label(viewer_pane, text="Playtime", font=(None, 16), background=viewer_pane_background, foreground=label_foreground).grid(row=1, column=0, columnspan=2, sticky="w", padx=5)
            tk.Label(viewer_pane, textvariable=game_playtime_var, font=(None, 16), background=viewer_pane_background, foreground=label_foreground).grid(row=1, column=0, columnspan=2, sticky="e", padx=5)
            tk.Label(viewer_pane, text="Times Played", font=(None, 16), background=viewer_pane_background, foreground=label_foreground).grid(row=2, column=0, columnspan=2, sticky="w", padx=5)
            tk.Label(viewer_pane, textvariable=game_timesplayed_var, font=(None, 16), background=viewer_pane_background, foreground=label_foreground).grid(row=2, column=0, columnspan=2, sticky="e", padx=5)
            tk.Label(viewer_pane, text="Last Played", font=(None, 16), background=viewer_pane_background, foreground=label_foreground).grid(row=3, column=0, columnspan=2, sticky="w", padx=5)
            tk.Label(viewer_pane, textvariable=game_lastplayed_var, font=(None, 16), background=viewer_pane_background, foreground=label_foreground).grid(row=3, column=0, columnspan=2, sticky="e", padx=5)
            tk.Button(viewer_pane, text="Play", relief="flat", command=lambda:start_game(), background=app_background, foreground=label_foreground).grid(row=4, column=0, padx=5, pady=5, sticky="we")
            tk.Button(viewer_pane, text="Remove", command=lambda:self.sumbit_game_manager(self, "remove"), relief="flat", background=remove_button_background, foreground=label_foreground).grid(row=4, column=1, padx=5, pady=5)

            def list_action_pane_update(game):
                game_title_var.set(f"{game[0]}")
                self.game_path = game[1]
                self.game_exe = game[2]
                self.game_exe_var.set(self.game_exe)
                game_playtime_var.set(f"{time_format(file_management.TIME_INFO_DEFAULT[game[2]][0])}")
                game_timesplayed_var.set(f"{file_management.TIME_INFO_DEFAULT[game[2]][1]}")
                game_lastplayed_var.set(file_management.TIME_INFO_DEFAULT[game[2]][2])
            list_action_pane_update(file_management.get_program_info()[0])

            for game in file_management.get_program_info():
                if len(game[0]) >= text_length:
                    tk.Button(canvas, text=f"{game[0][0:text_length]}...", font=("Consolas", 10), command=lambda game_name=game:list_action_pane_update(game_name), relief="flat", background=action_pane_background, foreground=label_foreground).grid(sticky="we")
                else:
                    tk.Button(canvas, text=f"{game[0][0:text_length]}", font=("Consolas", 10), command=lambda game_name=game:list_action_pane_update(game_name), relief="flat", background=action_pane_background, foreground=label_foreground).grid(sticky="we")

            action_pane.grid(row=1, column=0, sticky="nsew")
            viewer_pane.grid(row=1, column=1, sticky="nsew")
            self.rowconfigure(1, weight=1)
            self.columnconfigure(0)


if __name__ == "__main__":
    app = TkinterApp()
    try:
        _thread.start_new_thread(app.check_for_program, ())
    except Exception as E:
        print(f"Error: {E}")
    app.mainloop()