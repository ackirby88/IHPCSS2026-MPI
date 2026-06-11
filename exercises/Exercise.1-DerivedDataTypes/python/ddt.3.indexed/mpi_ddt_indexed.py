from mpi4py import MPI
import numpy as np

NELEMENTS = 6

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
numtasks = comm.Get_size()
source = 0
tag = 1

if rank == 0:
    a = np.array([ 1.0,  2.0,  3.0,  4.0,  5.0,  6.0,  7.0,  8.0,
                   9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0], dtype='f')
else:
    a = None

b = np.empty(NELEMENTS, dtype='f')

# =========================================================================
# Step 1. Create an MPI Indexed Type
#    MPI.Datatype.Create_indexed(blocklengths, displacements)
#      blocklengths   - number of elements in each block
#      displacements  - displacement of each block in multiples of oldtype
#
# NOTE: We want the resulting values of b[] to be {6.0 7.0 8.0 9.0 13.0 14.0}.

# TODO: fill in the values for blocklengths
blocklengths  = [None, None]

# TODO: fill in the values for the displacements
displacements = [None, None]

# TODO: create the indexed data type

# TODO: commit the new derived datatype

# =========================================================================

if rank == 0:
    for i in range(1, numtasks):
        # task 0 sends one element of indextype to all tasks
        comm.Send([a, 1, indextype], dest=i, tag=tag)
    # copy indexed elements locally
    b[0:4] = a[5:9]
    b[4:6] = a[12:14]
else:
    # TODO: receive into b
    pass

print(f"rank= {rank}  b= {b[0]:.1f} {b[1]:.1f} {b[2]:.1f} {b[3]:.1f} {b[4]:.1f} {b[5]:.1f}")

# TODO: free the derived datatype
