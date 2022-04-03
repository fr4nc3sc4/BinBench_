import json
import os
from set_id_json import list_files
import argparse
from multiprocessing import Pool


# MAP UNIQUE IDs TO RESPECTIVE PATHS

def dump_json(dictionary, jsonfilepath):
    jsonFile = open(jsonfilepath, "w+")
    ret = {}
    for entry in dictionary:
        # construct entry for json index file
        key = (list(entry.keys()))[0]
        value = entry[key]
        ret[key] = value
    json.dump(ret, jsonFile, indent=1)


def uniqueid_file(path):
    entry = {}

    try:
        open_json = open(path, "r")
        json_data = json.load(open_json)
        if 'id' in json_data:
            temp = path.split("/")[-4:]
            rel_path = f'/{temp[0]}/{temp[1]}/{temp[2]}/{temp[3]}'

            id = json_data['id']

            entry[rel_path] = id
        open_json.close()
        return entry
    except Exception as e:
        print('Error in json_index.py / uniqueid_file(): ' + str(e) + ', file: ' + str(path))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parsing JSON arguments...')

    parser.add_argument("workdir", type=str, help='Folder of json files')
    parser.add_argument("nProc", type=int, help='Number of processes used')

    args = parser.parse_args()

    lst = list_files(args.workdir)  # get list of all json functions

    output_path = f'{os.getcwd()}/path-uniqueid.json'
    print(f'Writing path-uniqueid file...')
    p = Pool(processes=args.nProc)

    mappool = p.map(uniqueid_file, lst)

    p.close()
    p.join()

    dump_json(mappool, output_path)