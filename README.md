# BinBench
BinBench is a benchmark for the evaluation of machine learning solutions applied to binary analisys.

## Generating Docker images
Binbench uses docker containers to compile arc linux packages. Before starting the compilation process,
be sure to build the required docker images:
```
cd docker/
./spawn_images.sh
```
The script will build an Arc Linux image for each of the following compilers:
- gcc-10, gcc-9, gcc-8, gcc-7, gcc-6.
- clang-11, clang-10, clang-8, clang-6, clang-4.

## Compilation
Start the compilation process using:
```
cd compiler/
python3 ./compilation_boostrapper.py -j <num_parallel_processes>
```
This process may take a very long time depending on the number of packages listed in package_list.txt file.\
The script implements some kind of partial work recovery, not all progress will be lost on interruption.\
In particular, it creates a *.nopkg* file in the *elf* package directory for any package failing to compile, this
prevents any attempts at compiling the package again.

## JSONization
Once the compilation process finishes, start setting up the Ghidra plugin:

- First of all, install [*Ghidra*](https://ghidra-sre.org/ghidra_9.2.1_PUBLIC_20201215.zip) and append the Ghidra
*support* directory to your *PATH*.

- Install a virtual environment in the plugin directory:\
```virtualenv -p python2.7 ./ghidra_plugin```

- Activate the virtual environment using:\
```source ./ghidra_plugin/bin/activate```

- Install the plugin dependencies:\
```pip install -r ./ghidra_plugin/requirements.txt```

Finally, run the driver script and start generating the JSON dataset
```
python3 ./driver.py -j <num_parallel_processes>
```