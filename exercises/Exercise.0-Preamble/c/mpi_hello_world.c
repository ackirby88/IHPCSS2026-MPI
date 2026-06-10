#include <mpi.h>
#include <stdio.h>

int main(int argc, char *argv[])  {
    int numtasks, rank;
    char processor_name[MPI_MAX_PROCESSOR_NAME];
    int name_len;

    MPI_Init(&argc,&argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &numtasks);
    MPI_Get_processor_name(processor_name, &name_len);
    
    printf("Hello world from rank %d out of %d on processor %s\n",
           rank, numtasks, processor_name);

    MPI_Finalize();
    return 0;
}
