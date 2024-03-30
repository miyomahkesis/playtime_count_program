# For automation: Put these files in the Windows Start-up folder.
# Win+R then type "shell:startup" adn drag these files in there.
# ^^^ Actually dont do this?
import tkinter as tk
import _thread
from psutil import process_iter
import time, file_management


# app_background = "#dfcbe4"
# viewer_pane_background = "#ccccff"
# label_foreground = "#462d86"
# label_background = "#242b2e"
app_background = "#373645"
viewer_pane_background = "#46455c"
label_foreground = "White"
label_background = "#242b2e"
time_passed_in_program = {}
time_passed_in_program = file_management.open_to('program_time_info.json', time_passed_in_program)

def time_format(seconds):
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
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

        self.game_list_type = "list"
        self.update_game_list(self.game_list_type)

        menu = tk.Menu(self)
        menu_configure = tk.Menu(menu, tearoff=False)
        menu_configure.add_command(label='Add Game', command=lambda:self.list_game_manager("add"))
        menu_style = tk.Menu(menu, tearoff=False)
        menu_style.add_command(label='Grid', command=lambda:self.set_game_list_type("grid"))
        menu_style.add_command(label='Viewer', command=lambda:self.set_game_list_type("list"))
        menu.add_cascade(label='Configure', menu=menu_configure)
        menu.add_cascade(label='Style', menu=menu_style)
        self.config(menu=menu)

        self.rowconfigure(0, minsize=75, weight=0)
        self.columnconfigure(1, minsize=50, weight=1)

        self.pvz_playtime = tk.Label(text="Welcome to Sonny!", font=(None, 15), background=app_background, foreground=label_foreground)
        self.pvz_playtime.grid(column=0, row=0, columnspan=2, padx=15)

        self.update()

    def set_game_list_type(self, key):
        self.game_list_type = key

    def check_for_program(self):
        is_program_opened = False
        while True:
            for programs in process_iter(): # Cycles through the processes
                for program_name in file_management.get_program_info(): # Cycles through the programs
                    # If the program listed is found and running, it'll get the create time
                    # and the current time to find the differnce in both to get how long it
                    # has been running. After that it'll add it to the time info json.
                    while programs.name() == program_name[2] and programs.is_running() == True:
                        is_program_opened = True
                        time_passed_in_program[program_name[2]] = time.time() - programs.create_time()
                        self.pvz_playtime["text"] = (f"{program_name[0]}\n{time_format(file_management.TIME_INFO_DEFAULT[program_name[2]])} - {time_format(time.time() - programs.create_time())}")
                    if is_program_opened == True:
                        print("Program not opened")
                        is_program_opened = False
                        file_management.TIME_INFO_DEFAULT[program_name[2]] += time_passed_in_program[program_name[2]]
                        file_management.write_to("program_time_info.json", file_management.TIME_INFO_DEFAULT)
                        self.pvz_playtime["text"] = (f"{program_name[0]}\n{time_format(file_management.TIME_INFO_DEFAULT[program_name[2]])}")
                        self.update_game_list(self.game_list_type)

    def list_game_manager(self, action):
        top = tk.Toplevel(self)
        top.geometry("250x250")
        top.rowconfigure(0, minsize=50, weight=0)
        top.columnconfigure(1, minsize=50, weight=1)
        if action == "add":
            self.game_exe_var.set("")
            game_name_title = tk.Label(top, text="Name")
            game_exe_title = tk.Label(top, text="Exe Name")
            game_name_title.grid(column=0, row=0)
            game_exe_title.grid(column=0, row=1)
            game_name = tk.Entry(top, textvariable=self.game_name_var)
            game_exe = tk.Entry(top, textvariable=self.game_exe_var)
            game_name.grid(column=1, row=0)
            game_exe.grid(column=1, row=1)
            sub_btn = tk.Button(top, text='Submit', command=lambda:self.sumbit_game_manager(top, action))
            sub_btn.grid(column=0, row=3, columnspan=2)

    def update_game_list(self, view):
        if len(file_management.get_program_info()) == 0:
            lo_list = tk.Label(text="No Games/Processes Added", font=(None, 10))
            lo_list.grid(column=0, row=1, columnspan=3)
        else:
            column_max = 3
            text_length = (720 // 25) - 3
            game_list_column = 0
            if view == "grid":
                for game in file_management.get_program_info():
                    try:
                        frame = tk.Frame(master=self, relief="flat", background=viewer_pane_background, borderwidth=1)
                        frame.grid(row=(game_list_column // column_max)+1, column=game_list_column % column_max, padx=5, pady=5, sticky="we")
                        self.columnconfigure(game_list_column % column_max, weight=1, minsize=75, uniform="column")
                        if len(game[0]) >= text_length:
                            tk.Label(master=frame, text=f"{game[0][0:text_length]}...\n{time_format(file_management.TIME_INFO_DEFAULT[game[2]])}", background=viewer_pane_background, foreground=label_foreground).pack(padx=5, pady=5)
                        else:
                            tk.Label(master=frame, text=f"{game[0][0:text_length]}\n{time_format(file_management.TIME_INFO_DEFAULT[game[2]])}", background=viewer_pane_background, foreground=label_foreground).pack(padx=5, pady=5)
                        game_list_column += 1
                    except:
                        pass
            elif view == "list":
                action_pane = tk.Frame(master=self, relief="flat", background=app_background)
                viewer_pane = tk.Frame(master=self, relief="flat", background=viewer_pane_background)
                canvas = tk.Canvas(action_pane, height=10, bg=app_background)
                canvas.grid(row=0, column=0, sticky="news")
                button_frame = tk.Frame(canvas, relief=tk.RAISED, background=app_background)
                button_frame.grid(row=0, column=0, sticky="nw")

                game_title_var = tk.StringVar()
                game_exe_var = tk.StringVar()
                game_playtime_var = tk.StringVar()
                game_title_var.set("Welcome to Sonny")
                tk.Label(viewer_pane, textvariable=game_title_var, font=(None, 18), background=viewer_pane_background, foreground=label_foreground).pack(padx=5, pady=5)
                tk.Label(viewer_pane, textvariable=game_exe_var, font=(None, 14), background=viewer_pane_background, foreground=label_foreground).pack(padx=5, pady=5)
                tk.Label(viewer_pane, textvariable=game_playtime_var, font=(None, 16), background=viewer_pane_background, foreground=label_foreground).pack(padx=5, pady=5)
                tk.Button(viewer_pane, text="Remove Game", command=lambda:self.sumbit_game_manager(self, "remove"), relief="flat", background=app_background, foreground=label_foreground).pack(padx=5, pady=5)

                vsb = tk.Scrollbar(action_pane, orient="vertical", command=canvas.yview)
                vsb.grid(row=0, column=1, sticky='ns')
                canvas.configure(yscrollcommand=vsb.set, scrollregion=canvas.bbox("all"))
                canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

                def list_action_pane_update(game):
                    game_title_var.set(f"{game[0]}")
                    self.game_exe_var.set(f"{game[2]}")
                    game_exe_var.set(f"{game[2]}")
                    game_playtime_var.set(f"Played {time_format(file_management.TIME_INFO_DEFAULT[game[2]])}")

                list_action_pane_update(file_management.get_program_info()[0])

                for game in file_management.get_program_info():
                    if len(game[0]) >= text_length:
                        tk.Button(button_frame, text=f"{game[0][0:text_length]}...", command=lambda game_name=game:list_action_pane_update(game_name), relief="flat", background=app_background, foreground=label_foreground).grid(sticky="w")
                    else:
                        tk.Button(button_frame, text=f"{game[0][0:text_length]}", command=lambda game_name=game:list_action_pane_update(game_name), relief="flat", background=app_background, foreground=label_foreground).grid(sticky="w")

                action_pane.grid(row=1, column=0, sticky="nsew")
                viewer_pane.grid(row=1, column=1, sticky="nsew")
                self.rowconfigure(1, weight=1)
                self.columnconfigure(0)

    
    def sumbit_game_manager(self, window, action):
        if action == "add":
            f = open("search_for_programs.txt", "a")
            f.write("\n")
            f.write(f"{self.game_name_var.get()},none,{self.game_exe_var.get()}")
            f.close()
            self.update_game_list(self.game_list_type)
            window.destroy()
        if action == "remove":
            with open("search_for_programs.txt", "r") as fp:
                lines = fp.readlines()
            with open("search_for_programs.txt", "w") as fp:
                for line in lines:
                    if "\n" in line.split(",")[2]:
                        if line.split(",")[2][0:-1] != self.game_exe_var.get():
                            fp.write(line)
                            print(line.split(",")[2], line.split(",")[2] != self.game_exe_var.get())
                    else:
                        if line.split(",")[2] != self.game_exe_var.get():
                            fp.write(line)
                            print(line.split(",")[2], line.split(",")[2] != self.game_exe_var.get())
            self.update_game_list(self.game_list_type)

if __name__ == "__main__":
    app = TkinterApp()
    try:
        _thread.start_new_thread(app.check_for_program, ())
    except Exception as E:
        print(f"Error: {E}")

    app.mainloop()