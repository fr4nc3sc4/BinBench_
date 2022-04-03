#!/bin/bash

gcc=( "gcc-10" "gcc-9" "gcc-8" "gcc-7" "gcc-6" )
clang=( "clang-11" "clang-10" "clang-8" "clang-6" "clang-4" )

clang10="https://github.com/llvm/llvm-project/releases/download/llvmorg-10.0.0/clang+llvm-10.0.0-x86_64-linux-gnu-ubuntu-18.04.tar.xz"
clang8="https://releases.llvm.org/8.0.0/clang+llvm-8.0.0-x86_64-linux-gnu-ubuntu-18.04.tar.xz"
clang6="https://releases.llvm.org/6.0.0/clang+llvm-6.0.0-x86_64-linux-gnu-ubuntu-16.04.tar.xz"
clang4="https://releases.llvm.org/4.0.0/clang+llvm-4.0.0-x86_64-linux-gnu-ubuntu-16.10.tar.xz"

declare -A pids

for gcc_ver in ${gcc[@]}; do
	c_compiler_name="gcc"
	cxx_compiler_name="g++"
	compiler_version="${gcc_ver##*-}"
	package_name="$c_compiler_name$compiler_version"

	echo "building docker image for $gcc_ver"
	docker build --build-arg C_COMPILER_NAME=$c_compiler_name --build-arg CXX_COMPILER_NAME=$cxx_compiler_name \
	--build-arg COMPILER_VERSION=$compiler_version --build-arg PACKAGE_NAME=$package_name -f Dockerfile --rm \
	-t binbench/$gcc_ver . &

	pids[$gcc_ver]=$!
done

for clang_ver in ${clang[@]}; do
	c_compiler_name="clang"
	cxx_compiler_name="clang++"
	compiler_version="${clang_ver##*-}"

	if [[ $compiler_version == "10" ]]; then
		package_name=$clang10
	elif [[ $compiler_version == "8" ]]; then
		package_name=$clang8
	elif [[ $compiler_version == "6" ]]; then
		package_name=$clang6
	elif [[ $compiler_version == "4" ]]; then
		package_name=$clang4
	fi

	echo "building docker image for $clang_ver"
	docker build --build-arg C_COMPILER_NAME=$c_compiler_name --build-arg CXX_COMPILER_NAME=$cxx_compiler_name \
	--build-arg COMPILER_VERSION=$compiler_version --build-arg PACKAGE_NAME=$package_name -f Dockerfile --rm \
	-t binbench/$clang_ver . &

	pids[$clang_ver]=$!
done

for gcc_ver in ${gcc[@]}; do
	wait ${pids[$gcc_ver]}
done

for clang_ver in ${clang[@]}; do
	wait ${pids[$clang_ver]}
done