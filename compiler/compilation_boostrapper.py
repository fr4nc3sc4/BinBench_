import argparse
import filecmp
import multiprocessing
import subprocess
import os
import shutil
import time

# Keep track of storage space usage, stop at 95% occupied space.
storage_threshold = 0.95

# Run the compilation script using this working directory.
work_dir = os.path.dirname(os.path.realpath(__file__))

# Directory storing compiled ELF files.
elf_dir = os.path.join(os.path.dirname(work_dir), 'elf')

# Compilation script.
script = os.path.join(work_dir, 'init_compilation.sh')

# Compilers and optmization levels corpus.
compilers = ['gcc-10', 'gcc-9', 'gcc-8', 'gcc-7', 'gcc-6', 'clang-11', 'clang-10', 'clang-8', 'clang-6', 'clang-4']
opts = ['O0', 'O1', 'O2', 'O3']


# Return storage space occupation ratio.
def get_storage_usage():
	total, used, free = shutil.disk_usage("/")
	return round(used / total, 2)


# Return True if the script managed to produce differently optmized binaries. Compare the hash-code produced by a
# random file, optimized using O0 and O3.
def check_optimization_level(package_name):
	package_dir = os.path.join(elf_dir, package_name)
	elf_O0_name = os.listdir(os.path.join(package_dir, 'gcc-10', 'O0'))[0]
	elf_O3_name = os.listdir(os.path.join(package_dir, 'gcc-10', 'O3'))[0]
	elf_O0 = os.path.join(package_dir, 'gcc-10', 'O0', elf_O0_name)
	elf_O3 = os.path.join(package_dir, 'gcc-10', 'O3', elf_O3_name)

	if filecmp.cmp(elf_O0, elf_O3, shallow=False):
		return False
	else:
		return True


# Return True if the compilation process was successful for any compiler. Compilation is unsuccessful if:
# - Some optimization level directory is missing.
# - The number of compiled files differs among any two optimization level directories.
# - Some optimization level directory is empty.
def check_successful_compilation(package_dir, compiler):
	compiler_dir = os.path.join(package_dir, compiler)

	if len(os.listdir(compiler_dir)) < len(opts):
		return False

	num_elf = [len(os.listdir(os.path.join(compiler_dir, opt))) for opt in opts]

	if len(set(num_elf)) != 1:
		return False

	if num_elf[0] == 0:
		return False

	return True


# Check for partial results in case the script execution is interrupted. Return the list of compilers which
# successfully completed the compilation process.
def get_successful_compilers(package_name):
	package_dir = os.path.join(elf_dir, package_name)
	successful_compilers = []

	if os.path.isdir(package_dir):

		if '.nopkg' in os.listdir(package_dir):
			return compilers.copy()

		for compiler in os.listdir(package_dir):
			if check_successful_compilation(package_dir, compiler):
				successful_compilers.append(compiler)

	return successful_compilers


# Create a .nopkg file for packages failing to compile. This prevents the script from trying to compile them again.
def flag_package(package_name):
	package_dir = os.path.join(elf_dir, package_name)
	flag = open(os.path.join(package_dir, '.nopkg'), 'w+')
	flag.close()


# Worker processes job.
def compile(package_name):
	package_dir = os.path.join(elf_dir, package_name)

	# Check for storage space occupation.
	if get_storage_usage() > storage_threshold:
		return -3

	# Check for previous work.
	successful_compilers = get_successful_compilers(package_name)

	# Start the compilation process for a package.
	num_compilers = len(successful_compilers)
	work_compilers = set(compilers) - set(successful_compilers)

	for compiler in work_compilers:
		print(f'compiling {package_name} - {num_compilers / len(compilers):.0%} complete')
		subprocess.run([script, package_name, compiler], cwd=work_dir, capture_output=True)
		num_compilers += 1

	print(f'compiled {package_name} - {1.0:.0%} complete')

	# Check for errors
	successful_compilers = get_successful_compilers(package_name)

	if len(successful_compilers) != len(compilers):
		flag_package(package_name)
		return -1

	if '.nopkg' in os.listdir(package_dir):
		return -1

	if not check_optimization_level(package_name):
		flag_pakcage(package_name)
		return -2

	# Compilation was successful.
	return 0


if __name__ == '__main__':
	# Get the number of runnable parallel processes from command line.
	parser = argparse.ArgumentParser()
	parser.add_argument('-j', type=int, metavar='num_procs', default=10, help='maximum number of parallel processes')
	args = parser.parse_args()

	# Acquire the list of packages.
	with open(os.path.join(work_dir, 'package_list.txt')) as packages:
		package_list = packages.readlines()
	package_list = [package_name.strip() for package_name in package_list]

	# Start the parallel compilation process.
	with multiprocessing.Pool(args.j) as pool:
		ret = pool.map(compile, package_list)

	# Collect statitics
	compiled_packages = 0

	with open('out.log', 'w+') as log_file:
		for (package_name, code) in zip(package_list, ret):

			if code == 0:
				log = 'success'
				compiled_packages += 1
			elif code == -1:
				log = 'compilation error'
			elif code == -2:
				log = 'optimization error'
			else:
				log = 'saturation error'

			log_file.write(f'{package_name} - {log}\n')

	completition_ratio = compiled_packages / len(package_list)
	print(f'{completition_ratio:.0%} of packages successfuly compiled - {compiled_packages} / {len(package_list)}')
	print('please checkout out.log for additional results')