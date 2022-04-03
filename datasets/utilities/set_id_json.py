from multiprocessing import Pool, Value
import json
import argparse
import os
import random
from pathlib import Path

counter = None


def init(args):
    global counter
    counter = args


def set_unique_id(filepath):
    global counter
    # atomic increment of the counter:
    with counter.get_lock():
        counter.value += 1
        local_counter = counter.value

    # write id in json file
    try:
        open_json = open(filepath, "r")
        json_data = json.load(open_json)
        open_json.close()

        json_data["id"] = local_counter

        json_file = open(filepath, "w+")
        json_file.write(json.dumps(json_data))
        json_file.close()

    except Exception as e:
        print("Error in SET_ID_JSON.PY / set_unique_id(). Error: " + str(e))
    return None


def list_files(work_folder):
    # list paths of all existing json functions (and return them in random order)

    files = []
    try:
        for file_path in Path(work_folder).rglob('*.json'):
            files.append(str(file_path))
    except Exception as e:
        print("Error in SET_ID_JSON.PY / list_files(). Error: " + str(e) + ", file:" + str(file_path))
    random.shuffle(files)
    return files


def similarity(files):
    # return a dictionary that groups similar functions
    # (= functions with same name and package, but different compiler and compilation level)
    # Entry:
    # (key: project_name-function_name, value: list of paths of similar functions)
    print("Creating similarity file...")
    similarity_dict = {}
    try:
        for file in files:
            project_name = file.split("/")[-4]
            function_name = file.split("/")[-1].split(".json")[0]

            rel_path = f'/{file.split("/")[-4]}/{file.split("/")[-3]}/{file.split("/")[-2]}/{file.split("/")[-1]}'

            temp_key = f"{project_name}-{function_name}"

            if temp_key in similarity_dict:
                similarity_dict[temp_key].append(rel_path)
            else:
                similarity_dict[temp_key] = [rel_path]
    except Exception as e:
        print("Error in SET_ID_JSON.PY / similarity(...): Error:" + str(e))

    json_file = open(f'{os.getcwd()}/similarity.json', "w+")
    json_file.write(json.dumps(similarity_dict, indent=1))
    json_file.close()
    return similarity_dict


def uniqueidpool(files):
    #  [set unique id of functions]
    print("set unique id...")

    # pool creation with shared counter:
    counter = Value('i', 0)

    p = Pool(initializer=init, initargs=(counter,), processes=nProcesses)
    i = p.map_async(set_unique_id, files, )
    i.wait()
    p.close()
    p.join()


if __name__ == '__main__':

    # all : set uniqueid and produce similarity.json
    #
    # uniqueid : unique ID of each json file
    #
    #
    # similarity : produce only similarity.json

    parser = argparse.ArgumentParser(description='parser work directory')

    parser.add_argument("workdir", type=str, help='Folder of json files')
    parser.add_argument("idType", type=str, help='Choose: all / uniqueid / similarity')
    parser.add_argument("procNumber", type=int, help='Number of processes to be used')

    args = parser.parse_args()

    nProcesses = args.procNumber
    id = args.idType

    file_list = list_files(args.workdir)  # get list of all json functions

    if id.lower() == 'all':
        uniqueidpool(file_list)
        similarity(file_list)
    elif id.lower() == 'uniqueid':
        uniqueidpool(file_list)
    elif id.lower() == 'similarity':
        similarity(file_list)
    else:
        print("Please insert correct id to be set.")
