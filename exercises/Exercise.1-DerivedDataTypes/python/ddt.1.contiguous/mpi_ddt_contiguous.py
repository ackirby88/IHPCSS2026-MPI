from mpi4py import MPI
import numpy as np

SIZE = 4

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
numtasks = comm.Get_size()
source = 0
tag = 1

# Create the 2D array only on rank 0
if rank == 0:
    a = np.array([[ 1.0,  2.0,  3.0,  4.0],
                  [ 5.0,  6.0,  7.0,  8.0],
                  [ 9.0, 10.0, 11.0, 12.0],
                  [13.0, 14.0, 15.0, 16.0]], dtype='f')
else:
    a = None

# Prepare the destination buffer
b = np.empty(SIZE, dtype='f')

# Check that we have the correct number of processes
if numtasks == SIZE:
    # Create derived datatype: one row (contiguous SIZE floats)
    rowtype = MPI.FLOAT.Create_contiguous(SIZE)
    rowtype.Commit()

    if rank == 0:
        # Send each row i of a to process i
        for i in range(1, numtasks):
            comm.Send([a[i, :], rowtype], dest=i, tag=tag)
        # Copy row 0 locally
        b[:] = a[0, :]
    else:
        # Receive row into b
        comm.Recv([b, rowtype], source=source, tag=tag)

    print(f"rank= {rank}  b= {b[0]:.1f} {b[1]:.1f} {b[2]:.1f} {b[3]:.1f}")

    # Clean up
    rowtype.Free()
else:
    if rank == 0:
        print(f"Must specify {SIZE} processors. Terminating.")

