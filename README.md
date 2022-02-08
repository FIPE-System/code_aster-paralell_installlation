# Installation of the parallel version of code_aster 14.6

## Operating System

I tried to install code_aster as parallel on Ubuntu 18.04 and Ubuntu 20.04, but both didn't work. I think it was because of the versions of the `openmpi-bin` package. Then I tried it with Debian 10 "buster" and I got it finally to work. 

> I recommend to install code_aster on Debian 10 "buster" (i used GNOME Desktop)

## Preparation

### Folder rights

``` bash
sudo chown "username" / opt 
```

### Prerequieries
> Installation for Ubuntu

| package            | version           |
| ------------------ | ----------------- |
| gcc                | 8.3.0             |
| g++                | 8.3.0             |
| gfortran           | 8.3.0             |
| cmake              | 3.13.4            |
| python3            | 3.7.3             |
| python3-dev        | 3.7.3             |
| python3-numpy      | 1.16.2            |
| tk                 | 8.6.9             |
| tcl                | 8.6.9             |
| bison              | 3.3.2             |
| flex               | 2.6.4-6.2         |
| liblapack-dev      | 3.8.0-2           |
| libblas-dev        | 3.8.0-2           |
| libboost-numpy-dev | 1.67.0.1          |
| libboost-all-dev   | 1.67.0.1          |
| zlib1g-dev         | 1:1.2.11.dfsg-1   |
| checkinstall       | 1.6.2             |
| openmpi-bin        | 3.1.3-11          |
| libx11-dev         | 2:1.6.7-1+deb10u2 |
| grace              | 1:5.1.25-6        |
| gettext            | 0.19.8.1-9        |
| swig               | 3.0.12-2          |
| libsuperlu-dev     | 5.2.1+dfsg1-4     |

> Best use the programm `Synaptic`, `Apper` or `Debian Package Search` for the installation process!

### Download of needed packages

> You will finde the packages in the github repository.

| package    | version | Latest version | Link                                                            |
| ---------- | ------- | -------------- | --------------------------------------------------------------- |
| Code_Aster | 14.6    | 14.6           | https://www.code-aster.org                                      |
| OpenBLAS   | 0.2.0   | 0.3.10         | https://github.com/xianyi/OpenBLAS/                             |
| ScaLAPACK  | 2.0.0   | 2.1.0          | http://www.netlib.org/scalapack/#_scalapack_installer_for_linux |
| Parmetis   | 4.0.3   | 4.0.3          | http://glaros.dtc.umn.edu/gkhome/metis/parmetis/download        |
| Petsc      | 3.9.4   | 3.14.2         | https://www.mcs.anl.gov/petsc/download/index.html               |

##  Installation

### OpenBLAS

``` bash
cd ~/software  
tar xvzf OpenBLAS-0.2.20.tar.gz   
cd OpenBLAS-0.2.20  
make NO_AFFINITY=1 USE_OPENMP=1   
make PREFIX=/opt/OpenBLAS install
```

Add OpenBLAS to the search path of the shared library.

``` bash
echo /opt/OpenBLAS/lib | sudo tee -a /etc/ld.so.conf.d/openblas.conf   
sudo ldconfig
```

> NOTE: use following code for installation in virtualbox

``` bash
make NO_AFFINITY=1 USE_OPENMP=1 TARGET=NEHALEM 
make PREFIX=/opt/OpenBLAS install
```
### Code_Aster with OpenBLAS

``` bash
cd ~/software  
tar xvzf aster-full-src-14.6.0-1.noarch.tar.gz  
cd aster-full-src-14.6.0
```

Then edit the contents of the setup.cfg file. Change `PREFER_COMPILER = GNU` to `PREFER_COMPILER = GNU_without_MATH` to specify the OpenBLAS you just installed for MATHLIB and change the `ASTER_ROOT` to `/opt/aster146p`

> Take the the file `setup.cfg` from the `config/aster` folder and replace the on in the `aster-full-src-14.6.0` folder.

Install it in / opt / aster.

``` bash
python3 setup.py install –-prefix=/opt/aster146p
```

You will be asked various questions on the way, but all will be yes. After the installation is complete, check the operation.

``` bash
/opt/aster146p/bin/as_run --vers=14.6 --test forma01a
```

If there is no error, it is OK. Create a host file for parallel computing. When forming a cluster with another machine, it seems better to add in the same format.

``` bash
echo "$HOSTNAME cpu=$(cat /proc/cpuinfo | grep processor | wc -l)" > /opt/aster146p/etc/codeaster/mpi_hostfile
```

**TIPS** : \[FAILED\] is displayed while running setup.py

In my environment, it seemed to occur when numpy was already installed using pip. In that case `pip3 uninstall numpy`, delete numpy completely with ⇒ `sudo apt install python-numpy`install numpy with ⇒ install Code_Aster, and try it.

### ScaLAPACK

Unzip the `scalapack_installer.tgz `

``` bash
tar xvzf scalapack_installer.tgz   
```

Rename the file `scalapack-2.0.0.tgz` from the config folder to `scalapack.tgz` and place it into to the folder `scalapack_installer/build`. The `build` folder must be created and doesn't exist.

``` bash  
cd scalapack_installer  
./setup.py --lapacklib=/opt/OpenBLAS/lib/libopenblas.a --mpicc=mpicc --mpif90=mpif90 --mpiincdir=/usr/lib/x86_64-linux-gnu/openmpi/include --ldflags_c=-fopenmp --ldflags_fc=-fopenmp --prefix=/opt/scalapack
```

At the end of the log

``` 
BLACS: error running BLACS test routines xCbtest  
BLACS: Command  -np 4 ./xCbtest  
stderr:  
**************************************  
/bin/sh: 1: -np: not found  
**************************************
```

Is displayed, but it is successful if the file `/opt/scalapack/lib/libscalapack.a` is created.

### Parmetis

First, unzip it.

``` bash
tar xvzf parmetis-4.0.3.tar.gz   
cd parmetis-4.0.3
```

Next, rewrite a part of the file of metis / include / metis.h and change it to compile in 64bit mode.

``` bash
sed -i -e 's/#define IDXTYPEWIDTH 32/#define IDXTYPEWIDTH 64/' metis/include/metis.h
```

Install it.

``` bash
make config prefix=/opt/parmetis-4.0.3   
make  
make install
```

Next, let’s check the operation.

``` bash
cd Graphs  
mpirun -np 4 /opt/parmetis-4.0.3/bin/parmetis rotor.graph 1 6 1 1 6 1
```

If there are no errors, it is successful. On my computer it shows:

``` 
finished reading file: rotor.graph  
[ 99617  1324862 24904 24905] [150] [ 0.000] [ 0.000]  
[ 53043   786820 13086 13479] [150] [ 0.000] [ 0.000]  
[ 28227   423280  6930  7105] [150] [ 0.000] [ 0.000]  
[ 15247   229550  3789  3843] [150] [ 0.000] [ 0.000]  
[  8304   124178  2044  2121] [150] [ 0.000] [ 0.000]  
[  4617    67768  1123  1170] [150] [ 0.000] [ 0.000]  
[  2625    36962   643   685] [150] [ 0.000] [ 0.001]  
[  1545    20152   360   408] [150] [ 0.000] [ 0.001]  
[   944    11180   221   252] [150] [ 0.000] [ 0.002]  
[   609     6230   131   161] [150] [ 0.000] [ 0.005]  
[   411     3612    78   116] [150] [ 0.000] [ 0.009]  
[   347     2916    72   100] [150] [ 0.000] [ 0.009]  
nvtxs:        347, cut:    24723, balance: 1.023   
nvtxs:        411, cut:    22942, balance: 1.050   
nvtxs:        609, cut:    22082, balance: 1.044   
nvtxs:        944, cut:    20501, balance: 1.054   
nvtxs:       1545, cut:    19350, balance: 1.052   
nvtxs:       2625, cut:    18147, balance: 1.049   
nvtxs:       4617, cut:    16956, balance: 1.051   
nvtxs:       8304, cut:    15689, balance: 1.049   
nvtxs:      15247, cut:    14632, balance: 1.049   
nvtxs:      28227, cut:    13468, balance: 1.050   
nvtxs:      53043, cut:    12628, balance: 1.048   
nvtxs:      99617, cut:    11288, balance: 1.047   
Final   6-way Cut:  11288   Balance: 1.047
```

### Scotch

First, move `scotch-6.0.4-aster7.tar.gz` included in `aster-full-src-14.6.0/SRC` to `/opt` and unzip it there.

``` bash 
cd /opt  
tar xvzf scotch-6.0.4-aster7.tar.gz  
cd scotch-6.0.4
```

Next, edit `src/Makefile.inc` contained in `src/` as follows.

> Thake the file from the config folder and replace the original `Makefile.inc`.

``` bash
EXE     =  
LIB     = .a  
OBJ     = .o  

MAKE    = make  
AR      = ar  
ARFLAGS = -ruv  
CAT     = cat  
CCS     = gcc  
CCP     = mpicc  
CCD     = gcc  
CFLAGS  = -O3 -fPIC -DINTSIZE64 -DCOMMON_FILE_COMPRESS_GZ -DCOMMON_PTHREAD -DCOMMON_RANDOM_FIXED_SEED -DSCOTCH_RENAME -DSCOTCH_RENAME_PARSER -Drestrict=__restrict  
CLIBFLAGS   =  
LDFLAGS = -fPIC -lz -lm -pthread -lrt  
CP      = cp  
LEX     = flex -Pscotchyy -olex.yy.c  
LN      = ln  
MKDIR   = mkdir  
MV      = mv  
RANLIB  = ranlib  
YACC    = bison -pscotchyy -y -b y
```

Build and check the operation.

``` bash
cd src  
make scotch esmumps ptscotch ptesmumps CCD=mpicc  
make check  
make ptcheck
```

### MUMPS

Again, move `mumps-5.1.2-aster6.tar.gz` from `/aster-full-src-14.6.0/SRC` to `/opt` and unzip it.

``` bash
cd /opt  
tar xvzf mumps-5.1.2-aster6.tar.gz  
cd mumps-5.1.2
```

Take the `Makefile.inc` from the config folder and place it in to `mumps-5.1.2` folder. You can edit it to suit your environment. But i diddn't and just took the settings as shown below.


``` bash
#  
# This file is part of MUMPS 5.0.1, changed to be configured by waf scripts  
# provided by the Code_Aster team.  
#  
#Begin orderings  
​  
# NOTE that PORD is distributed within MUMPS by default. If you would like to  
# use other orderings, you need to obtain the corresponding package and modify  
# the variables below accordingly.  
# For example, to have Metis available within MUMPS:  
#          1/ download Metis and compile it  
#          2/ uncomment (suppress # in first column) lines  
#             starting with LMETISDIR,  LMETIS  
#          3/ add -Dmetis in line ORDERINGSF  
#             ORDERINGSF  = -Dpord -Dmetis  
#          4/ Compile and install MUMPS  
#             make clean; make   (to clean up previous installation)  
#  
#          Metis/ParMetis and SCOTCH/PT-SCOTCH (ver 5.1 and later) orderings are now available for MUMPS.  
#  
​  
ISCOTCH    = -I/opt/aster146p/public/metis-5.1.0/include -I/opt/parmetis-4.0.3/include -I/opt/scotch-6.0.4/include  
# You have to choose one among the following two lines depending on  
# the type of analysis you want to perform. If you want to perform only  
# sequential analysis choose the first (remember to add -Dscotch in the ORDERINGSF  
# variable below); for both parallel and sequential analysis choose the second   
# line (remember to add -Dptscotch in the ORDERINGSF variable below)  
​  
LSCOTCH    = -L/opt/aster146p/public/metis-5.1.0/lib -L/opt/parmetis-4.0.3/lib -L/opt/scotch-6.0.4/lib -L/opt/scalapack/lib -Wl,-Bdynamic -lesmumps -lptscotch -lptscotcherr -lptscotcherrexit -lscotch -lscotcherr -lscotcherrexit   
#LSCOTCH    = -L$(SCOTCHDIR)/lib -lptesmumps -lptscotch -lptscotcherr  
​  
​  
LPORDDIR = $(topdir)/PORD/lib/  
IPORD    = -I$(topdir)/PORD/include/  
LPORD    = -L$(LPORDDIR) -lpord  
​  
#IMETIS    = # Metis doesn't need include files (Fortran interface avail.)  
# You have to choose one among the following two lines depending on  
# the type of analysis you want to perform. If you want to perform only  
# sequential analysis choose the first (remember to add -Dmetis in the ORDERINGSF  
# variable below); for both parallel and sequential analysis choose the second   
# line (remember to add -Dparmetis in the ORDERINGSF variable below)  
​  
LMETIS    = -L/opt/aster146p/public/metis-5.1.0/lib -L/opt/parmetis-4.0.3/lib -L/opt/scotch-6.0.4/lib -L/opt/scalapack/lib -Wl,-Bdynamic -lparmetis  -Wl,-Bdynamic -lmetis    
#LMETIS    = -L$(LMETISDIR) -lparmetis -lmetis  
​  
# The following variables will be used in the compilation process.  
# Please note that -Dptscotch and -Dparmetis imply -Dscotch and -Dmetis respectively.  
#ORDERINGSF = -Dscotch -Dmetis -Dpord -Dptscotch -Dparmetis  
ORDERINGSF  = -Dpord -Dmetis -Dparmetis -Dscotch -Dptscotch  
ORDERINGSC  = $(ORDERINGSF)  
​  
LORDERINGS = $(LMETIS) $(LPORD) $(LSCOTCH)  
IORDERINGSF = $(ISCOTCH)  
IORDERINGSC = $(IMETIS) $(IPORD) $(ISCOTCH)  
​  
#End orderings  
########################################################################  
################################################################################  
​  
PLAT    =  
LIBEXT  = .a  
OUTC    = -o   
OUTF    = -o   
RM      = /bin/rm -f  
CC      = mpicc  
FC      = mpif90  
FL      = mpif90  
# WARNING: AR must ends with a blank space!  
AR      = /usr/bin/ar rcs   
#  
RANLIB  = echo  
​  
#  
INCPAR = -I/opt/aster146p/public/metis-5.1.0/include -I/opt/parmetis-4.0.3/include -I/opt/scotch-6.0.4/include  
LIBPAR =   
#  
INCSEQ = -I$(topdir)/libseq  
LIBSEQ = -L$(topdir)/libseq -lmpiseq  
​  
#  
LIBBLAS = -L/opt/aster146p/public/metis-5.1.0/lib -L/opt/parmetis-4.0.3/lib -L/opt/scotch-6.0.4/lib -L/opt/scalapack/lib -Wl,-Bdynamic -lpthread -lm -lblas -llapack -lscalapack -L/opt/OpenBLAS/lib -lopenblas   
LIBOTHERS =  -L/opt/aster146p/public/metis-5.1.0/lib -L/opt/parmetis-4.0.3/lib -L/opt/scotch-6.0.4/lib -L/opt/scalapack/lib -Wl,-Bdynamic -ldl -lutil -lpthread     
#Preprocessor defs for calling Fortran from C (-DAdd_ or -DAdd__ or -DUPPER)  
CDEFS   = -D_USE_MPI=1 -DHAVE_MPI=1 -D_USE_OPENMP=1 -DHAVE_METIS_H=1 -D_HAVE_METIS=1 -DHAVE_METIS=1 -DHAVE_PARMETIS_H=1 -D_HAVE_PARMETIS=1 -DHAVE_PARMETIS=1 -DHAVE_STDIO_H=1 -DHAVE_SCOTCH=1 -DAdd_ -Dmetis -Dparmetis  
​  
#Begin Optimized options  
OPTF    = -O -fPIC -DPORD_INTSIZE64 -fopenmp  
OPTL    = -O -Wl,--export-dynamic -fopenmp -L/opt/aster146p/public/metis-5.1.0/lib -L/opt/parmetis-4.0.3/lib -L/opt/scotch-6.0.4/lib -L/opt/scalapack/lib -L/usr/lib -L/usr/lib/x86_64-linux-gnu/openmpi/lib -L/opt/aster146p/public/metis-5.1.0/lib -L/opt/parmetis-4.0.3/lib -L/opt/scotch-6.0.4/lib -L/opt/scalapack/lib -L/usr//lib -L/usr/lib/x86_64-linux-gnu/openmpi/lib -Lnow -Lrelro -L/opt/aster146p/public/metis-5.1.0/lib -L/opt/parmetis-4.0.3/lib -L/opt/scotch-6.0.4/lib -L/opt/scalapack/lib -L/usr//lib -L/usr/lib/x86_64-linux-gnu/openmpi/lib -L/usr/lib/gcc/x86_64-linux-gnu/7 -L/usr/lib/gcc/x86_64-linux-gnu/7/../../../x86_64-linux-gnu -L/usr/lib/gcc/x86_64-linux-gnu/7/../../../../lib -L/lib/x86_64-linux-gnu -L/lib/../lib -L/usr/lib/x86_64-linux-gnu -L/usr/lib/../lib -L/usr/lib/gcc/x86_64-linux-gnu/7/../../.. -lmpi_usempif08 -lmpi_usempi_ignore_tkr -lmpi_mpifh -lmpi -lgfortran -lquadmath -lpthread -L/opt/aster146p/public/metis-5.1.0/lib -L/opt/parmetis-4.0.3/lib -L/opt/scotch-6.0.4/lib -L/opt/scalapack/lib -L/usr//lib -L/usr/lib/x86_64-linux-gnu/openmpi/lib  
OPTC    = -O -fPIC -fopenmp  
#End Optimized options  
​  
INCS = $(INCPAR)  
LIBS = $(LIBPAR)  
LIBSEQNEEDED =
```

Build and check the operation.

``` bash 
make all  
cd examples  
mpirun -np 4 ./ssimpletest < input_simpletest_real
```

If there is no error, it is OK. On my computer, it shows:

``` bash
Entering SMUMPS 5.1.2 with JOB, N, NNZ =   6           5             12  
      executing #MPI =      4 and #OMP =     16  
​  
 =================================================  
 MUMPS compiled with option -Dmetis  
 MUMPS compiled with option -Dparmetis  
 MUMPS compiled with option -Dptscotch  
 MUMPS compiled with option -Dscotch  
 =================================================  
L U Solver for unsymmetric matrices  
Type of parallelism: Working host  
​  
 ****** ANALYSIS STEP ********  
​  
 ... Structural symmetry (in percent)=   92  
 Average density of rows/columns =    2  
 ... No column permutation  
 Ordering based on AMF   
​  
Leaving analysis phase with  ...  
INFOG(1)                                       =               0  
INFOG(2)                                       =               0  
 -- (20) Number of entries in factors (estim.) =              15  
 --  (3) Storage of factors  (REAL, estimated) =              15  
 --  (4) Storage of factors  (INT , estimated) =              65  
 --  (5) Maximum frontal size      (estimated) =               3  
 --  (6) Number of nodes in the tree           =               3  
 -- (32) Type of analysis effectively used     =               1  
 --  (7) Ordering option effectively used      =               2  
ICNTL(6) Maximum transversal option            =               0  
ICNTL(7) Pivot order option                    =               7  
Percentage of memory relaxation (effective)    =              20  
Number of level 2 nodes                        =               0  
Number of split nodes                          =               0  
RINFOG(1) Operations during elimination (estim)=   1.900D+01  
 ** Rank of proc needing largest memory in IC facto        :               0  
 ** Estimated corresponding MBYTES for IC facto            :               1  
 ** Estimated avg. MBYTES per work. proc at facto (IC)     :               1  
 ** TOTAL     space in MBYTES for IC factorization         :               4  
 ** Rank of proc needing largest memory for OOC facto      :               0  
 ** Estimated corresponding MBYTES for OOC facto           :               1  
 ** Estimated avg. MBYTES per work. proc at facto (OOC)    :               1  
 ** TOTAL     space in MBYTES for OOC factorization        :               4  
 ELAPSED TIME IN ANALYSIS DRIVER=       0.0007  
​  
 ****** FACTORIZATION STEP ********  
​  
​  
 GLOBAL STATISTICS PRIOR NUMERICAL FACTORIZATION ...  
 NUMBER OF WORKING PROCESSES              =               4  
 OUT-OF-CORE OPTION (ICNTL(22))           =               0  
 REAL SPACE FOR FACTORS                   =              15  
 INTEGER SPACE FOR FACTORS                =              65  
 MAXIMUM FRONTAL SIZE (ESTIMATED)         =               3  
 NUMBER OF NODES IN THE TREE              =               3  
 MEMORY ALLOWED (MB -- 0: N/A )           =               0  
 RELATIVE THRESHOLD FOR PIVOTING, CNTL(1) =      0.1000D-01  
 Convergence error after scaling for ONE-NORM (option 7/8)   = 0.38D+00  
 Maximum effective relaxed size of S              =             475  
 Average effective relaxed size of S              =             467  
 ELAPSED TIME FOR MATRIX DISTRIBUTION      =      0.0000  
 ** Memory relaxation parameter ( ICNTL(14)  )            :        20  
 ** Rank of processor needing largest memory in facto     :         0  
 ** Space in MBYTES used by this processor for facto      :         1  
 ** Avg. Space in MBYTES per working proc during facto    :         1  
​  
 ELAPSED TIME FOR FACTORIZATION           =      0.0004  
 Maximum effective space used in S     (KEEP8(67))               12  
 Average effective space used in S     (KEEP8(67))                4  
 ** EFF Min: Rank of processor needing largest memory :         0  
 ** EFF Min: Space in MBYTES used by this processor   :         1  
 ** EFF Min: Avg. Space in MBYTES per working proc    :         1  
​  
 GLOBAL STATISTICS   
 RINFOG(2)  OPERATIONS IN NODE ASSEMBLY   = 2.000D+00  
 ------(3)  OPERATIONS IN NODE ELIMINATION= 1.900D+01  
 INFOG (9)  REAL SPACE FOR FACTORS        =              15  
 INFOG(10)  INTEGER SPACE FOR FACTORS     =              65  
 INFOG(11)  MAXIMUM FRONT SIZE            =               3  
 INFOG(29)  NUMBER OF ENTRIES IN FACTORS  =              15  
 INFOG(12)  NUMBER OF OFF DIAGONAL PIVOTS =               0  
 INFOG(13)  NUMBER OF DELAYED PIVOTS      =               0  
 INFOG(14)  NUMBER OF MEMORY COMPRESS     =               0  
 ELAPSED TIME IN FACTORIZATION DRIVER=       0.0010  
​  
​  
 ****** SOLVE & CHECK STEP ********  
​  
​  
 STATISTICS PRIOR SOLVE PHASE     ...........  
 NUMBER OF RIGHT-HAND-SIDES                    =           1  
 BLOCKING FACTOR FOR MULTIPLE RHS              =           1  
 ICNTL (9)                                     =           1  
  --- (10)                                     =           0  
  --- (11)                                     =           0  
  --- (20)                                     =           0  
  --- (21)                                     =           0  
  --- (30)                                     =           0  
 ** Rank of processor needing largest memory in solve     :         0  
 ** Space in MBYTES used by this processor for solve      :         0  
 ** Avg. Space in MBYTES per working proc during solve    :         0  
​  
 Global statistics  
 TIME to build/scatter RHS        =       0.000038  
 TIME in solution step (fwd/bwd)  =       0.000093  
  .. TIME in forward (fwd) step   =          0.000057  
  .. TIME in backward (bwd) step  =          0.000031  
 TIME to gather solution(cent.sol)=       0.000004  
 TIME to copy/scale RHS (dist.sol)=       0.000000  
 ELAPSED TIME IN SOLVE DRIVER=       0.0004  
  Solution is    1.00000060       2.00000048       3.00000000       4.00000000       4.99999905      
​  
Entering SMUMPS 5.1.2 with JOB =  -2  
      executing #MPI =      4 and #OMP =     16
```

### Petsc


First copy the packages `hypre_2.14.0.orig.tar.gz` and `petsc-pkg-ml-b12e8907eb59.zip` and place them into the `/opt` folder **NO UNZIPING**

Then, unzip the `petsc-3.9.4` it into the `/opt` folder.

``` 
cd /opt  
cd petsc-3.9.4
```



Then open the file located at `/opt/petsc-3.9.4/config/BuildSystem/config/packages/metis.py`

and next, comment out lines 43-48. It will be the following part.

> Again take the one from the confog file and replace it!

metis.py

``` 
def configureLibrary(self):  
    config.package.Package.configureLibrary(self)  
    oldFlags = self.compilers.CPPFLAGS  
    self.compilers.CPPFLAGS += ' '+self.headers.toString(self.include)  
#    if not self.checkCompile('#include "metis.h"', '#if (IDXTYPEWIDTH != '+ str(self.getDefaultIndexSize())+')\n#error incompatible IDXTYPEWIDTH\n#endif'):  
#      if self.defaultIndexSize == 64:  
#        msg= '--with-64-bit-indices option requires a metis build with IDXTYPEWIDTH=64.\n'  
#      else:  
#        msg= 'IDXTYPEWIDTH=64 metis build appears to be specified for a default 32-bit-indices build of PETSc.\n'  
#      raise RuntimeError('Metis specified is incompatible!\n'+msg+'Suggest using --download-metis for a compatible metis')  

    self.compilers.CPPFLAGS = oldFlags  
    return
```

In addition, register the OpenMPI library in LD_LIBRARY_PATH.

>I also placed / copied this in to my `~/bashrc` file.

``` bash
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/openmpi/lib/:$LD_LIBRARY_PATH
```

and then execute configure.


``` bash 
./configure --with-debugging=0 COPTFLAGS=-O CXXOPTFLAGS=-O FOPTFLAGS=-O --with-shared-libraries=0 --with-scalapack-dir=/opt/scalapack --PETSC_ARCH=linux-metis-mumps --with-metis-dir=/opt/aster146p/public/metis-5.1.0 --with-parmetis-dir=/opt/parmetis-4.0.3 --with-ptscotch-dir=/opt/scotch-6.0.4 --LIBS="-lgomp" --with-mumps-dir=/opt/mumps-5.1.2 -with-x=0 --with-blas-lapack-lib=[/opt/OpenBLAS/lib/libopenblas.a] --download-hypre=/opt/hypre_2.14.0.orig.tar.gz --download-ml=/opt/petsc-pkg-ml-b12e8907eb59.zip
```

It shows on my computer:

```
PETSc:  
  PETSC_ARCH: linux-metis-mumps  
  PETSC_DIR: /opt/petsc-3.9.4  
  Scalar type: real  
  Precision: double  
  Clanguage: C  
  Integer size: 32  
  shared libraries: disabled  
  Memory alignment: 16  
========================================================================= 
 Configure stage complete. Now build PETSc libraries with (gnumake build):  
   make PETSC_DIR=/opt/petsc-3.9.4 PETSC_ARCH=linux-metis-mumps all  
=========================================================================

```


After successfully configure, run make.

``` bash
make PETSC_DIR=/opt/petsc-3.9.4 PETSC_ARCH=linux-metis-mumps all  
make PETSC_DIR=/opt/petsc-3.9.4 PETSC_ARCH=linux-metis-mumps check
```

> With this step i had my most trouble, i think because of the version of `openmpi-bin`

### Side by side Code_Aster

There is an parallel version of Code_Aster source file (`aster-14.6.0.tgz`) in the Code_Aster source file `aster-full-src-14.6.0/SRC`, so unzip there. No need to copy / move it.

``` bash
tar xfvz aster-14.6.0.tgz  
cd aster-14.6.0
```

Comment out lines 362-364 of `waftools/mathematicals.py` in the above directory. It will be the following part.
> again take the file from the config folder and replace it!

mathematics.py

``` python
# program testing a blacs call, output is 0 and 1  
blacs_fragment = r"""  
program test_blacs  
    integer iam, nprocs  
#    call blacs_pinfo (iam, nprocs)  
#    print *,iam  
#    print *,nprocs  
end program test_blacs  
"""
```

> again take the file from the config folder and replace it!

Next, create `mint_gnu_mpi.py` and `mint_gnu.py` and place them in your current directory

> again take the file from the config folder and replace it!

(`/aster-full-src-14.6.0/SRC/aster-14.6.0`).

**mint_gnu_mpi.py:**

``` python
# encoding: utf-8  
  
"""  
Fichier de configuration WAF pour version parallﾃｨle sur Ubuntu 13.6 :  
- Compilateur : GNU  
- MPI         : systﾃｨme (OpenMPI, Ubuntu 13.6)  
- BLAS        : OpenBLAS  
- Scalapack   : systﾃｨme (Ubuntu 13.6)  
- PETSc       :   
"""  
  
import mint_gnu  
  
def configure(self):  
    opts = self.options  
    mint_gnu.configure(self)  
  
    self.env.prepend_value('LIBPATH', [  
        '/opt/petsc-3.9.4/linux-metis-mumps/lib',  
        '/opt/parmetis-4.0.3/lib',  
        '/opt/mumps-5.1.2/lib',])  
  
    self.env.prepend_value('INCLUDES', [  
        '/opt/petsc-3.9.4/linux-metis-mumps/include',  
        '/opt/petsc-3.9.4/include',  
        '/usr/include/superlu',  
        '/opt/parmetis-4.0.3/include',  
        '/opt/mumps-5.1.2/include',])  
  
    self.env.append_value('LIB', ('X11',))  
  
    opts.parallel = True  
  
    opts.enable_mumps  = True  
    opts.mumps_version = '5.1.2'  
    opts.mumps_libs = 'dmumps zmumps smumps cmumps mumps_common pord metis scalapack openblas esmumps scotch scotcherr'  
#    opts.embed_mumps = True  
  
    opts.enable_petsc = True  
    opts.petsc_libs='petsc HYPRE ml'  
#    opts.petsc_libs='petsc'  
#    opts.embed_petsc = True  
  
#    opts.enable_parmetis  = True  
    self.env.append_value('LIB_METIS', ('parmetis'))  
    self.env.append_value('LIB_SCOTCH', ('ptscotch','ptscotcherr','ptscotcherrexit','ptesmumps'))
```

**mint_gnu.py**:

``` python
# encoding: utf-8  
  
"""  
Fichier de configuration WAF pour version sﾃｩquentielle sur Ubuntu 13.6 :  
- Compilateur : GNU  
- BLAS        : OpenBLAS  
"""  
import os  
  
def configure(self):  
    opts = self.options  
  
    # mfront path  
#    self.env.TFELHOME = '/opt/tfel-3.2.0'  
  
    self.env.append_value('LIBPATH', [  
        '/opt/aster146p/public/hdf5-1.10.3/lib',  
        '/opt/aster146p/public/med-4.0.0/lib',  
        '/opt/aster146p/public/metis-5.1.0/lib',  
        '/opt/scotch-6.0.4/lib',  
        '/opt/OpenBLAS/lib',  
        '/opt/scalapack/lib',])  
#        '/opt/tfel-3.2.0/lib',  
  
    self.env.append_value('INCLUDES', [  
        '/opt/aster146p/public/hdf5-1.10.3/include',  
        '/opt/aster146p/public/med-4.0.0/include',  
        '/opt/aster146p/public/metis-5.1.0/include',  
        '/opt/scotch-6.0.4/include',  
        '/opt/OpenBLAS/include',  
        '/opt/scalapack/include',])  
#        '/opt/tfel-3.2.0/include',  
  
    opts.maths_libs = 'openblas superlu'    
#    opts.embed_math = True  
  
    opts.enable_hdf5 = True  
    opts.hdf5_libs  = 'hdf5 z'  
#    opts.embed_hdf5 = True  
  
    opts.enable_med = True  
    opts.med_libs  = 'med stdc++'  
#    opts.embed_med  = True  
  
    opts.enable_mfront = False  
  
    opts.enable_scotch = True  
#    opts.embed_scotch  = True  
  
    opts.enable_homard = True  
#    opts.embed_aster    = True  
#    opts.embed_fermetur = True  
  
    # add paths for external programs  
#    os.environ['METISDIR'] = '/opt/aster146p/public/metis-5.1.0'  
#    os.environ['GMSH_BIN_DIR'] = '/opt/aster146p/public/gmsh-3.0.6-Linux/bin'  
    os.environ['HOMARD_ASTER_ROOT_DIR'] = '/opt/aster146p/public/homard-11.12'  
  
    opts.with_prog_metis = True  
#    opts.with_prog_gmsh = True  
    # salome: only required by few testcases  
    # europlexus: not available on all platforms  
#    opts.with_prog_miss3d = True  
    opts.with_prog_homard = True  
#    opts.with_prog_ecrevisse = True  
    opts.with_prog_xmgrace = True
```

I will install it when I am ready.

``` bash
export ASTER_ROOT=/opt/aster146p  
```

> IMPORTANT: Check if the path really exist `ll /opt/aster146p`

``` bash
export PYTHONPATH=$ASTER_ROOT/lib/python3.7/site-packages/:$PYTHONPATH  
```

> IMPORTANT: Check if the path really exist `ll $ASTER_ROOT/lib/python3.6/site-packages/ `

``` bash
./waf configure --use-config-dir=$ASTER_ROOT/14.6/share/aster --use-config=mint_gnu_mpi --prefix=$ASTER_ROOT/PAR14.6MUPT  
./waf install -p --jobs=1
```

It shows on my computer:

``` 
'install' finished successfully (15m17.139s)
```

When you’re close to done, register it with the name 14.6MUPT so that you can use the parallel version of Code_Aster with ASTK.

There is a file called `aster` in `/opt/aster146p/etc/codeaster/`, so add the following to the last line of it.

``` 
vers : PAR14.6MUPT:/opt/aster146p/PAR14.6MUPT/share/aster
```

It has to look like this:

``` 
# Code_Aster versions  
# versions can be absolute paths or relative to ASTER_ROOT  
# examples : NEW11, /usr/lib/codeaster/NEW11  
  
# default version (overridden by --vers option)  
default_vers : stable  
  
# available versions  
# DO NOT EDIT FOLLOWING LINE !  
#?vers : VVV?  
vers : stable:/opt/aster146p/14.6/share/aster  
vers : PAR14.6MUPT:/opt/aster146p/PAR14.6MUPT/share/aster
```

Then  change of create the file `aster.conf` in `/opt/aster146p/PAR14.6MUPT`. It has to contane the following line:

aster.conf
``` 
vers : PAR14.6MUPT:/opt/aster146p/PAR14.6MUPT/share/aster
```

Finally lets test it:
``` bash
/opt/aster146p/bin/as_run --vers=PAR14.6MUPT --test perfe01a
```


> If you get an error called something like `Processor Id` unkown or missing (sorry can't remeber) we have change on line in the `/opt/aster146p/etc/codeaster/asrun` file. Just open it with the text editor and find the parameter `mpi_get_procid_cmd`. This parameter have to be changed according your `openmpi-bin` version. In my case:

``` bash
# shell command to get processor id
# LAM/MPI : echo $LAMRANK
# OpenMPI (1.2) : echo $OMPI_MCA_ns_nds_vpid
# OpenMPI (1.3) : echo $OMPI_MCA_orte_ess_vpid
# OpenMPI (1.34 : echo $OMPI_COMM_WORLD_RANK
# Mpich2  : echo $PMI_RANK
mpi_get_procid_cmd : echo $OMPI_COMM_WORLD_RANK
```


## References

Really thanks to the tutorials i got all my information. Actually the most text is from:

- https://openfisheries.wordpress.com/2020/12/10/parallel-code_aster-14-6-installnation/
- https://hitoricae.com/2019/11/10/code_aster-14-4-with-petsc/
- https://sites.google.com/site/codeastersalomemeca/home/code_asterno-heiretuka/parallel-code_aster-12-4-english