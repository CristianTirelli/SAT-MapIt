# SAT-MapIt: A SAT-based Modulo Scheduling Mapper for Coarse Grain Reconfigurable Architectures


### Abstract:

Coarse-Grain Reconfigurable Arrays (CGRAs) are emerging low-power architectures aimed at accelerating compute-intensive application loops.
The acceleration that a CGRA can ultimately provide, however, heavily depends on the quality of the mapping, i.e. on how effectively the loop is compiled onto the given platform. State of the Art compilation techniques achieve mapping through modulo scheduling, a strategy which  attempts to minimize the II (Iteration Interval) needed to execute a loop, and they do so usually through well known graph algorithms, such as Max-Clique Enumeration.


We address the mapping problem through a SAT formulation, instead, and thus explore the solution space more effectively than current SoA tools.
To formulate the SAT problem, we introduce an ad-hoc schedule called the Kernel Mobility Schedule (KMS), which we use in conjunction with  the data-flow graph and the architectural information of the CGRA in order to create a set of boolean statements that describe all constraints to be obeyed by the mapping for a given II. We then let  the SAT solver efficiently navigate this complex space. As in other SoA techniques, the process is iterative: if a valid mapping does not exist for the given II, the II is increased and a new KMS and set of constraints is generated and solved.

Our experimental results show that SAT-MapIt obtains better results compared to SoA alternatives in 47.72% of the benchmarks explored: sometimes finding a lower II, and others even finding a valid mapping when none could previously be found.

## Requirements 
This project was developed and tested on Ubuntu 20.04.6. To generate the CMake files, we used CMake version 3.23.20220426-g07a54b2.

## First start:
1. Run `setup.sh` to compile LLVM and configure the Python environment.
2) Before using the compiler, activate the virtual environment with:
``` bash
source cgra-compiler/bin/activate
```



## Supported Code
In the `benchmarks` folder, you'll find sample code that can be used to map onto a CGRA. 
To compile your own code, simply add  ```#pragma cgra acc``` before the loop you'd like to map to the CGRA.

**Note**: Currently, the compiler only supports:
- Innermost loops.
- Loops without function calls or conditionals.

#### Example (from `benchmarks/reverse_bits`):
```c
#pragma cgra acc
for (int i = rev = 0; i < NumBits; i++)
{
    rev = (rev << 1) | (index & 1);
    index >>= 1;
}
```



## Compilation Instructions
After adding the ```#pragma cgra acc```  directive to your code, compile it with the following command:

```bash
./cgralang -f benchmarks/sha2/sha.c
```

By default, the code will be compiled for a 4x4 CGRA. To specify a different CGRA size, use the `-x` and `-y` options. For example, to compile for a 5x5 CGRA, run:

```bash
./cgralang -f benchmarks/sha2/sha.c -x 5 -y 5
```
## Output
The output of the compiler is a file called `cgra-code-acc`, which includes various debug information and the mapping result. The tool is still in development and not yet reliable enough to be used as a black box. \
A manual review of the output is always recommended at this stage to ensure correctness.

## Future Improvements
The compiler is still under active development. \
In the next update, we plan to include:
- Code refactoring for better maintainability.
- Additional mapping options that can be configured at compile time for increased flexibility.

## SAT-MapIt LITE
A Lite version of the tool is available at: https://github.com/CristianTirelli/SAT-MapIt-Lite
