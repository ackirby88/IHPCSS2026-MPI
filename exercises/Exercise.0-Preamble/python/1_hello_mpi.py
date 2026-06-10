from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
processor_name = MPI.Get_processor_name()

print(f"Hello world from rank {rank} out of {size} on processor {processor_name}")

