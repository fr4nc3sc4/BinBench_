import multiprocessing
import json
import os
import random
from re import finditer
from wordsegment import load, segment

# Store the dataset files in the current directory.
work_dir = os.path.dirname(os.path.realpath(__file__))

# Directories storing functions JSON representation
json_dir = os.path.join(os.path.dirname(os.path.dirname(work_dir)), 'BinBench/json-secret')
json_test_dir = os.path.join(os.path.dirname(os.path.dirname(work_dir)), 'BinBench/json-test')

# Compilers and optimization levels corpus.
compilers = ['gcc-10', 'gcc-9', 'gcc-8', 'gcc-7', 'gcc-6', 'clang-11', 'clang-10', 'clang-8', 'clang-6', 'clang-4']
opts = ['O0', 'O1', 'O2', 'O3']

# Number of generated datapoints
num_datapoints = 10000

def flatten_array_name(pretokenized_name):
	# flatten the array of the pretokenized name
    return [tok for sublst in pretokenized_name for tok in sublst]

def snake_case(func_name):
	match = list(filter(None,func_name.split("_")))
	return match

def pick_random_function(package):
	compiler_idx = random.randint(0, len(compilers) - 1)
	opt_idx = random.randint(0, len(opts) - 1)
	compiler = compilers[compiler_idx]
	opt = opts[opt_idx]

	random_path = os.path.join(json_dir, package, compiler, opt)
	functions = os.listdir(random_path)
	function_idx = random.randint(0, len(functions) - 1)

	return os.path.join(random_path, functions[function_idx])


def make_blind_entry(datapoint_id):
	return {
		'datapoint_id': datapoint_id,
		'name': [],
		'splitted_name': []
	}


def make_secret_entry(datapoint_id, json_function):
	name = load()
	name = snake_case(json_function['name'])
	name = flatten_array_name([segment(word) for word in name])

	return {
		'datapoint_id': datapoint_id,
		'name': json_function['name'],
		'splitted_name': name
	}


def make_index_entry(json_function):
	return f'{json_function["id"]}.json'


if __name__ == '__main__':
	blind_dataset_name = 'function_naming-blind_new.jsonl'
	secret_dataset_name = 'function_naming-secret_new.jsonl'
	index_name = 'function_naming-index_new.json'

	blind_dataset = open(os.path.join(work_dir, blind_dataset_name), 'w+')
	secret_dataset = open(os.path.join(work_dir, secret_dataset_name), 'w+')
	index_file = open(os.path.join(work_dir, index_name), 'w+')

	packages = [package for package in os.listdir(json_dir) if os.path.isdir(os.path.join(json_dir, package))]

	index = {}
	selected_functions = set()
	datapoint_id = 0
	max_num_function_per_package = num_datapoints // len(packages)
	function_per_package = 0

	for package in packages:
		try:
			while function_per_package < max_num_function_per_package:				
				function = pick_random_function(package)
				if function not in selected_functions:
					selected_functions.add(function)
					function_per_package += 1

					with open(function) as json_function_file:
						json_function = json.loads(json_function_file.read())
						blind_entry = make_blind_entry(datapoint_id)
						secret_entry = make_secret_entry(datapoint_id, json_function)
						index[datapoint_id] = make_index_entry(json_function)
						print(json_function['name'], secret_entry)

						json.dump(blind_entry, blind_dataset, sort_keys=True)
						json.dump(secret_entry, secret_dataset, sort_keys=True)
						blind_dataset.write('\n')
						secret_dataset.write('\n')

						datapoint_id += 1
						print(function_per_package)

			function_per_package = 0
		except Exception as e:
				print(str(e), "[ERROR] \n...continue...\n")

	json.dump(index, index_file, sort_keys=True)

	blind_dataset.close()
	secret_dataset.close()
	index_file.close()