# For automation: Put these files in the Windows Start-up folder.
# Win+R then type "shell:startup" adn drag these files in there.
# ^^^ Actually dont do this?
import os, _thread, time, datetime, webbrowser, subprocess
# 
import tkinter as tk
from tkinter import messagebox
import tkinter.filedialog as tkf
import tkinter.ttk as ttk
import psutil
import file_management


time_passed_in_program = file_management.open_to('program_time_info.json')
settings_save = file_management.open_to('settings.json')

def time_format(seconds):
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    if hour == 0:
        return f"{int(minutes)}m {int(seconds)}s"
    else:
        return f"{int(hour)}h {int(minutes)}m {int(seconds)}s"

def ordinal_convert(num):
    ordinal = ["st", "nd", "rd"]
    if num % 10 == 1 and not num == 11 or num % 10 == 2 and not num == 12 or num % 10 == 3 and not num == 13:
        return f"{num}{ordinal[num%10-1]}"
    else:
        return f"{num}th"
    
def date_format(date):
    months = {"01": "January", "02": "Feburary", "03": "March", "04": "April", "05": "May", "06": "June", "07": "July", "08": "August", "09": "September", "10": "October", "11": "November", "12": "December"}
    format = date.split("-") # The dates looks like "YEAR-MONTH-DAY", so i peel it apart and stitch a new monster together.
    return f"{months[format[1]]} {ordinal_convert(int(format[2]))}, {format[0]}" # Gimme Gimme Gimme

def sort(nums, length):
    for j in range(length):
        iMin = j 
        for i in range(j + 1, length):
            if nums[i] > nums[iMin]:
                iMin = i
        (nums[j], nums[iMin]) = (nums[iMin], nums[j])

def check_app_running():
    for pid in psutil.pids():
        if psutil.Process(pid).name() == "SonnyApp.exe" and file_management.app_file_path == find_path("SonnyApp.exe"):
            return True

def find_path(name):
    for pid in psutil.pids():
        try:
            if psutil.Process(pid).name() == name:
                return psutil.Process(pid).exe().replace("\\", "/")
        except psutil.NoSuchProcess:
            print("find_path Error: NoSuchProcess")

class TkinterApp(tk.Tk):
    def __init__(self) -> None:
        if settings_save["app_theme"] == "light":
            self.label_foreground = "Black"
            self.label_background = "#ffffff"
            self.app_background = "#c9c9c9"
            self.action_pane_background = "#f5f5f5"
            self.viewer_pane_background = "#f5f5f5"
            self.viewer_pane_play = "#66c942" # Viewer Pane Play Button
            self.viewer_pane_remove = "#f06e62"
            self.viewer_pane_button_hover = "#e3e3e3"
        elif settings_save["app_theme"] == "melancholic":
            self.label_foreground = "#462d86"
            self.label_background = "#242b2e"
            self.app_background = "#9f95fc"
            self.action_pane_background = "#b8b8f2"
            self.viewer_pane_background = "#ccccff"
            self.viewer_pane_play = "#b1b1fa" # Viewer Pane Play Button
            self.viewer_pane_remove = "#b8b8f2"
            self.viewer_pane_button_hover = "#817bb8"
        elif settings_save["app_theme"] == "dark":
            self.label_foreground = "White"
            self.label_background = "#242b2e"
            self.app_background = "#292936"
            self.action_pane_background = "#3a394f"
            self.viewer_pane_background = "#46455c"
            self.viewer_pane_remove = "#ad0505"
            self.viewer_pane_play = "#147d25" # Viewer Pane Play Button
            self.viewer_pane_button_hover = "Black"
        elif settings_save["app_theme"] == "crimson":
            self.label_foreground = "White"
            self.label_background = "#242b2e"
            self.app_background = "#171717"
            self.action_pane_background = "#822121"
            self.viewer_pane_background = "#701616"
            self.viewer_pane_remove = "#380101"
            self.viewer_pane_play = "#147d25" # Viewer Pane Play Button
            self.viewer_pane_button_hover = "Black"
        else:
            messagebox.showerror("Sonny Error", '"app_theme" in "settings.json" is missing or incorrect')

        tk.Tk.__init__(self)
        self.title("Sonny")
        self.geometry('760x450')
        self.resizable(0, 0)
        self.iconbitmap("sonny.ico")
        self.configure(background=self.app_background)

        self.game_name_var = tk.StringVar()
        self.game_exe_var = tk.StringVar()
        self.game_path_var = tk.StringVar()
        self.current_game_index = 0
        self.update_game_list()
# py -m PyInstaller main.py --onefile --windowed --clean --add-data "*.py;app" --icon=sonnny.ico 
        # TOP MENUSSSSS
        menu = tk.Menu(self)
        menu_config = tk.Menu(menu, tearoff=False) # Configure menu for games
        menu_config.add_command(label='Add Game', command=lambda:self.open_dialog_findfile())
        menu_theme = tk.Menu(menu, tearoff=False) # Theme menu for the app
        menu_theme.add_command(label='Light', command=lambda:self.change_theme("light"))
        menu_theme.add_command(label='Melancholic', command=lambda:self.change_theme("melancholic"))
        menu_theme.add_separator()
        menu_theme.add_command(label='Dark', command=lambda:self.change_theme("dark"))
        menu_theme.add_command(label='Crimson', command=lambda:self.change_theme("crimson"))
        menu_help = tk.Menu(menu, tearoff=False) # Help menu for the app too :)
        menu_help.add_command(label='GitHub Page', command=lambda:webbrowser.open('https://github.com/miyomahkesis/sonny_program'))
        menu_help.add_command(label='About', command=lambda:messagebox.showinfo("About", "Sonny App\n- Version 1.1.0"))
        menu.add_cascade(label='Configure', menu=menu_config)
        menu.add_cascade(label='Theme', menu=menu_theme)
        menu.add_cascade(label='Help', menu=menu_help)
        self.config(menu=menu)

        # Scroll bar style!!!!
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Vertical.TScrollbar", gripcount=0, background=self.action_pane_background, darkcolor=self.app_background, lightcolor=self.action_pane_background, troughcolor=self.app_background, bordercolor=self.action_pane_background, arrowcolor=self.app_background)

        style.configure('action_pane.TButton', background=self.action_pane_background, foreground=self.label_foreground, relief="flat", justify="left", font=('Consolas', 10))
        style.map('action_pane.TButton', background=[('active', self.app_background)])
        style.configure('viewer_pane_play.TButton', background=self.viewer_pane_play, foreground=self.label_foreground, relief="flat", font=('Consolas Bold', 10))
        style.map('viewer_pane_play.TButton', background=[('active', self.app_background)])
        style.configure('viewer_pane.TButton', background=self.app_background, foreground=self.label_foreground, relief="flat", font=('Consolas Bold', 10))
        style.map('viewer_pane.TButton', background=[('active', self.viewer_pane_button_hover)])
        style.configure('viewer_pane_remove.TButton', background=self.viewer_pane_remove, foreground=self.label_foreground, relief="flat", font=('Consolas Bold', 10))
        style.map('viewer_pane_remove.TButton', background=[('active', self.app_background)])

        self.rowconfigure(0, minsize=75, weight=0)
        self.columnconfigure(1, minsize=50, weight=1)

        # For the top bar. Displays the current game information.
        self.current_game_time = tk.StringVar()
        self.current_game_state = tk.StringVar()
        self.current_game_state.set("MEOW")
        self.current_playtime = tk.Label(textvariable=self.current_game_state, font=("Consolas Bold", 15), background=self.app_background, foreground=self.label_foreground, justify="left")
        self.current_playtime.grid(column=0, row=0, columnspan=2, padx=15, sticky="w")
        self.current_playtime = tk.Label(textvariable=self.current_game_time, font=("Consolas", 15), background=self.app_background, foreground=self.label_foreground, justify="right")
        self.current_playtime.grid(column=0, row=0, columnspan=2, padx=15, sticky="e")

        self.is_program_opened = False # For when an application is open
        self.apps_currently_running = [] # I dont even think this is used at all.
        self.update()

    def change_theme(self, theme):
        settings_save["app_theme"] = theme # Change the app_theme setting to the theme you selected.
        file_management.write_to("settings.json", settings_save) # Save it.
        self.destroy()
        self.__init__()

    def check_for_program(self):
        # This is probably not the fastest way to do this,
        # but im simple and it works... so whatever!!
        while 1:
            for programs in psutil.process_iter(): # Cycles through the processes.
                for program_name in file_management.get_program_info(): # Cycles through the programs.
                    # If the program listed is found and running, it'll get the create time
                    # and the current time to find the differnce in both to get how long it
                    # has been running. After that it'll add it to the time info json.
                    while programs.name() == program_name[2] and (program_name[1] + f"/{program_name[2]}") == find_path(program_name[2]):
                        if (program_name[1] + f"/{program_name[2]}") not in self.apps_currently_running:
                            self.apps_currently_running.append((program_name[1] + f"/{program_name[2]}"))
                        else:
                            os.chdir(file_management.app_file_path)
                            self.is_program_opened = True # Tick it to true because an app opened.
                            time_passed_in_program[program_name[1] + f"/{program_name[2]}"] = time.time() - programs.create_time() # Get the time from open to now.
                            # Set the current game state to Playing and display the current time playing.
                            self.current_game_state.set(f'Playing\n"{program_name[0]}"')
                            self.current_game_time.set(f"{time_format(time.time() - programs.create_time())}")
                    if self.is_program_opened == True: # When the app is finally closed.
                        self.is_program_opened = False # Tick it back to close.
                        self.apps_currently_running.clear()
                        # Add all the game information to the respected space and perhaps give it a pat on the shoulder :D
                        file_management.TIME_INFO_DEFAULT[program_name[1] + "/" + program_name[2]][0] += time_passed_in_program[program_name[1] + f"/{program_name[2]}"]
                        file_management.TIME_INFO_DEFAULT[program_name[1] + "/" + program_name[2]][1] += 1
                        file_management.TIME_INFO_DEFAULT[program_name[1] + "/" + program_name[2]][2] = str(datetime.date.today())
                        file_management.write_to("program_time_info.json", file_management.TIME_INFO_DEFAULT)
                        # Set the current game state to Last Played and display all the information from that playthrough.
                        self.current_game_state.set(f'Last Played\n"{program_name[0]}"')
                        self.current_game_time.set(f"{time_format(file_management.TIME_INFO_DEFAULT[program_name[1] + '/' + program_name[2]][0])}\n{time_format(time.time() - programs.create_time())}")
                        self.update_game_list() # Update the game list for the new time.

    def open_dialog_findfile(self):
        game_found_in_storage = False # Check if the game you selected is in your storage or not
        os.chdir(file_management.app_file_path) # Change to the app file path for a reason i forgot but its important!!
        path = tkf.askopenfilename(filetypes=[("Executables", "*.exe")]) #  Only search for exe files.
        self.game_exe_var.set(path.split('/')[-1])
        self.game_path_var.set("/".join(path.split('/')[0:-1]))
        # This is for checking if the game is in storage or not
        for games in file_management.get_program_info():
            if self.game_path_var.get() == games[1]:
                print("Trying to add a game that was in storage already!!!!!!")
                game_found_in_storage = True
                break
        if path != "" and game_found_in_storage != True: # If the game is not in storage and you picked a correct path.
            self.add_game_func() # Then proceed my sweet prince.
        if game_found_in_storage == True:
            messagebox.showerror("Found in storage", f"You already have this path in the app!")

    def add_game_func(self):
        # This whole thing is for naming the app you selected.
        self.game_name_var.set("")
        top = tk.Frame(master=self, background=self.viewer_pane_background)
        top.grid(row=1, column=0, columnspan=2, sticky="nsew")
        top.columnconfigure(0, weight=1)
        top.rowconfigure(0, minsize=50, weight=0)
        top.columnconfigure(1, minsize=50, weight=1)
        tk.Label(top, text="Name", font=(None, 16), background=self.viewer_pane_background, foreground=self.label_foreground).grid(row=0, columnspan=2, padx=5)
        tk.Label(top, text="Path", font=(None, 16), background=self.viewer_pane_background, foreground=self.label_foreground).grid(row=2, columnspan=2, padx=5)
        tk.Entry(top, textvariable=self.game_name_var).grid(row=1, columnspan=2, padx=5)
        tk.Label(top, textvariable=self.game_path_var).grid(row=3, columnspan=2, padx=5)
        tk.Button(top, text='Submit', relief="flat", command=lambda:self.sumbit_game_manager(top, "add"), background=self.app_background, foreground=self.label_foreground, width=15).grid(row=4, columnspan=2, padx=5)

    def sumbit_game_manager(self, window, action, selected_game=[], new_name="", dev_name=""):
        if action == "add" and self.game_name_var.get() != "":
            file_management.APP_INFO_DEFAULT[self.game_name_var.get()] = {"path": self.game_path_var.get(), "exe": self.game_exe_var.get(), "dev": ""}
            file_management.title_init(self.game_path_var.get() + "/" + self.game_exe_var.get())
            file_management.write_to("program_app_info.json", file_management.APP_INFO_DEFAULT)
            self.update_game_list()
        if action == "remove":
            file_management.APP_INFO_DEFAULT.pop(self.game_name_var.get())
            if self.current_game_index != 0:
                self.current_game_index -= 1
            file_management.write_to("program_app_info.json", file_management.APP_INFO_DEFAULT)
            self.update_game_list()
        if action == "edit":
            print("edit", selected_game, new_name, dev_name)
            file_management.APP_INFO_DEFAULT[selected_game[2]]["dev"] = dev_name
            file_management.APP_INFO_DEFAULT[new_name] = file_management.APP_INFO_DEFAULT[selected_game[2]]
            if selected_game[2] != new_name:
                del file_management.APP_INFO_DEFAULT[selected_game[2]]
            file_management.write_to("program_app_info.json", file_management.APP_INFO_DEFAULT)
            self.update_game_list() # Update the game list for the new game.
            window.destroy()

    def edit_game_info(self, path, exe, name, dev): # Also another not fast method. :/
        new_name = tk.StringVar()
        new_name.set(name)
        dev_name = tk.StringVar()
        dev_name.set(dev)
        month_int = tk.IntVar()
        months=[1,2,3,4,5,6,7,8,9,10,11,12]# This is probably the most stinkyest thing EVER!!!!!!! 
        selected_game = [path, exe, name]
        print(path + "/" + exe, " | THis is top secret shhhhh", selected_game)
        viewer_pane = tk.Frame(master=self, background=self.viewer_pane_background)
        viewer_pane.grid(row=1, column=0, columnspan=2, sticky="nsew")
        viewer_pane.columnconfigure(0, weight=1)
        tk.Label(viewer_pane, text="Name", font=(None, 16), background=self.viewer_pane_background, foreground=self.label_foreground).grid(row=0, columnspan=2, padx=5)
        tk.Entry(viewer_pane, textvariable=new_name, width=50).grid(row=1, columnspan=2, padx=15, pady=5)
        tk.Label(viewer_pane, text="Developer", font=(None, 16), background=self.viewer_pane_background, foreground=self.label_foreground).grid(row=2, columnspan=2, padx=5)
        tk.Entry(viewer_pane, textvariable=dev_name, width=50).grid(row=3, columnspan=2, padx=15, pady=5)
        #tk.Label(viewer_pane, text="Release Date", font=(None, 16), background=self.viewer_pane_background, foreground=self.label_foreground).grid(row=4, columnspan=2, padx=5)
        #tk.Entry(viewer_pane, textvariable="", width=10).grid(row=5, column=0, padx=5, pady=5)
        #tk.OptionMenu(viewer_pane, month_int, *months).grid(row=5, column=1, padx=5, pady=5)
        tk.Button(viewer_pane, text="Save", relief="flat", command=lambda:self.sumbit_game_manager(viewer_pane, "edit", selected_game, new_name.get(), dev_name.get()), background=self.app_background, foreground=self.label_foreground, width=15).grid(row=6, columnspan=2, padx=5, pady=5)
        tk.Button(viewer_pane, text="Back", relief="flat", command=lambda:viewer_pane.destroy(), background=self.app_background, foreground=self.label_foreground, width=15).grid(row=7, columnspan=2, padx=5, pady=5)
    
    def update_game_list(self):
        if len(file_management.APP_INFO_DEFAULT) == 0:
            viewer_pane = tk.Frame(master=self, background=self.viewer_pane_background)
            viewer_pane.grid(row=1, column=0, columnspan=2, sticky="nsew")
            lo_list = tk.Label(viewer_pane, text="No Games Added", font=(None, 10))
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
                # Reset the scroll region to encompass the inner frame
                canvas.configure(scrollregion=canvas.bbox("all"))
            
            text_length = (720 // 25) - 3

            SORTED_APP_INFO = list(file_management.APP_INFO_DEFAULT.keys())
            SORTED_APP_INFO.sort()

            # VEIWER PANE FOR GAME INFORMATION ----------------------------------
            viewer_pane = tk.Frame(master=self, background=self.viewer_pane_background)
            viewer_pane.grid(row=1, column=1, sticky="nsew")
            viewer_pane.columnconfigure(0, weight=1)

            game_title_var = tk.StringVar()
            self.game_path = ""
            self.game_exe = ""
            game_developer = tk.StringVar()
            game_playtime_podium = tk.StringVar()
            game_timesplayed_podium = tk.StringVar()
            game_playtime_var = tk.StringVar()
            game_timesplayed_var = tk.StringVar()
            game_lastplayed_var = tk.StringVar()
            tk.Label(viewer_pane, textvariable=game_title_var, font=("Consolas Bold", 18), background=self.label_foreground, foreground=self.viewer_pane_background).grid(row=0, column=0, columnspan=2, sticky="we")
            tk.Label(viewer_pane, textvariable=game_developer, font=("Consolas Italic", 14), background=self.viewer_pane_background, foreground=self.label_foreground).grid(row=1, column=0, columnspan=2, sticky="we", padx=5)
            tk.Label(viewer_pane, textvariable=game_playtime_podium, font=("Consolas", 16), background=self.viewer_pane_background, foreground=self.label_foreground).grid(row=2, column=0, columnspan=2, sticky="we", padx=5)
            tk.Label(viewer_pane, textvariable=game_timesplayed_podium, font=("Consolas", 16), background=self.viewer_pane_background, foreground=self.label_foreground).grid(row=3, column=0, columnspan=2, sticky="we", padx=5)
            tk.Label(viewer_pane, text="Playtime", font=("Consolas", 16), background=self.viewer_pane_background, foreground=self.label_foreground).grid(row=2, column=0, columnspan=2, sticky="w", padx=5)
            tk.Label(viewer_pane, textvariable=game_playtime_var, font=("Consolas", 16), background=self.viewer_pane_background, foreground=self.label_foreground).grid(row=2, column=0, columnspan=2, sticky="e", padx=5)
            tk.Label(viewer_pane, text="Times Played", font=("Consolas", 16), background=self.viewer_pane_background, foreground=self.label_foreground).grid(row=3, column=0, columnspan=2, sticky="w", padx=5)
            tk.Label(viewer_pane, textvariable=game_timesplayed_var, font=("Consolas", 16), background=self.viewer_pane_background, foreground=self.label_foreground).grid(row=3, column=0, columnspan=2, sticky="e", padx=5)
            tk.Label(viewer_pane, text="Last Played", font=("Consolas", 16), background=self.viewer_pane_background, foreground=self.label_foreground).grid(row=4, column=0, columnspan=2, sticky="w", padx=5)
            tk.Label(viewer_pane, textvariable=game_lastplayed_var, font=("Consolas", 16), background=self.viewer_pane_background, foreground=self.label_foreground).grid(row=4, column=0, columnspan=2, sticky="e", padx=5)
            ttk.Button(viewer_pane, text="▶ Play Game", command=lambda:start_game(), style="viewer_pane_play.TButton").grid(row=5, column=0, padx=5, pady=5, sticky="we")
            ttk.Button(viewer_pane, text="Remove", command=lambda:self.sumbit_game_manager(self, "remove"), style="viewer_pane_remove.TButton").grid(row=5, column=1, padx=5, pady=5)
            ttk.Button(viewer_pane, text="Edit Game Info", command=lambda:self.edit_game_info(self.game_path, self.game_exe, game_title_var.get(), game_developer.get()), style="viewer_pane.TButton").grid(row=6, columnspan=2, padx=5, pady=5, sticky="we")
            # UPDATE ACTION PANE ----------------------------------
            def list_action_pane_update(game, index):
                self.current_game_index = index
                game_title_var.set(f"{game}")
                self.game_name_var.set(f"{game}")
                self.game_path = file_management.APP_INFO_DEFAULT[game]["path"]
                self.game_exe = file_management.APP_INFO_DEFAULT[game]["exe"]
                self.game_exe_var.set(self.game_exe)
                try:
                    game_developer.set(f"{file_management.APP_INFO_DEFAULT[game]['dev']}")
                except:
                    game_developer.set("")
                game_playtime_var.set(f"{time_format(file_management.TIME_INFO_DEFAULT[self.game_path+'/'+self.game_exe][0])}")
                game_timesplayed_var.set(f"{file_management.TIME_INFO_DEFAULT[self.game_path+'/'+self.game_exe][1]} Time" if file_management.TIME_INFO_DEFAULT[self.game_path+'/'+self.game_exe][1] == 1 else f"{file_management.TIME_INFO_DEFAULT[self.game_path+'/'+self.game_exe][1]} Times")
                if file_management.TIME_INFO_DEFAULT[self.game_path+'/'+self.game_exe][2] != "Never":
                    game_lastplayed_var.set(f"{date_format(file_management.TIME_INFO_DEFAULT[self.game_path+'/'+self.game_exe][2])}")
                else:
                    game_lastplayed_var.set(f"{file_management.TIME_INFO_DEFAULT[self.game_path+'/'+self.game_exe][2]}")

                TIMES_ = []
                for i in file_management.TIME_INFO_DEFAULT:
                    TIMES_.append(file_management.TIME_INFO_DEFAULT[i][0])
                sort(TIMES_, len(TIMES_))
                PLAYED_ = []
                for i in file_management.TIME_INFO_DEFAULT:
                    PLAYED_.append(file_management.TIME_INFO_DEFAULT[i][1])
                sort(PLAYED_, len(PLAYED_))
                PLAYTIME_PODIUM = {}
                TIMESPLAYED_PODIUM = {}
                for i in range(0, 3):
                    for j in file_management.TIME_INFO_DEFAULT:
                        if file_management.TIME_INFO_DEFAULT[j][0] == TIMES_[i]:
                            PLAYTIME_PODIUM[j] = i+1
                for i in range(0, 3):
                    for j in file_management.TIME_INFO_DEFAULT:
                        if file_management.TIME_INFO_DEFAULT[j][1] == PLAYED_[i]:
                            TIMESPLAYED_PODIUM[j] = i+1
                if self.game_path+'/'+self.game_exe in PLAYTIME_PODIUM:
                    game_playtime_podium.set(f"♛ {ordinal_convert(PLAYTIME_PODIUM[self.game_path+'/'+self.game_exe])}")
                else:
                    game_playtime_podium.set("")
                if self.game_path+'/'+self.game_exe in TIMESPLAYED_PODIUM:
                    game_timesplayed_podium.set(f"♛ {ordinal_convert(TIMESPLAYED_PODIUM[self.game_path+'/'+self.game_exe])}")
                else:
                    game_timesplayed_podium.set("")
            list_action_pane_update(SORTED_APP_INFO[self.current_game_index], self.current_game_index)

            # ACTION PANE FOR GAME BUTTONS ----------------------------------
            action_pane = tk.Frame(master=self, background=self.action_pane_background)
            action_pane.grid(row=1, column=0, sticky="nsew")
            action_pane.grid_rowconfigure(0, weight=1)
            action_pane.grid_columnconfigure(0, weight=1)
            # Add a canvas in action_pane
            canvas = tk.Canvas(action_pane, background=self.action_pane_background, width=222, highlightthickness=0)
            canvas.grid(row=0, column=0, sticky="news")
            # Linked scrollbar to the action_pane
            vsb = ttk.Scrollbar(action_pane, orient="vertical", command=canvas.yview)
            canvas.configure(yscrollcommand=vsb.set)
            if len(file_management.APP_INFO_DEFAULT) >= 13:
                vsb.grid(row=0, column=1, sticky='ns')
            # Create a frame to contain the buttons
            button_frame = tk.Frame(canvas, background=self.action_pane_background)
            canvas.create_window((0, 0), window=button_frame, anchor='w')

            button_frame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))
            if len(file_management.APP_INFO_DEFAULT) >= 13:
                canvas.bind_all("<MouseWheel>", lambda event, canvas=canvas: _on_mousewheel(canvas, event))
            # Get all the Game names for buttons
            for index, game in enumerate(SORTED_APP_INFO):
                ttk.Button(button_frame, text=f"{game}" if len(game) <= text_length else f"{game[0:text_length]}...", command=lambda game_name=game, index=index:list_action_pane_update(game_name, index), style="action_pane.TButton", width=30).grid(row=index+1, sticky="we")
                    #tk.Label(button_frame, text=f"{game[0]}" if len(game[0]) <= text_length else f"{game[0][0:text_length]}...", font=("Consolas", 10), background=self.action_pane_background, foreground=self.label_foreground).grid(row=index, sticky="w", padx=9)
            # ROW AND COLUMN CONFIGS ----------------------------------
            self.rowconfigure(1, weight=1)
            self.columnconfigure(0)



if __name__ == "__main__":
    app = TkinterApp()
    try:
        _thread.start_new_thread(app.check_for_program, ())
    except Exception as E:
        print(f"Thread Error: {E}")
    app.mainloop()