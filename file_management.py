import json, os

app_file_path = os.getcwd().replace("\\", "/")
print("THIS IS THE APP FILE PATH -> ", app_file_path)

# should've worked with json instead of txt but whatever
def get_program_info() -> list:
    program_name_list = []
    file = open(app_file_path + "\search_for_programs.txt", 'r')
    for program_title in file:
        if "\n" in program_title:
            program_name_list.append(program_title[0:(len(program_title) - 1)].split(","))
        else:
            program_name_list.append(program_title.split(","))
    return program_name_list

def open_to(file) -> dict:
    with open(file) as load:
        data = json.load(load)
    return data

def write_to(file, data) -> None:
    with open(file, "w") as save:
        json.dump(data, save, indent=4)

APP_INFO_DEFAULT = {}
if os.path.exists("search_for_programs.txt"):
    print("search for does exist.", end=" ")
    if os.path.exists("program_app_info.json"):
        print("no upgrade because ITS REAL!!!!!!!.")
        pass
    else:
        print("time to upgrade hahhahahaha.")
        with open("search_for_programs.txt", "r") as programs:
            for program in programs:
                APP_INFO_DEFAULT[program.split(",")[0]] = {"path": program.split(",")[1], "exe": program.split(",")[2], "dev": ""}
        write_to("program_app_info.json", APP_INFO_DEFAULT)
APP_INFO_DEFAULT = open_to("program_app_info.json")
print("I WANT EVERYONE TO KNOW THAT THIS IS APP INFO DEFAULT!!!!! -> ", APP_INFO_DEFAULT)

TIME_INFO_DEFAULT = {}
TIME_INFO_DEFAULT = open_to(app_file_path + '\program_time_info.json')
def title_init(game):
    TIME_INFO_DEFAULT[game] = [0, 0, "Never"]
for title in APP_INFO_DEFAULT:
    if f"{APP_INFO_DEFAULT[title]['path']}/{APP_INFO_DEFAULT[title]['exe']}" not in TIME_INFO_DEFAULT:
        title_init(APP_INFO_DEFAULT[title]["exe"])

title_init("hello")