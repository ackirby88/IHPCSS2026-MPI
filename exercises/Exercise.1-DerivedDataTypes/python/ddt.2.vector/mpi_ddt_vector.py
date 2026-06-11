from mpi4py import MPI
import numpy as np

SIZE = 4

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
numtasks = comm.Get_size()
source = 0
tag = 1

if rank == 0:
    a = np.array([[ 1.0,  2.0,  3.0,  4.0],
                  [ 5.0,  6.0,  7.0,  8.0],
                  [ 9.0, 10.0, 11.0, 12.0],
                  [13.0, 14.0, 15.0, 16.0]], dtype='f')
else:
    a = None

b = np.empty(SIZE, dtype='f')

if numtasks == SIZE:
    # =========================================================================
    # Step 1. Create an MPI Vector Type
    #    MPI.Datatype.Create_vector(count, blocklength, stride)
    #      count       - number of blocks
    #      blocklength - number of elements in each block
    #      stride      - number of elements between start of each block

    # TODO: create the vector data type

    # TODO: commit the new derived datatype

    # =========================================================================

    if rank == 0:
        for i in range(1, numtasks):
            # =====================================================================
            # Step 2. Send a vector data type.
            #   HINT: a.ravel()[i:] starts the buffer at column i (flat offset i),
            #         mirroring C's &a[0][i]. The vector type then strides through
            #         the row-major data to extract column i.
            # TODO: send each COLUMN i of array 'a' to rank i using the derived data type.

            # =====================================================================
        # TODO: copy column 0 locally into b
    else:
        # TODO: receive into b
        pass

    print(f"rank= {rank}  b= {b[0]:.1f} {b[1]:.1f} {b[2]:.1f} {b[3]:.1f}")
else:
    if rank == 0:
        print(f"Must specify {SIZE} processors. Terminating.")

# TODO: free the derived datatype
