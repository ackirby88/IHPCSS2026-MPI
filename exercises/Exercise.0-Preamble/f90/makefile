FC = mpif90
CFLAGS = -g
EXEC = mpi_hello_world

all:
	$(FC) $(FFLAGS) mpi_hello_world.f90 -o $(EXEC)
clean:
	@echo "*** Clean : removing object files"
	@( $(RM) *.o *.mod *~)
	@( $(RM) $(EXEC))
