# For automation: Put these files in the Windows Start-up folder.
# Win+R then type "shell:startup" adn drag these files in there.

from psutil import process_iter
import time, file_management


def time_format(seconds):
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return f"{int(hour)}h {int(minutes)}m {int(seconds)}s"

time_passed_in_program = {}
time_passed_in_program = file_management.open_to('program_time_info.json', time_passed_in_program)
is_program_opened = False

while 1:
    for programs in process_iter(): # Cycles through the processes
        for program_name in file_management.get_program_info(): # Cycles through the programs
            # If the program listed is found and running, it'll get the create time
            # and the current time to find the differnce in both to get how long it
            # has been running. After that it'll add it to the time info json.
            while programs.name() == program_name[2] and programs.is_running() == True:
                is_program_opened = True
                time_passed_in_program[program_name[2]] = time.time() - programs.create_time()
                #print(f"{time.ctime(programs.create_time())} | {program_name[2]}") # program_time_info.json
                #print(f"{time.ctime(time.time())}\t{time_passed_in_program}")
                print(f"{time_format(time_passed_in_program[program_name[2]])} -> {time.time() - programs.create_time()}, {file_management.TIME_INFO_DEFAULT[program_name[2]]}")
            if is_program_opened == True:
                print("Program not opened")
                is_program_opened = False
                file_management.TIME_INFO_DEFAULT[program_name[2]] += time_passed_in_program[program_name[2]]
                file_management.write_to("program_time_info.json", file_management.TIME_INFO_DEFAULT)