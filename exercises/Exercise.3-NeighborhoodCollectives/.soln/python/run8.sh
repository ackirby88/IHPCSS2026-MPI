#!/bin/bash
mpirun -np 8 python3 stencil_mpi_carttopo_neighcolls.py 512 10 10000
