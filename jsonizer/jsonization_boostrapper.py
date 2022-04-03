import argparse
import multiprocessing
import os
import shutil
import subprocess
import sys
import time

# Keep track of storage space usage, stop at 95% occupied space.
storage_threshold = 0.95

# Run the jsonizer and cleaner script using this working directory.
work_dir = os.path.dirname(os.path.realpath(__file__))

# Directory storing compiled ELF files.
elf_dir = os.path.join(os.path.dirname(work_dir), 'elf')

# Directory storing JSON output.
json_dir = os.path.join(os.path.dirname(work_dir), 'json')

# JSONization script.
jsonizer_script = os.path.join(work_dir, 'jsonize.sh')

# Cleanup script.
cleaner_script = os.path.join(work_dir, 'clean.sh')

# Compilers corpus.
compilers = ['gcc-10', 'gcc-9', 'gcc-8', 'gcc-7', 'gcc-6', 'clang-11', 'clang-10', 'clang-8', 'clang-6', 'clang-4']


# Return storage space occupation ratio.
def get_storage_usage():
	total, used, free = shutil.disk_usage("/")
	return round(used / total, 2)


# Return True if the JSONization process was successful for any compiler. JSONization is successful if there exists
# a .jsonized file inside the compiler directory.
def check_successful_jsonization(package_dir, compiler):
	compiler_dir = os.path.join(package_dir, compiler)

	if '.jsonized' in os.listdir(compiler_dir):
		return True
	else:
		return False


# Check for partial results in case the script execution is interrupted. Return the list of compilers for which
# the JSONization process was successful.
def get_successful_compilers(package_name):
	package_dir = os.path.join(json_dir, package_name)
	successful_compilers = []

	if os.path.isdir(package_dir):

		for compiler in os.listdir(package_dir):
			if check_successful_jsonization(package_dir, compiler):
				successful_compilers.append(compiler)

	return successful_compilers


# Create a .jsonized file for successfully JSONized packages. This prevents the script from trying to
# JSONize them again.
def flag_package(package_name, compiler):
	package_dir = os.path.join(json_dir, package_name)
	compiler_dir = os.path.join(package_dir, compiler)
	flag = open(os.path.join(compiler_dir, '.jsonized'), 'w+')
	flag.close()


def jsonize(package_name):
	# Read elf data from this directory.
	elf_package_dir = os.path.join(elf_dir, package_name)

	# Check for storage space occupation.
	if get_storage_usage() > storage_threshold:
		return -2

	# Skip packages failing to compile.
	if '.nopkg' in os.listdir(elf_package_dir):
		return -1

	# Check for previous work.
	successful_compilers = get_successful_compilers(package_name)

	# Start producing JSON output.
	num_compilers = len(successful_compilers)
	work_compilers = set(compilers) - set(successful_compilers)

	for compiler in work_compilers:
		print(f'jsonizing {package_name} - {num_compilers / len(compilers):.0%} complete')
		subprocess.run([jsonizer_script, package_name, compiler], cwd=work_dir, capture_output=True)
		flag_package(package_name, compiler)
		num_compilers +=1

	print(f'jsonized {package_name} - {1.0:.0%} complete')

	# JSON output corrrectly generated.
	return 0


if __name__ == '__main__':
	# Get the number of runnable parallel processes from command line.
	parser = argparse.ArgumentParser()
	parser.add_argument('-j', type=int, metavar='num_procs', default=1, help='maximum number of parallel processes')
	args = parser.parse_args()

	# Acquire the package list.
	package_list = [package_name for package_name in os.listdir(elf_dir) if os.path.isdir(os.path.join(elf_dir, package_name))]

	# Cleanup just in case the script was unexpectedly interrupted.
	subprocess.run([cleaner_script], cwd=work_dir)

	# Start procducing JSON output using multiple processes.
	with multiprocessing.Pool(args.j) as pool:
		ret = pool.map(jsonize, package_list)

	# Cleanup
	subprocess.run([cleaner_script], cwd=work_dir)

	# Collect statitics
	jsonized_packages = 0

	with open('out.log', 'w+') as log_file:
		for (package_name, code) in zip(package_list, ret):

			if code == 0:
				log = 'success'
				jsonized_packages += 1
			elif code == -1:
				log = 'compilation error'
				jsonized_packages += 1
			else:
				log = 'saturation error'

			log_file.write(f'{package_name} - {log}\n')

	completition_ratio = jsonized_packages / len(package_list)
	print(f'{completition_ratio:.0%} of packages successfuly JSONized - {jsonized_packages} / {len(package_list)}')
	print('please checkout out.log for additional results')
