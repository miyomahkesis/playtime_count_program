import json

def get_program_info() -> list:
    program_name_list = []
    file = open("search_for_programs.txt", 'r')
    for program_title in file:
        if "\n" in program_title:
            program_name_list.append(program_title[0:(len(program_title) - 1)].split(","))
        else:
            program_name_list.append(program_title.split(","))
    return program_name_list

def open_to(file, data) -> dict:
    with open(file) as load:
        data = json.load(load)
    return data

def write_to(file, data) -> None:
    with open(file, "w") as save:
        json.dump(data, save, indent=4)

TIME_INFO_DEFAULT = {}
TIME_INFO_DEFAULT = open_to('program_time_info.json', TIME_INFO_DEFAULT)
for title in get_program_info():
    if title[2] not in TIME_INFO_DEFAULT:
        TIME_INFO_DEFAULT[title[2]] = 0
print(TIME_INFO_DEFAULT)