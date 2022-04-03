import argparse
import json
import math
import multiprocessing
import os

work_dir = os.path.dirname(os.path.realpath(__file__))
json_dir = os.path.join(os.path.dirname(work_dir), 'json')
elf_dir = os.path.join(os.path.dirname(work_dir), 'elf')

# Compilers and optmization levels corpus.
compilers = ['gcc-10', 'gcc-9', 'gcc-8', 'gcc-7', 'gcc-6', 'clang-11', 'clang-10', 'clang-8', 'clang-6', 'clang-4']
opts = ['O0', 'O1', 'O2', 'O3']


def count_similar(func, package):
	pacakge_sim_count = 0

	for compiler in compilers:
		for opt in opts:
			functions_path = os.path.join(json_dir, package, compiler, opt)
			function_pool = os.listdir(functions_path)
			pacakge_sim_count = pacakge_sim_count + 1 if func in function_pool else pacakge_sim_count

	return pacakge_sim_count - 1


def count_package(package):
	package_num_functions_tot = 0
	package_num_functions_unique = 0
	package_num_avg_sim = 0

	sample_dir = os.path.join(json_dir, package, 'gcc-10', 'O0')
	function_pool = os.listdir(sample_dir)

	package_num_functions_unique = len(function_pool)

	for func in function_pool:
		package_num_avg_sim += count_similar(func, package)

	package_num_avg_sim = package_num_avg_sim / len(function_pool)

	for compiler in compilers:
		for opt in opts:
			function_pool = os.listdir(os.path.join(json_dir, package, compiler, opt))
			package_num_functions_tot += len(function_pool)

	print(f'collected stats for {package}')
	return package_num_functions_tot, package_num_functions_unique, package_num_avg_sim


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-j', type=int, metavar='num_procs', default=30, help='maximum number of parallel processes')
	args = parser.parse_args()

	num_functions_tot = 0
	num_functions_unique = 0
	num_avg_sim = 0

	packages = [package for package in os.listdir(json_dir) if os.path.isdir(os.path.join(json_dir, package))]
	num_procs = len(packages)

	with multiprocessing.Pool(num_procs) as pool:
		package_stats = pool.map(count_package, packages)

	for package_stat in package_stats:
		num_functions_tot += package_stat[0]
		num_functions_unique += package_stat[1]
		num_avg_sim += package_stat[2]

	num_avg_sim /= len(packages)

	print(f'Total number of functions {num_functions_tot}')
	print(f'Total number of unique functions {num_functions_unique}')
	print(f'Average number of similar functions {num_avg_sim}')
