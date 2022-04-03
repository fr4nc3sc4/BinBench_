import json
import os
import argparse
from multiprocessing import Pool
import random

# k = number of similar functions to be picked randomly
# k-1 --> functions to be inserted in search_base file
# 1 --> function to be inserted in query file

k = 21
datapoints_query = 10000


def dump_json(lst, search_b, qry_blind, qry_secret):
    global k
    global relpath_uniqueid

    # datapoint IDs
    dtpoint_blind_secret = 1

    # map query function (key) to search base functions (value)
    similar_dict = {}

    query_blind = open(qry_blind, "w+")
    query_secret = open(qry_secret, "w+")
    src_base = open(search_b, "w+")

    try:
        for i in lst:
            # check if the total number of datapoints has been reached
            if len(similar_dict) == datapoints_query:
                break
            # remove empty entries
            elif len(i) > 0:
                similar_dict[i[0]] = i[1:k]

        # Indices needed to shuffle datapoints:
        tot_searchbase_entries = (len(similar_dict)) * (k - 1)
        dtpoint_searchbase = list(range(1, tot_searchbase_entries + 1))
        similar_dict_indx = list(similar_dict.keys())
        random.shuffle(similar_dict_indx)

        tempsearchb = {}

        for key in similar_dict_indx:
            uniqueid_blind = relpath_uniqueid[key]
            blind_path = f'{uniqueid_blind}.json'

            blind = {'datapoint_id': dtpoint_blind_secret, 'file_id': blind_path, 'similars': []}
            query_blind.write(json.dumps(blind))
            query_blind.write('\n')

            searchbase_list = []
            for e in similar_dict.get(key):
                # get id and path of the similar function
                uniqueid_searchbase = relpath_uniqueid[e]
                srcbase_path = f'{uniqueid_searchbase}.json'

                # pick a random index for searchbase entry
                rnd_index = random.choice(dtpoint_searchbase)
                dtpoint_searchbase.remove(rnd_index)

                searchb = {'datapoint_id': rnd_index, 'file_id': srcbase_path}
                tempsearchb[rnd_index] = searchb
                # Given the query, save all similar id of functions in searchbase
                searchbase_list.append(srcbase_path)

            secret = {'datapoint_id': dtpoint_blind_secret, 'file_id': blind_path, 'similars': searchbase_list}
            query_secret.write(json.dumps(secret))
            query_secret.write('\n')

            dtpoint_blind_secret += 1

        # sort searchbase datapoints by datapoint_id, then dump on jsonl
        tempsearchb = dict(sorted(tempsearchb.items()))
        for value in tempsearchb.values():
            src_base.write(json.dumps(value))
            src_base.write('\n')
        query_blind.close()
        query_secret.close()
        src_base.close()
    except Exception as e:
        print("error in dump_json(): " + str(e))


def get_k_similars(similarity_list):
    # return k similar functions
    global k

    ret = []
    # filter out functions with less than k similars
    if len(similarity_list) >= k:
        while len(ret) < k:
            rnd = random.choice(similarity_list)
            if rnd not in ret:
                ret.append(rnd)
    return ret


if __name__ == '__main__':
    global relpath_uniqueid

    parser = argparse.ArgumentParser(description='Parsing arguments for binary similarity')

    parser.add_argument("nProc", type=int, help='number of processes to be used')
    args = parser.parse_args()
    n_processes = args.nProc

    # load json file containing similarity relationships

    similarity_path = f'{os.getcwd()}/similarity.json'
    open_json = open(similarity_path, "r")
    similarity_list = json.load(open_json)

    p = Pool(processes=n_processes)

    mappool = p.map(get_k_similars, similarity_list.values())

    p.close()
    p.join()

    # load json file containing index: uniqueid - relative path of each json file
    index_path = f'{os.getcwd()}/path-uniqueid.json'

    open_json = open(index_path, "r")
    relpath_uniqueid = json.load(open_json)

    output_searchbase = f'{os.getcwd()}/function-search-searchbase-test.jsonl'  # function search base
    output_blind = f'{os.getcwd()}/function-search-blind.jsonl'  # function search query blind
    output_secret = f'{os.getcwd()}/function-search-secret.jsonl'  # function search query secret
    dump_json(mappool, output_searchbase, output_blind, output_secret)  # clean + dump on JSON files
