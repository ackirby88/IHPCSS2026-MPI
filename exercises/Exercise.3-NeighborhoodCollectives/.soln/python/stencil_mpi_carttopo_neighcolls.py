from mpi4py import MPI
import numpy as np
import sys
import struct

def printarr_par(iteration, array, n, px, py, rx, ry, bx, by, offx, offy, comm):
    myrank = comm.Get_rank()
    fname  = f'./output-{iteration}.bmp'

    fh = MPI.File.Open(comm, fname,
                       MPI.MODE_SEQUENTIAL | MPI.MODE_CREATE | MPI.MODE_WRONLY)

    if myrank == 0:
        linesize_full = n * 3
        padding_full  = (4 - linesize_full % 4) % 4
        bmp_data_size = n * (linesize_full + padding_full)
        hdr = struct.pack('<2sIHHI',
                          b'BM',
                          54 + bmp_data_size,
                          0xFE, 0xFE,
                          54)
        hdr += struct.pack('<IiiHHIIiiII',
                           40,
                           n, n,
                           1, 24,
                           0,
                           bmp_data_size,
                           n, n,
                           0, 0)
        fh.Write_shared(np.frombuffer(hdr, dtype=np.uint8))

    linesize = bx * 3
    padding  = (n * 3) % 4 if (rx + 1 == px) else 0
    myline   = np.zeros(linesize + padding, dtype=np.uint8)

    xcnt    = 0
    ycnt    = n
    my_ycnt = 0

    while ycnt >= 0:
        comm.Barrier()
        if xcnt == offx and offy <= ycnt < offy + by:
            row = by - my_ycnt
            for col in range(bx):
                val = array[col + 1, row]
                rgb = min(255, max(0, int(255.0 * val)))
                if col == 0 or col == bx - 1 or my_ycnt == 0 or my_ycnt == by - 1:
                    rgb = 255
                myline[col * 3 + 0] = 0
                myline[col * 3 + 1] = 0
                myline[col * 3 + 2] = rgb
            my_ycnt += 1
            fh.Write_shared(myline)
        xcnt += bx
        if xcnt >= n:
            xcnt = 0
            ycnt -= 1

    fh.Close()


def main():
    comm = MPI.COMM_WORLD
    r    = comm.Get_rank()
    p    = comm.Get_size()

    if r == 0:
        if len(sys.argv) < 4:
            print("usage: stencil_mpi <n> <energy> <niters>")
            comm.Abort(1)
        n      = int(sys.argv[1])
        energy = int(sys.argv[2])
        niters = int(sys.argv[3])
        args   = np.array([n, energy, niters], dtype=np.int32)
    else:
        args = np.empty(3, dtype=np.int32)
    comm.Bcast(args, root=0)
    n, energy, niters = int(args[0]), int(args[1]), int(args[2])

    # Compute 2D domain decomposition
    pdims = MPI.Compute_dims(p, [0, 0])
    px, py = pdims[0], pdims[1]

    # Create Cartesian topology
    topocomm = comm.Create_cart(dims=[px, py], periods=[False, False], reorder=False)

    coords = topocomm.Get_coords(r)
    rx, ry = coords[0], coords[1]

    west,  east  = topocomm.Shift(0, 1)
    north, south = topocomm.Shift(1, 1)

    bx   = n // px
    by   = n // py
    offx = rx * bx
    offy = ry * by

    # Working arrays with 1-wide halo
    aold = np.zeros((bx + 2, by + 2), dtype=np.float64)
    anew = np.zeros((bx + 2, by + 2), dtype=np.float64)

    # Heat sources
    nsources = 3
    sources  = [(n // 2, n // 2), (n // 3, n // 3), (n * 4 // 5, n * 8 // 9)]
    locsources = []
    for sx, sy in sources:
        locx = sx - offx
        locy = sy - offy
        if 0 <= locx < bx and 0 <= locy < by:
            locsources.append((locx + 1, locy + 1))

    # Communication buffers: [west:by] [east:by] [north:bx] [south:bx]
    sbuf = np.zeros(2 * by + 2 * bx, dtype=np.float64)
    rbuf = np.zeros(2 * by + 2 * bx, dtype=np.float64)

    counts = np.array([by, by, bx, bx], dtype=np.int32)
    displs = np.array([0, by, 2 * by, 2 * by + bx], dtype=np.int32)

    for iteration in range(niters):
        # Refresh heat sources
        for lx, ly in locsources:
            aold[lx, ly] += energy

        # Pack send buffer: west col, east col, north row, south row
        sbuf[0:by]            = aold[1,  1:by+1]
        sbuf[by:2*by]         = aold[bx, 1:by+1]
        sbuf[2*by:2*by+bx]    = aold[1:bx+1, 1]
        sbuf[2*by+bx:2*by+2*bx] = aold[1:bx+1, by]

        # =====================================================================
        # Step 1. Nonblocking neighborhood collective
        #
        #   topocomm.Ineighbor_alltoallv(sendbuf, recvbuf,
        #                                sendcounts, sdispls, sendtype,
        #                                recvcounts, rdispls, recvtype)
        #
        #   Neighbor order for 2D Cart: [dim0-, dim0+, dim1-, dim1+]
        #                              = [west,  east,  north, south]
        req = topocomm.Ineighbor_alltoallv(
            [sbuf, counts, displs, MPI.DOUBLE],
            [rbuf, counts, displs, MPI.DOUBLE])
        req.Wait()
        # =====================================================================

        # Unpack receive buffer into halo zones
        aold[0,    1:by+1] = rbuf[0:by]
        aold[bx+1, 1:by+1] = rbuf[by:2*by]
        aold[1:bx+1, 0]    = rbuf[2*by:2*by+bx]
        aold[1:bx+1, by+1] = rbuf[2*by+bx:2*by+2*bx]

        # Update interior and accumulate heat
        anew[1:bx+1, 1:by+1] = (
            aold[1:bx+1, 1:by+1] / 2.0 +
            (aold[0:bx,   1:by+1] + aold[2:bx+2, 1:by+1] +
             aold[1:bx+1, 0:by]   + aold[1:bx+1, 2:by+2]) / 4.0 / 2.0
        )
        heat = np.sum(anew[1:bx+1, 1:by+1])

        aold, anew = anew, aold

        if iteration == niters - 1:
            printarr_par(iteration, anew, n, px, py, rx, ry, bx, by, offx, offy, topocomm)

    rheat = comm.allreduce(heat, op=MPI.SUM)
    if r == 0:
        print(f"[{r}] last heat: {rheat:.6f}")


if __name__ == '__main__':
    main()
