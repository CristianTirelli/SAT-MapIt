#!/bin/sh -eu

git submodule init 
git submodule update --recursive
mkdir -p llvm-project/build
cd llvm-project/build
cmake -G "Ninja" -DCMAKE_BUILD_TYPE=Release -DLLVM_ENABLE_PROJECTS="clang;" ../llvm
ninja -j 1
cd -
python3 -m venv cgra-compiler
. cgra-compiler/bin/activate
python3 -m pip install -r requirements.txt