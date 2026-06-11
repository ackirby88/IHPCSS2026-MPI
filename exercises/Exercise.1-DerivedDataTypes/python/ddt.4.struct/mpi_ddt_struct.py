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

# TODO: setup description of the 4 MPI_FLOAT fields x, y, z, velocity
#   offsets[0]    = TODO
#   blockcounts[0] = TODO
#   oldtypes[0]   = TODO

# TODO: setup description of the 2 MPI_INT fields n, type.
#   We first figure the offset by getting the size of MPI_FLOAT
#   float_extent  = MPI.FLOAT.Get_size()
#   offsets[1]    = TODO  HINT: how many 'extent's do we need?
#   blockcounts[1] = TODO
#   oldtypes[1]   = TODO

# TODO: create the struct data type

# TODO: commit the new derived datatype

# =========================================================================

if rank == 0:
    for i in range(NELEM):
        particles[i]['x']        =  i * 1.0
        particles[i]['y']        =  i * -1.0
        particles[i]['z']        =  i * 1.0
        particles[i]['velocity'] =  0.25
        particles[i]['n']        =  i
        particles[i]['type']     =  i % 2

    for i in range(1, numtasks):
        # TODO: send particles to rank i using the derived data type

        pass
    # copy locally
    p[:] = particles
else:
    # TODO: receive into p
    pass

print(f"rank= {rank}   {p[3]['x']:.2f} {p[3]['y']:.2f} {p[3]['z']:.2f} "
      f"{p[3]['velocity']:.2f} {p[3]['n']} {p[3]['type']}")

# TODO: free the derived datatype
