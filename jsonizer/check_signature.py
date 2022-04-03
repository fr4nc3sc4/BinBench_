import json
import os

# Run the jsonizer and cleaner script using this working directory.
work_dir = os.path.dirname(os.path.realpath(__file__))

# Directory storing JSON output.
json_dir = os.path.join(os.path.dirname(work_dir), 'json')

# Compilers corpus.
compiler = 'gcc-10'
opt = 'O0'

if __name__ == '__main__':
	packages = [package for package in os.listdir(json_dir) if os.path.isdir(os.path.join(json_dir, package))]
	types = set()

	for package in packages:
		if os.path.isdir(os.path.join(json_dir, package, compiler, opt)):
			functions = os.listdir(os.path.join(json_dir, package, compiler, opt))
			for function in functions:
				function = os.path.join(json_dir, package, compiler, opt, function)
				with open(function) as json_function_file:
						json_function = json.loads(json_function_file.read())
						for param in json_function['parameters']:
							types.add(param['type'])

	print(types)