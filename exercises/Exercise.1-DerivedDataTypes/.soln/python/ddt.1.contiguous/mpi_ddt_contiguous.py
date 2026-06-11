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
# Step 1. Create an MPI Contiguous Type
#    MPI.Datatype.Create_contiguous(count)
#      count - replication count (non-negative integer)
rowtype = MPI.FLOAT.Create_contiguous(SIZE)
rowtype.Commit()
# =========================================================================

if numtasks == SIZE:
    # =====================================================================
    # Step 2. Send contiguous data type using MPI_Send.
    if rank == 0:
        # task 0 sends each ROW i to rank i (skip self to avoid deadlock)
        for i in range(1, numtasks):
            comm.Send([a[i, :], 1, rowtype], dest=i, tag=tag)
        # copy row 0 locally
        b[:] = a[0, :]
    else:
        comm.Recv([b, 1, rowtype], source=source, tag=tag)
    # =====================================================================

    print(f"rank= {rank}  b= {b[0]:.1f} {b[1]:.1f} {b[2]:.1f} {b[3]:.1f}")
else:
    print(f"Must specify {SIZE} processors. Terminating.")

rowtype.Free()
