import multiprocessing
import json
import os
import random
from re import finditer
from wordsegment import load, segment

# Store the dataset files in the current directory.
work_dir = os.path.dirname(os.path.realpath(__file__))

# Directories storing functions JSON representation
json_dir = os.path.join(os.path.dirname(os.path.dirname(work_dir)), 'BinBench/json')

# Compilers and optimization levels corpus.
compilers = ['gcc-10', 'gcc-9', 'gcc-8', 'gcc-7', 'gcc-6', 'clang-11', 'clang-10', 'clang-8', 'clang-6', 'clang-4']
opts = ['O0', 'O1', 'O2', 'O3']

# Number of generated datapoints
num_datapoints = 1300000
# Max number of random attempts for picking a function
max_attempts = 30

def flatten_array_name(pretokenized_name):
	# flatten the array of the pretokenized name
    return [tok for sublst in pretokenized_name for tok in sublst]

def camel_case_split(func_name):
	match = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', func_name)
	return [m.group(0) for m in match]

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


def make_secret_entry(datapoint_id, json_function):
	name = load()
	name = camel_case_split(json_function['name'])
	name = [snake_case(splt) for splt in name]
	name = (flatten_array_name(name))
	name = flatten_array_name([segment(word) for word in name])

	return {
		'datapoint_id': datapoint_id,
		'name': json_function['name'],
		'splitted_name': name
	}


def make_index_entry(function):
	function_split = function.split("/")[-4:]
	function_path =""
	for funct in function_split:
		function_path += f'/{funct}'
	return function_path


if __name__ == '__main__':
	secret_dataset_name = 'function_naming-train.jsonl'
	index_name = 'function_naming-index-train.json'

	secret_dataset = open(os.path.join(work_dir, secret_dataset_name), 'w+')
	index_file = open(os.path.join(work_dir, index_name), 'w+')

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
					function_per_package += 1

					with open(function) as json_function_file:
						json_function = json.loads(json_function_file.read())
						secret_entry = make_secret_entry(datapoint_id, json_function)
						index[datapoint_id] = make_index_entry(function)

						
						json.dump(secret_entry, secret_dataset, sort_keys=True)
						
						secret_dataset.write('\n')

						datapoint_id += 1
						print(function_per_package)
				else:
					counter_skip +=1

			function_per_package = 0
			counter_skip = 0
		except Exception as e:
			print("[ERROR]", str(e))
			continue

	json.dump(index, index_file, sort_keys=True)

	secret_dataset.close()
	index_file.close()