from mpi4py import MPI
import numpy as np

NELEM = 25

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
numtasks = comm.Get_size()
source = 0
tag = 1

particle_dt = np.dtype([('x',        'f4'),
                        ('y',        'f4'),
                        ('z',        'f4'),
                        ('velocity', 'f4'),
                        ('n',        'i4'),
                        ('type',     'i4')])

particles = np.zeros(NELEM, dtype=particle_dt)
p         = np.zeros(NELEM, dtype=particle_dt)

# =========================================================================
# Step 1. Create an MPI Struct Type
#    MPI.Datatype.Create_struct(blocklengths, displacements, datatypes)
#      blocklengths  - number of elements in each block
#      displacements - byte displacement of each block
#      datatypes     - MPI datatype of each block
#
# Setup description of the 4 MPI_FLOAT fields x, y, z, velocity
float_extent = MPI.FLOAT.Get_size()
offsets    = [0, 4 * float_extent]
blockcounts = [4, 2]
oldtypes   = [MPI.FLOAT, MPI.INT]

particletype = MPI.Datatype.Create_struct(blockcounts, offsets, oldtypes)
particletype.Commit()
# =========================================================================

if rank == 0:
    for i in range(NELEM):
        particles[i]['x']        =  i * 1.0
        particles[i]['y']        =  i * -1.0
        particles[i]['z']        =  i * 1.0
        particles[i]['velocity'] =  0.25
        particles[i]['n']        =  i
        particles[i]['type']     =  i % 2

    # task 0 sends to all tasks (skip self to avoid deadlock)
    for i in range(1, numtasks):
        comm.Send([particles, NELEM, particletype], dest=i, tag=tag)
    # copy locally
    p[:] = particles
else:
    comm.Recv([p, NELEM, particletype], source=source, tag=tag)

print(f"rank= {rank}   {p[3]['x']:.2f} {p[3]['y']:.2f} {p[3]['z']:.2f} "
      f"{p[3]['velocity']:.2f} {p[3]['n']} {p[3]['type']}")

particletype.Free()
