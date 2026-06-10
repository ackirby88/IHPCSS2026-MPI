CXX = mpicxx
CFLAGS = -g
EXEC = mpi_hello_world

all:
	$(CXX) $(CFLAGS) mpi_hello_world.c -o $(EXEC)
clean:
	@echo "*** Clean : removing object files"
	@( $(RM) *.o *.mod *~)
	@( $(RM) $(EXEC))
