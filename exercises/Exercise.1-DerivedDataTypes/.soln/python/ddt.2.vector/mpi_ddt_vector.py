from mpi4py import MPI
import numpy as np

SIZE = 4

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
numtasks = comm.Get_size()
source = 0
tag = 1

a = np.array([[ 1.0,  2.0,  3.0,  4.0],
              [ 5.0,  6.0,  7.0,  8.0],
              [ 9.0, 10.0, 11.0, 12.0],
              [13.0, 14.0, 15.0, 16.0]], dtype='f')
b = np.empty(SIZE, dtype='f')

# =========================================================================
# Step 1. Create an MPI Vector Type
#    MPI.Datatype.Create_vector(count, blocklength, stride)
#      count       - number of blocks
#      blocklength - number of elements in each block
#      stride      - number of elements between start of each block
columntype = MPI.FLOAT.Create_vector(SIZE, 1, SIZE)
columntype.Commit()
# =========================================================================

if numtasks == SIZE:
    # =========================================================================
    # Step 2. Send a vector data type.
    #   a.ravel()[i:] starts the buffer at column i (flat offset i),
    #   mirroring C's &a[0][i]. The vector type then strides through
    #   the row-major data to extract column i.
    if rank == 0:
        for i in range(1, numtasks):
            comm.Send([a.ravel()[i:], 1, columntype], dest=i, tag=tag)
        # Copy column 0 locally instead of sending to self
        b[:] = a[:, 0]
    else:
        comm.Recv([b, SIZE, MPI.FLOAT], source=source, tag=tag)
    # =========================================================================

    print(f"rank= {rank}  b= {b[0]:.1f} {b[1]:.1f} {b[2]:.1f} {b[3]:.1f}")
else:
    print(f"Must specify {SIZE} processors. Terminating.")

columntype.Free()
