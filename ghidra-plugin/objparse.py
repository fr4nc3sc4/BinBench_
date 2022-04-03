# Import Ghidra classes.
from ghidra.program.model.block import BasicBlockModel
from ghidra.util.task import TaskMonitor

# Import Java classes.
from java.lang import Byte

# Import built-in modules.
import json
import os
import sys
import time

# Append this tag to script output.
TAG = 'OBJPARSE: '

# Retrieve directories path.
bin_bench_dir = os.path.dirname(os.getcwd())
plugin_dir = os.path.join(bin_bench_dir, 'ghidra-plugin')
json_dir = os.path.join(bin_bench_dir, 'json')

# Append directories containing BinBench dependencies to system path.
sys.path.append(os.path.join(plugin_dir, 'lib', 'python2.7', 'site-packages'))

# Import dependecies.
import networkx as nx

# Get the block model for the current program
block_model = BasicBlockModel(currentProgram)


# Return the standard string representation for an istruction, or process
# the instruction object to return a custom string represenation for the
# instruction.
# Instructions are represented as a dictionary:
# { assembly_code, op_code }
def filter_instruction(instruction):
	inst = instruction.toString()
	inst_addr = instruction.getAddress().toString()

	if instruction.getMnemonicString() == 'CALL':
		target_addr = instruction.getPrimaryReference(0)
		if target_addr != None:
			target_addr = target_addr.getToAddress()
			function_name = getFunctionContaining(target_addr)
			if function_name != None:
				inst = 'CALL {}'.format(function_name)

	return {'code': inst, 'op_code':retrieve_bytecode(instruction)}


# Return the dictionary of instructions contained inside a code block. We look for
# instructions at every address that belongs to the block.
def retrieve_instuctions(block):
	instructions = {}
	for addr in block.getAddresses(True):
		inst = getInstructionAt(addr)
		if inst != None:
			instructions[str(addr)] = filter_instruction(inst)
	return instructions


# Build a networkx control-flow graph for the specified function. Return a
# JSON-serializable representation for the graph, in addition to a dictionary
# mapping a block tag to the actual instructions composing a code block.
# A block tag is just the address associated to the first instruction in a
# block. The CFG only stores block tags to optimize storage usage.
def retrieve_cfg(function):
	cfg = nx.DiGraph()
	asm = {}
	source_blocks = []

	# Retrieve the starting block for the current function, obtain the block
	# tag by retrieving the address of the first instruction in the block.
	start_addr = function.getEntryPoint()
	start_block = block_model.getCodeBlockAt(start_addr, TaskMonitor.DUMMY)
	start_block_tag = start_block.getFirstStartAddress().toString()

	# Add the block tag to the CFG.
	cfg.add_node(start_block_tag)
	# Map block tag to block instructions.
	asm[start_block_tag] = retrieve_instuctions(start_block)
	# Explore blocks structure using BFS. Insert unexplored blocks into a stack.
	source_blocks.append(start_block)

	while len(source_blocks) > 0:
		# Get an unexplored block.
		source_block = source_blocks.pop(0)
		source_block_tag = source_block.getFirstStartAddress().toString()
		# Look for unexplored blocks among the destinations referenced by the
		# current block.
		block_iterator = source_block.getDestinations(TaskMonitor.DUMMY)
		while block_iterator.hasNext():
			dest_block = block_iterator.next().getDestinationBlock()
			dest_block_tag = dest_block.getFirstStartAddress()
			if function == getFunctionContaining(dest_block_tag):
				dest_block_tag = dest_block_tag.toString()
				# When a new block is discovered, insert it into the stack for
				# further exploration and map the block tag to the block
				# instructions
				if dest_block_tag not in cfg.nodes:
					asm[dest_block_tag] = retrieve_instuctions(dest_block)
					source_blocks.append(dest_block)
				cfg.add_edge(source_block_tag, dest_block_tag)

	return nx.readwrite.json_graph.node_link_data(cfg), asm


# Return the function bytecode as a string.
# Please notice that Java represents the byte type as
# an 8-bit signed number. This causes binary numbers with leading ones to be
# interpreted as negative numbers. We solve this problem by extending the byte
# type to int type, using a shift operation.
def retrieve_bytecode(inst):
	bytecode = []
	opcode = inst.getBytes()
	for byte in opcode:
		byte += 1 << Byte.SIZE if byte < 0 else 0
		byte = format(byte, '02X')
		bytecode.append(byte)
	return " ".join(bytecode)


def decode_data_type(data_type):
	data_type_name = str(type(data_type)).split('.')[-1].strip("'<>")
	type_name = data_type_name

	if 'Pointer' in data_type_name or 'Function' in data_type_name or 'Array' in data_type_name:
		type_name = 'pointer'

	elif 'Float' in data_type_name or 'Double' in data_type_name:
		type_name = 'float'

	elif 'Char' in data_type_name:
		type_name = 'char'

	elif 'Integer' in data_type_name or 'Long' in data_type_name or 'Short' in data_type_name or \
	'Word' in data_type_name or 'Byte' in data_type_name or 'Boolean' in data_type_name:
		type_name = 'int'

	elif 'Enum' in data_type_name:
		type_name = 'enum'

	elif 'Struct' in data_type_name:
		type_name = 'struct'

	elif 'Union' in data_type_name:
		type_name = 'union'

	elif 'Typedef' in data_type_name:
		type_name = decode_data_type(data_type.getBaseDataType())

	elif 'Void' in data_type_name:
		type_name = 'void'

	elif 'Undefined' in data_type_name or 'Default' in data_type_name:
		type_name = 'undefined'

	else:
		print(type_name)

	return type_name


# Return the function parameters as a list of tuples, where each tuple follows
# the scheme: (< parameter_name >, < parameter_type >).
def retrieve_parameters(function):
	params = []
	signature = function.getSignature()
	for param in signature.getArguments():
		params.append({'name': param.getName(), 'type': decode_data_type(param.getDataType())})
	return params


# Return the dictonary of functions calling the current function.
# The dictonary contains entries having format:
# { function_entry_point: function_name }
def retrieve_callers(function):
	caller_functions = {}
	for caller_function in function.getCallingFunctions(TaskMonitor.DUMMY):
		start_addr = caller_function.getEntryPoint().toString()
		name = caller_function.getName()
		caller_functions[start_addr] = name
	return caller_functions


# Return the dictonary of functions called by the current function.
# The dictonary contains entries having format:
# { function_entry_point: function_name }
def retrieve_called(function):
	called_functions = {}
	for called_function in function.getCalledFunctions(TaskMonitor.DUMMY):
		start_addr = called_function.getEntryPoint().toString()
		name = called_function.getName()
		called_functions[start_addr] = name
	return called_functions


try:
	package_name = getScriptArgs()[0]
	compiler = getScriptArgs()[1]
	opt = getScriptArgs()[2]
	work_dir = os.path.join(json_dir, package_name, compiler, opt)
except:
	work_dir = json_dir
	print('{} no working directory specied, writing output in {}'.format(TAG, json_dir))

# Benchmark script execution time
time_start = time.time()

# Retrieve all functions in the analyzed program, dynamicaly linked library
# calls are excluded from the list.
functions = currentProgram.getFunctionManager().getFunctionsNoStubs(True)

# Produce the BinBench function representation for each program function.
for function in functions:
	cfg, asm = retrieve_cfg(function)
	bin_bench_fun = {}
	bin_bench_fun['id'] = ''
	bin_bench_fun['package'] = package_name
	bin_bench_fun['compiler'] = compiler
	bin_bench_fun['opt_level'] = opt
	bin_bench_fun['origin_file'] = currentProgram.getName()
	bin_bench_fun['cfg'] = cfg
	bin_bench_fun['asm'] = asm
	bin_bench_fun['name'] = function.getName()
	bin_bench_fun['parameters'] = retrieve_parameters(function)
	bin_bench_fun['return_type'] = decode_data_type(function.getReturnType())
	bin_bench_fun['callers'] = retrieve_callers(function)
	bin_bench_fun['called'] = retrieve_called(function)

	# Write json fragments representing the functions Ghidra identified during
	# program analysis.
	json_frag_name = '{}.json'.format(bin_bench_fun['name'])
	with open(os.path.join(work_dir, json_frag_name), 'w+') as frag:
		json.dump(bin_bench_fun, frag, sort_keys=True)

time_end = time.time()
print('{} execution time: {} ms'.format(TAG, int((time_end - time_start) * 1000)))