#
#  This file is part of MUMPS 5.1.2, released
#  on Mon Oct  2 07:37:01 UTC 2017
#
# These settings for a PC under Debian/linux with standard packages :
# metis (parmetis), scotch (ptscotch), openmpi, gfortran

# packages installation : 
# apt-get install libmetis-dev libparmetis-dev libscotch-dev libptscotch-dev libatlas-base-dev openmpi-bin libopenmpi-dev lapack-dev

# Begin orderings
ISCOTCH    = -I/opt/aster146p/public/metis-5.1.0/include -I/opt/parmetis-4.0.3/include -I/opt/scotch-6.0.4/include

#LSCOTCH   = -L$(LSCOTCHDIR) -lptesmumps -lptscotch -lptscotcherr
LSCOTCH    = -L/opt/aster146p/public/metis-5.1.0/lib -L/opt/parmetis-4.0.3/lib -L/opt/scotch-6.0.4/lib -L/opt/scalapack/lib -Wl,-Bdynamic -lesmumps -lptscotch -lptscotcherr -lptscotcherrexit -lscotch -lscotcherr -lscotcherrexit 

LPORDDIR = $(topdir)/PORD/lib/
IPORD    = -I$(topdir)/PORD/include/
LPORD    = -L$(LPORDDIR) -lpord

# LMETISDIR = /usr/lib 
#IMETIS    = -I/usr/include/parmetis
# IMETIS    = -I/usr/include/metis

# LMETIS    = -L$(LMETISDIR) -lparmetis -lmetis
LMETIS    = -L/opt/aster146p/public/metis-5.1.0/lib -L/opt/parmetis-4.0.3/lib -L/opt/scotch-6.0.4/lib -L/opt/scalapack/lib -Wl,-Bdynamic -lparmetis  -Wl,-Bdynamic -lmetis  

# Corresponding variables reused later
#ORDERINGSF = -Dmetis -Dpord -Dparmetis -Dscotch -Dptscotch
ORDERINGSF  = -Dpord -Dmetis -Dparmetis -Dscotch -Dptscotch
ORDERINGSC  = $(ORDERINGSF)

LORDERINGS = $(LMETIS) $(LPORD) $(LSCOTCH)
IORDERINGSF = $(ISCOTCH)
IORDERINGSC = $(IMETIS) $(IPORD) $(ISCOTCH)
# End orderings
################################################################################

PLAT    =
LIBEXT  = .a
OUTC    = -o 
OUTF    = -o 
RM = /bin/rm -f
CC      = mpicc
FC      = mpif90
FL      = mpif90
AR      = /usr/bin/ar rcs 
RANLIB = echo
# LAPACK = -llapack
# SCALAP  = -lscalapack-openmpi -lblacs-openmpi  -lblacsF77init-openmpi -lblacsCinit-openmpi

INCPAR = -I/opt/aster146p/public/metis-5.1.0/include -I/opt/parmetis-4.0.3/include -I/opt/scotch-6.0.4/include
LIBPAR =

INCSEQ = -I$(topdir)/libseq
LIBSEQ = -L$(topdir)/libseq -lmpiseq

LIBBLAS = -L/opt/aster146p/public/metis-5.1.0/lib -L/opt/parmetis-4.0.3/lib -L/opt/scotch-6.0.4/lib -L/opt/scalapack/lib -Wl,-Bdynamic -lpthread -lm -lblas -llapack -lscalapack -L/opt/OpenBLAS/lib -lopenblas 
LIBOTHERS =  -L/opt/aster146p/public/metis-5.1.0/lib -L/opt/parmetis-4.0.3/lib -L/opt/scotch-6.0.4/lib -L/opt/scalapack/lib -Wl,-Bdynamic -ldl -lutil -lpthread   

#Preprocessor defs for calling Fortran from C (-DAdd_ or -DAdd__ or -DUPPER)
CDEFS   = -D_USE_MPI=1 -DHAVE_MPI=1 -D_USE_OPENMP=1 -DHAVE_METIS_H=1 -D_HAVE_METIS=1 -DHAVE_METIS=1 -DHAVE_PARMETIS_H=1 -D_HAVE_PARMETIS=1 -DHAVE_PARMETIS=1 -DHAVE_STDIO_H=1 -DHAVE_SCOTCH=1 -DAdd_ -Dmetis -Dparmetis

#Begin Optimized options
# uncomment -fopenmp in lines below to benefit from OpenMP
OPTF    = -O -fPIC -DPORD_INTSIZE64 -fopenmp
OPTL    = -O -Wl,--export-dynamic -fopenmp -L/opt/aster146p/public/metis-5.1.0/lib -L/opt/parmetis-4.0.3/lib -L/opt/scotch-6.0.4/lib -L/opt/scalapack/lib -L/usr/lib -L/usr/lib/x86_64-linux-gnu/openmpi/lib -L/opt/aster146p/public/metis-5.1.0/lib -L/opt/parmetis-4.0.3/lib -L/opt/scotch-6.0.4/lib -L/opt/scalapack/lib -L/usr//lib -L/usr/lib/x86_64-linux-gnu/openmpi/lib -Lnow -Lrelro -L/opt/aster146p/public/metis-5.1.0/lib -L/opt/parmetis-4.0.3/lib -L/opt/scotch-6.0.4/lib -L/opt/scalapack/lib -L/usr//lib -L/usr/lib/x86_64-linux-gnu/openmpi/lib -L/usr/lib/gcc/x86_64-linux-gnu/7 -L/usr/lib/gcc/x86_64-linux-gnu/7/../../../x86_64-linux-gnu -L/usr/lib/gcc/x86_64-linux-gnu/7/../../../../lib -L/lib/x86_64-linux-gnu -L/lib/../lib -L/usr/lib/x86_64-linux-gnu -L/usr/lib/../lib -L/usr/lib/gcc/x86_64-linux-gnu/7/../../.. -lmpi_usempif08 -lmpi_usempi_ignore_tkr -lmpi_mpifh -lmpi -lgfortran -lquadmath -lpthread -L/opt/aster146p/public/metis-5.1.0/lib -L/opt/parmetis-4.0.3/lib -L/opt/scotch-6.0.4/lib -L/opt/scalapack/lib -L/usr//lib -L/usr/lib/x86_64-linux-gnu/openmpi/lib
OPTC    = -O -fPIC -fopenmp
#End Optimized options
 
INCS = $(INCPAR)
LIBS = $(LIBPAR)
LIBSEQNEEDED =
