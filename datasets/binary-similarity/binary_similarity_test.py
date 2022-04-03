import json
import os
import argparse
from multiprocessing import Pool
from random import shuffle, choice
from math import factorial

k = 3


def dump_json(lst, blind, secret):
    # shuffle all tuples in lst:
    temp = []
    datapoint_id = 1
    # convert in JSONL format
    try:
        json_blind = open(blind, "w+")
        json_secret = open(secret, "w+")
        for i in lst:
            # remove empty entries
            if len(i) > 0:
                for entry in i:
                    temp.append(entry)
        shuffle(temp)
        for entry in temp:
            # blind entry
            b = {'datapoint_id': datapoint_id, 'file_id': [entry[0], entry[1]], 'similarity': []}
            json_blind.write(json.dumps(b))
            json_blind.write('\n')
            # secret entry
            s = {'datapoint_id': datapoint_id, 'file_id': [entry[0], entry[1]], 'similarity': entry[2]}
            json_secret.write(json.dumps(s))
            json_secret.write('\n')

            datapoint_id += 1
        json_secret.close()
        json_blind.close()
    except Exception as e:
        print("error in dump_json(lst, path): " + str(e))


def rnd_index(n_indices, actual_index):
    # rnd_index() returns n_indices random indices from index_list.
    # Indices are unique and different from actual_index

    ret = []

    while len(ret) < n_indices:
        rnd = choice(index_list)
        if rnd != actual_index and rnd not in ret:
            ret.append(rnd)
    return ret


def tuples(indx):
    global uniqueid_relpath
    dct = []  # returned list

    similar = similarity_list[indx]  # list of similar functions given their index

    length = len(similar)

    # tot_of_couples = N!/n!(N-n)!
    # N = length
    # n = 2 --> 2! = 2
    if length > 1:
        tot_of_couples = (factorial(length)) / (2 * (factorial(length - 2)))

        try:

            if tot_of_couples < k:
                n_iterations = tot_of_couples
            else:
                n_iterations = k

            while len(dct) < n_iterations:
                rnd1 = f'{uniqueid_relpath[choice(similar)]}.json'
                rnd2 = f'{uniqueid_relpath[choice(similar)]}.json'
                if rnd1 != rnd2:
                    if (rnd1, rnd2, '+1') not in dct and (rnd2, rnd1, '+1') not in dct:
                        # AVOID DUPLICATE TUPLES:
                        # (a,b, label) tuple is added only if
                        # (a,b,label) AND (b,a, label) are not already in dct
                        tple = (rnd1, rnd2, '+1')
                        dct.append(tple)
            # not similar functions
            tmpindex = rnd_index(n_iterations, indx)
            for i in tmpindex:
                dissimilar = similarity_list[i]  # not similar functions

                # randomly pick an entry from similar functions and another from dissimilar functions
                rnd1 = f'{uniqueid_relpath[choice(similar)]}.json'
                rnd2 = f'{uniqueid_relpath[choice(dissimilar)]}.json'
                tple = (rnd1, rnd2, '-1')
                dct.append(tple)
        except Exception as e:
            print("error in tuples(indx) :" + str(e))
    return dct


if __name__ == '__main__':
    global similarity_list
    global index_list
    global uniqueid_relpath

    parser = argparse.ArgumentParser(description='Parsing arguments for binary similarity')
    parser.add_argument("nProc", type=int, help='number of processes to be used')

    args = parser.parse_args()
    n_processes = args.nProc

    # load json file containing similarity relationships

    similarity_path = f'{os.getcwd()}/similarity.json'
    open_json = open(similarity_path, "r")
    similarity_list = json.load(open_json)


    index_list = list(similarity_list.keys()) # list of indices of similar functions

    # load json file containing index: relative path - uniqueid of each json file
    index_path = f'{os.getcwd()}/path-uniqueid.json'
    open_json = open(index_path, "r")
    uniqueid_relpath = json.load(open_json)

    p = Pool(processes=n_processes)
    mappool = p.map(tuples, index_list)

    p.close()
    p.join()

    output_blind = f'{os.getcwd()}/binary-similarity-blind.jsonl'
    output_secret = f'{os.getcwd()}/binary-similarity-secret.jsonl'

    dump_json(mappool, output_blind, output_secret)  # dump on JSON file
