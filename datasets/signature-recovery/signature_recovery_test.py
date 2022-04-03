import multiprocessing
import json
import os
import random

# Store the dataset files in the current directory.
work_dir = os.path.dirname(os.getcwd())

# Directories storing functions JSON representation
json_dir = os.path.join(work_dir, 'json-secret')
json_test_dir = os.path.join(work_dir, 'json-test')

# Compilers and optmization levels corpus.
compilers = ['gcc-10', 'gcc-9', 'gcc-8', 'gcc-7', 'gcc-6', 'clang-11', 'clang-10', 'clang-8', 'clang-6', 'clang-4']
opts = ['O0', 'O1', 'O2', 'O3']

# Number of generated datapoints
num_datapoints = 15000
max_attempts =30


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
		'parameters': [],
	}


def make_secret_entry(datapoint_id, json_function):
	return {
		'datapoint_id': datapoint_id,
		'parameters': json_function['parameters']
	}


def make_index_entry(json_function):
	return f'{json_function["id"]}.json'


if __name__ == '__main__':
	blind_dataset_name = 'signature-recovery-blind_nuovo.jsonl'
	secret_dataset_name = 'signature-recovery-secret_nuovo.jsonl'
	index_name = 'signature-recovery-index_nuovo.json'

	blind_dataset = open(blind_dataset_name, 'w+')
	secret_dataset = open(secret_dataset_name, 'w+')
	index_file = open(index_name, 'w+')

	packages = [package for package in os.listdir(json_dir) if os.path.isdir(os.path.join(json_dir, package))]

	index = {}
	selected_functions = set()
	datapoint_id = 0
	max_num_function_per_package = num_datapoints // len(packages)
	function_per_package = 0
	counter_skip = 0

	for package in packages:
		try:
			while function_per_package < max_num_function_per_package:
				function = pick_random_function(package)
				if counter_skip == max_attempts:
					break
				elif function not in selected_functions:
					selected_functions.add(function)
					skip_flag= False
					with open(function) as json_function_file:
						json_function = json.loads(json_function_file.read())
						params = json_function['parameters']
						if len(params) > 0:
							for p in params:
								type_param = p['type']
								if type_param == 'undefined':
									skip_flag = True
							if not skip_flag:
								function_per_package += 1
								blind_entry = make_blind_entry(datapoint_id)
								secret_entry = make_secret_entry(datapoint_id, json_function)
								index[datapoint_id] = make_index_entry(json_function)

								json.dump(blind_entry, blind_dataset, sort_keys=True)
								json.dump(secret_entry, secret_dataset, sort_keys=True)
								blind_dataset.write('\n')
								secret_dataset.write('\n')

								datapoint_id += 1
						print(function_per_package)
				else:
					counter_skip += 1

			function_per_package = 0
			counter_skip=0
		except Exception as e:
			print("[ERROR]", str(e))
			continue

	json.dump(index, index_file, sort_keys=True)

	blind_dataset.close()
	secret_dataset.close()
	index_file.close()