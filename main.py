# For automation: Put these files in the Windows Start-up folder.
# Win+R then type "shell:startup" adn drag these files in there.
import tkinter as tk
import _thread
from psutil import process_iter
import time, file_management


tk_root = tk.Tk()
tk_root.title("Sonny")
tk_root.geometry('420x300')
time_passed_in_program = {}
time_passed_in_program = file_management.open_to('program_time_info.json', time_passed_in_program)

def time_format(seconds):
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return f"{int(hour)}h {int(minutes)}m {int(seconds)}s"

def check_for_program():
    global time_passed_in_program
    global pvz_playtime
    is_program_opened = False
    while True:
        update_game_list()
        for programs in process_iter(): # Cycles through the processes
            for program_name in file_management.get_program_info(): # Cycles through the programs
                # If the program listed is found and running, it'll get the create time
                # and the current time to find the differnce in both to get how long it
                # has been running. After that it'll add it to the time info json.
                while programs.name() == program_name[2] and programs.is_running() == True:
                    is_program_opened = True
                    time_passed_in_program[program_name[2]] = time.time() - programs.create_time()
                    pvz_playtime["text"] = (f"{program_name[0]}\n{time_format(file_management.TIME_INFO_DEFAULT[program_name[2]])} - {time_format(time.time() - programs.create_time())}")
                if is_program_opened == True:
                    print("Program not opened")
                    is_program_opened = False
                    file_management.TIME_INFO_DEFAULT[program_name[2]] += time_passed_in_program[program_name[2]]
                    file_management.write_to("program_time_info.json", file_management.TIME_INFO_DEFAULT)
                    pvz_playtime["text"] = (f"{program_name[0]}\n{time_format(file_management.TIME_INFO_DEFAULT[program_name[2]])}")

game_name_var = tk.StringVar()
game_exe_var = tk.StringVar()
def sumbit_game_manager(window, action):
    if action == "add":
        f = open("search_for_programs.txt", "a")
        f.write("\n")
        f.write(f"{game_name_var.get()},none,{game_exe_var.get()}")
        f.close()
        update_game_list()
        window.destroy()
    if action == "remove":
        with open("search_for_programs.txt", "r") as fp:
            lines = fp.readlines()
        with open("search_for_programs.txt", "w") as fp:
            for line in lines:
                if line.split(",")[2] != game_exe_var.get():
                    fp.write(line)
        update_game_list()
        window.destroy()

def list_game_manager(action):
    top = tk.Toplevel(tk_root)
    top.geometry("250x250")
    top.rowconfigure(0, minsize=50, weight=0)
    top.columnconfigure(1, minsize=50, weight=1)
    if action == "add":
        game_name_title = tk.Label(top, text="Name")
        game_exe_title = tk.Label(top, text="Exe Name")
        game_name_title.grid(column=0, row=0)
        game_exe_title.grid(column=0, row=1)
        game_name = tk.Entry(top, textvariable=game_name_var)
        game_exe = tk.Entry(top, textvariable=game_exe_var)
        game_name.grid(column=1, row=0)
        game_exe.grid(column=1, row=1)
        sub_btn = tk.Button(top, text='Submit', command=lambda:sumbit_game_manager(top, action))
        sub_btn.grid(column=0, row=3, columnspan=2)
    if action == "remove":
        game_exe_title = tk.Label(top, text="Exe Name")
        game_exe_title.grid(column=0, row=0)
        game_exe = tk.Entry(top, textvariable=game_exe_var)
        game_exe.grid(column=1, row=0)
        sub_btn = tk.Button(top, text='Submit', command=lambda:sumbit_game_manager(top, action))
        sub_btn.grid(column=0, row=1, columnspan=2)

def help_about():
    top= tk.Toplevel(tk_root)
    top.geometry("250x250")
    top.title("Sonny")
    tk.Label(top, text="Sonny", font=(None, 20)).place(x=10,y=10)


menu = tk.Menu(tk_root)
menu_configure = tk.Menu(menu, tearoff=False)
menu_configure.add_command(label='Add Game', command=lambda:list_game_manager("add"))
menu_configure.add_command(label='Remove Game', command=lambda:list_game_manager("remove"))
menu_help = tk.Menu(menu, tearoff=False)
menu_help.add_command(label='Github')
menu_help.add_command(label='About', command=lambda:help_about())
menu.add_cascade(label='Configure', menu=menu_configure)
menu.add_cascade(label='Help', menu=menu_help)
tk_root.config(menu=menu)

tk_root.rowconfigure(0, minsize=75, weight=0)
tk_root.columnconfigure(1, minsize=50, weight=1)

pvz_string_var = "Open App!!!"
pvz_playtime = tk.Label(text=pvz_string_var, font=(None, 15))
pvz_playtime.grid(column=0, row=0, columnspan=3)


def update_game_list():
    if len(file_management.TIME_INFO_DEFAULT) <= 0:
        lo_list = tk.Label(text="No List", font=(None, 10))
        lo_list.grid(column=0, row=1, columnspan=3)
    else:
        row_i = 0
        for program_name in file_management.get_program_info():
            row_i += 1
            program_title = tk.Label(text=f"{program_name[0]}")
            program_author = tk.Label(text=f"{program_name[2]}")
            try:
                program_time = tk.Label(text=f"{time_format(file_management.TIME_INFO_DEFAULT[program_name[2]])}")
            except:
                program_time = tk.Label(text="No Time")
            program_title.grid(column=0, row=row_i, padx=10)
            #program_author.grid(column=1, row=row_i, padx=10)
            program_time.grid(column=2, row=row_i, padx=10)
update_game_list()

if __name__ == "__main__":
    _thread.start_new_thread(check_for_program, ())
    tk_root.mainloop()