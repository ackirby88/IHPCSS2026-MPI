program contiguous
    use mpi
    implicit none

    integer :: ierr, rank, numtasks, name_len
    character(len=MPI_MAX_PROCESSOR_NAME) :: processor_name
    
    call MPI_INIT(ierr)
    call MPI_COMM_RANK(MPI_COMM_WORLD, rank, ierr)
    call MPI_COMM_SIZE(MPI_COMM_WORLD, numtasks, ierr)
    call MPI_Get_processor_name(processor_name, name_len, ierr)

    print *, 'Hello world from rank', rank, 'out of', numtasks, 'on processor', trim(processor_name)

    call MPI_FINALIZE(ierr)

end program
