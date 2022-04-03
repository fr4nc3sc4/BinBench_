import multiprocessing
import json
import os
import random

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
		'compiler': '',
		'opt_level': ''
	}


def make_secret_entry(datapoint_id, json_function):
	return {
		'datapoint_id': datapoint_id,
		'compiler': json_function['compiler'],
		'opt_level': json_function['opt_level']
	}


def make_index_entry(json_function):
	return f'{json_function["id"]}.json'


if __name__ == '__main__':
	blind_dataset_name = 'compiler-provenance-blind.jsonl'
	secret_dataset_name = 'compiler-provenance-secret.jsonl'
	index_name = 'compiler-provenance-index.json'

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

						json.dump(blind_entry, blind_dataset, sort_keys=True)
						json.dump(secret_entry, secret_dataset, sort_keys=True)
						blind_dataset.write('\n')
						secret_dataset.write('\n')

						datapoint_id += 1
						print(function_per_package)

			function_per_package = 0
		except Exception as e:
			print("[ERROR]", str(e))

	json.dump(index, index_file, sort_keys=True)

	blind_dataset.close()
	secret_dataset.close()
	index_file.close()