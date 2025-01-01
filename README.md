# Waterlang

Statically typed, compiled to C++ language with OOP and FP facilities. 

## Compilation

Waterlang uses C++ as a backend, which is compiled with g++.

## Usage

```
main.py <IN> <OUT> [PARAMS...]
Parameters:
--check         check the correctness of the program without compilation
--cpp           don't remove the c++ source 
--no-compile    don't compile the c++ source. implies --cpp
```