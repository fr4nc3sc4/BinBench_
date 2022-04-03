#!/bin/bash

package_name=$1
if [[ -z $package_name ]]; then
	echo "usage: init_complation.sh < compiler > < package_name >"
	exit
fi

compiler=$2
if [[ -z $compiler ]]; then
	echo "usage: init_complation.sh < compiler > < package_name >"
	exit
fi

elf_dir=$(pwd)/../elf

opts=( "O0" "O1" "O2" "O3" )

declare -A pids

# Run docker containers responsible for compilation.
for opt in ${opts[@]}; do
	mkdir -p $elf_dir/$package_name/$compiler
	chmod 777 $elf_dir/$package_name/$compiler
	docker run -i -v "$elf_dir/$package_name/$compiler":/home/binbench/elf -v $(pwd):/home/binbench/data --rm \
	--env PACKAGE_NAME=$package_name --env OPT=$opt binbench/$compiler /home/binbench/data/compile.sh &
	pids[$opt]=$!
done

for opt in ${opts[@]}; do
	wait ${pids[$opt]}
done