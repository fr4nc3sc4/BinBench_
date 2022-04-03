#!/bin/bash

package_name=$1
if [[ -z $package_name ]]; then
	echo "usage: jsonize.sh < compiler > < package_name >"
	exit
fi

compiler=$2
if [[ -z $compiler ]]; then
	echo "usage: jsonize.sh < compiler > < package_name >"
	exit
fi

elf_dir=$(pwd)/../elf
json_dir=$(pwd)/../json
plugin_dir=$(pwd)/../ghidra-plugin
projects_dir=$(pwd)/../ghidra-projects

opts=( "O0" "O1" "O2" "O3" )

declare -A pids

# Start generating JSON output.
for opt in ${opts[@]}; do
	mkdir -p $json_dir/$package_name/$compiler/$opt
	chmod 777 $json_dir/$package_name/$compiler/$opt
	analyzeHeadless $projects_dir "$package_name"_"$compiler"_"$opt" -import $elf_dir/$package_name/$compiler/$opt/* \
	-postScript $plugin_dir/objparse.py $package_name $compiler $opt &
	pids[$opt]=$!
done

for opt in ${opts[@]}; do
	wait ${pids[$opt]}
done
