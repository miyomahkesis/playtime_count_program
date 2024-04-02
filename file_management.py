import json, os, datetime

app_file_path = os.getcwd()
print("THIS IS THE APP FILE PATH -> ", app_file_path)

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

TIME_INFO_DEFAULT = {}
TIME_INFO_DEFAULT = open_to(app_file_path + '\program_time_info.json')
def title_init(game):
    TIME_INFO_DEFAULT[game] = [0, 0, "Never"]
for title in get_program_info():
    if title[2] not in TIME_INFO_DEFAULT:
        title_init(title[2])
print("\033[1m  TIME INFO FILE MANAAGE -> ", TIME_INFO_DEFAULT, "\033[0m")