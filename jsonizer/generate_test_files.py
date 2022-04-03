import argparse
import multiprocessing
import json
import os

# Store the dataset files in the current directory.
work_dir = os.path.dirname(os.path.realpath(__file__))

# Directories storing functions JSON representation
json_dir = os.path.join(os.path.dirname(work_dir), 'json-secret')
json_test_dir = os.path.join(os.path.dirname(work_dir), 'json-test')

# Compilers and optmization levels corpus.
compilers = ['gcc-10', 'gcc-9', 'gcc-8', 'gcc-7', 'gcc-6', 'clang-11', 'clang-10', 'clang-8', 'clang-6', 'clang-4']
opts = ['O0', 'O1', 'O2', 'O3']


def make_test_entry(function):
	called, callers = resolve_function_names(function)
	return {
		'asm': function['asm'],
		'cfg': function['cfg'],
		'called': called,
		'callers': callers
	}


def resolve_function_names(function):
	called = []
	callers = []
	base_path = os.path.join(json_dir, function['package'], function['compiler'], function['opt_level'])
	functions = os.listdir(base_path)

	for called_fun in function['called']:
		called_fun_name = f'{called_fun[1]}.json'
		if called_fun_name in functions:
			with open(os.path.join(base_path, called_fun_name)) as json_called_func:
				function = json.loads(json_called_func.read())
				called_fun[1] = f'{function["id"]}.json'
				called.append(called_fun)

	for caller_fun in function['callers']:
		caller_fun_name = f'{caller_fun[1]}.json'
		if caller_fun_name in functions:
			with open(os.path.join(base_path, caller_fun_name)) as json_caller_func:
				function = json.loads(json_caller_func.read())
				caller_fun[1] = f'{function["id"]}.json'
				callers.append(caller_fun)

	return called, callers


def generate_test_files(package):
	for compiler in compilers:
		for opt in opts:
			base_path = os.path.join(json_dir, package, compiler, opt)
			functions = os.listdir(base_path)
			for function in functions:
				with open(os.path.join(base_path, function)) as json_func:
					function = json.loads(json_func.read())
					test_entry_file = open(os.path.join(json_test_dir, f'{function["id"]}.json'), 'w+')
					test_entry = make_test_entry(function)
					json.dump(test_entry, test_entry_file, sort_keys=True)
					test_entry_file.close()


if __name__ == '__main__':
	# Get the number of runnable parallel processes from command line.
	parser = argparse.ArgumentParser()
	parser.add_argument('-j', type=int, metavar='num_procs', default=1, help='maximum number of parallel processes')
	args = parser.parse_args()

	# Acquire the package list.
	package_list = [package_name for package_name in os.listdir(json_dir) if os.path.isdir(os.path.join(json_dir, package_name))]

	# Start procducing JSON output using multiple processes.
	with multiprocessing.Pool(args.j) as pool:
		ret = pool.map(generate_test_files, package_list)

	print('test files generated successfully')