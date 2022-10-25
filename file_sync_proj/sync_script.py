import sys
import os
import shutil
import datetime, time


hyph_10n = (10*"-")+"\n"
at_15n = (15*"@")+"\n"


def write_file(f_path, f_cont):
    with open(f_path, "w") as f:
        f.write(f_cont)
    return


def write_add_file(f_path, f_cont):
    with open(f_path, "a") as f:
        f.write(f_cont)
    return


def check_input(cmd_line_inp):
    if len(cmd_line_inp) != 5:
        print("Invalid number of arguments\nargs: <sourcedir path> <target dir path> <sync interval in min> <log file path>\n")
        quit()
    
    src_dir_path = cmd_line_inp[1]
    trg_dir_path = cmd_line_inp[2]
    sync_interval = cmd_line_inp[3]
    log_f = cmd_line_inp[4]
    
    # CHECK IF COMMAND LINE INPUT CORRECT
    if False in [os.path.isdir(src_dir_path),
                os.path.isdir(trg_dir_path),
                sync_interval.isdigit(),
                os.path.isfile(log_f)]:
        print("Invalid command line arguments.")
        quit()
    return src_dir_path, trg_dir_path, int(sync_interval)*60, log_f


def is_file_time_info_less_sync_interval(file_stat_info, time_now):
    return (time_now - datetime.datetime.fromtimestamp(file_stat_info)).seconds < SYNC_INTERVAL


def get_touched_f_li(time_now):
    f_created_li = []
    f_modified_li = []
    f_accessed_li = []
    f_missing_li = []
    f_removed_li = []

    # removing invisible file created during copying
    if os.path.exists(os.path.join(SOURCE_DIR, ".DS_Store")):
        os.remove(os.path.join(SOURCE_DIR, ".DS_Store"))
    if os.path.exists(os.path.join(TARGET_DIR, ".DS_Store")):
        os.remove(os.path.join(TARGET_DIR, ".DS_Store"))
    
    source_f_li = [sf for sf in sorted(os.listdir(SOURCE_DIR))]
    target_f_li = [tf for tf in sorted(os.listdir(TARGET_DIR))]
    
    # GET FILES THAT WERE CREATED / MODIFIED / ACCESSED MISSING WITHIN LAST SYNC INTERVAL
    for src_f in source_f_li:
        src_f_stats = os.stat(os.path.join(SOURCE_DIR, src_f))

        if is_file_time_info_less_sync_interval(src_f_stats.st_birthtime, time_now):
            f_created_li.append(src_f)
        elif is_file_time_info_less_sync_interval(src_f_stats.st_mtime, time_now):
            f_modified_li.append(src_f)
        elif is_file_time_info_less_sync_interval(src_f_stats.st_atime, time_now):
            f_accessed_li.append(src_f)
        elif src_f not in target_f_li:
            f_missing_li.append(src_f)
    
    # GET FILES THAT WERE REMOVED WITHIN LAST SYNC INTERVAL
    for target_f in target_f_li:
        if target_f not in source_f_li:
            f_removed_li.append(target_f)
    
    return [f_created_li, f_modified_li, f_accessed_li, f_missing_li, f_removed_li]


def update_target_dir_log_f(touched_f_li, F_STATE_LI, time_now):
    # COPY FILES THAT WERE CREATED / MODIFIED / ACCESSED / MISSING FROM SOURCE TO TARGET
    log_f_cont = f"SYNC AT {time_now}\n{hyph_10n}"

    f_to_copy_li = touched_f_li[:-1]
    for f_to_cp_li_idx, f_to_cp_li in enumerate(f_to_copy_li):
        if f_to_cp_li != []:
            for f_to_cp in f_to_cp_li:
                shutil.copy2(os.path.join(SOURCE_DIR, f_to_cp), os.path.join(TARGET_DIR, f_to_cp))
            f_to_cp_str = "\n".join(f_to_cp_li)
            log_f_cont += f"\nFILES {F_STATE_LI[f_to_cp_li_idx]}\n{hyph_10n}{f_to_cp_str}\n"
    
    # REMOVE FILES FROM TARGET THAT ARE NOT PRESENT IN SOURCE
    f_removed_li = touched_f_li[-1]
    if f_removed_li != []:
        for f_to_rm in f_removed_li:
            os.remove(os.path.join(TARGET_DIR, f_to_rm))
        f_removed_str = '\n'.join(f_removed_li)
        log_f_cont += f"\nFILES {F_STATE_LI[-1]}\n{hyph_10n}{f_removed_str}\n"
    
    # LOG INFO INTO SYNC_LOG FILE
    log_f_cont = f"\n{at_15n}\n{log_f_cont}\n{at_15n}\n"
    print(log_f_cont)
    write_add_file(LOG_F, log_f_cont)
    return


def main():
    while True:
        time_now = datetime.datetime.now()
        touched_f_li = get_touched_f_li(time_now)
        if touched_f_li != [[], [], [], [], []]:
            update_target_dir_log_f(touched_f_li, F_STATE_LI, time_now)
        time.sleep(SYNC_INTERVAL)


if __name__ == "__main__":
    F_STATE_LI = ["CREATED", "MODIFIED", "ACCESSED", "MISSING", "REMOVED"]
    SOURCE_DIR, TARGET_DIR, SYNC_INTERVAL, LOG_F = check_input(sys.argv)
    write_file(LOG_F, "")
    main()



