# coding=utf-8
# --------------------------------------------------------------------
# Copyright (C) 1991 - 2019 - EDF R&D - www.code-aster.org
# This file is part of code_aster.
#
# code_aster is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# code_aster is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with code_aster.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

import os
import os.path as osp
from itertools import product, takewhile
from functools import partial
from subprocess import Popen, PIPE
from waflib import Options, Configure, Errors, Logs, Utils

BLAS = ('openblas', 'blas')
BLACS = ('blacs', )
LAPACK = ('lapack', )
SCALAPACK = ('scalapack', )
OPTIONAL_DEPS = ('cblas', )

def options(self):
    group = self.add_option_group("Mathematics  libraries options")
    group.add_option('--maths-libs', type='string',
                    dest='maths_libs', default=None,
                    help='Math librairies to link with like blas and lapack. '
                         'Use None or "auto" to search them automatically.')
    group.add_option('--embed-maths', dest='embed_math',
                    default=False, action='store_true',
                    help='Embed math libraries as static library')

def configure(self):
    # always check for libpthread, libm (never in static)
    self.check_cc(uselib_store='MATH', lib='pthread')
    self.check_cc(uselib_store='MATH', lib='m')
    self.check_number_cores()
    if self.options.maths_libs in (None, 'auto'):
        # try MKL first, then automatic blas/lapack
        if not self.detect_mkl():
            self.detect_math_lib()
    elif self.options.maths_libs:
        self.check_opts_math_lib()
    self.check_libm_after_files()
    self.check_math_libs_call()

###############################################################################
@Configure.conf
def check_opts_math_lib(self):
    opts = self.options
    embed = opts.embed_math or opts.embed_all
    check_lib = lambda lib: self.check_cc(**{
        'mandatory':True, 'uselib_store':'MATH', 'use':'MPI',
        ('st' * embed + 'lib'):lib})

    for lib in Utils.to_list(opts.maths_libs):
        check_lib(lib)

@Configure.conf
def check_sizeof_blas_int(self):
    """Check size of blas integers"""
    self.set_define_from_env('BLAS_INT_SIZE',
                             'Setting size of blas/lapack integers',
                             'unexpected value for blas int: %(size)s',
                             into=(4, 8), default=4)

@Configure.conf
def check_libm_after_files(self):
    """Avoid warning #10315: specifying -lm before files may supercede the
    Intel(R) math library and affect performance"""
    self.start_msg('Setting libm after files')
    flags = self.env.LINKFLAGS_CLIB
    if '-lm' in flags:
        while True:
            try:
                flags.remove('-lm')
            except ValueError:
                break
        self.end_msg('yes ("-lm" removed from LINKFLAGS_CLIB)')
        self.env.LINKFLAGS_CLIB = flags
    else:
        self.end_msg('nothing done')

@Configure.conf
def detect_mkl(self):
    """Try to use MKL if ifort was detected"""
    var = 'OPTLIB_FLAGS_MATH'
    opts = self.options
    embed = opts.embed_math or opts.embed_all
    if 'ifort' not in self.env.FC_NAME.lower():
        return
    self.start_msg('Detecting MKL libraries')
    suffix = '_lp64' if self.env.DEST_CPU.endswith('64') else ''
    # first: out of the box (OPTLIB_FLAGS as provided)
    totest = ['']
    # http://software.intel.com/en-us/articles/intel-mkl-link-line-advisor/
    if self.get_define('HAVE_MPI'):
        totest.append('-mkl=parallel')
        scalapack = ['-lmkl_scalapack' + suffix or '_core', '-lmkl_intel' + suffix]   # ia32: mkl_scalapack_core
        blacs = ['-lmkl_intel_thread', '-lmkl_blacs_intelmpi' + suffix] + ['-lmkl_lapack95' + suffix]
    else:
        scalapack = []
        blacs = []
    interf = 'mkl_intel' + suffix
    for typ in ('parallel', 'sequential'):
        totest.append('-mkl=' + typ)
        thread = 'mkl_sequential' if typ == 'sequential' else 'mkl_intel_thread'
        core = 'mkl_core'
        optional = []
        if typ == 'parallel':
            optional.append('iomp5')
        libs = ['-l%s' % name for name in [interf, thread, core] + optional]
        libs = ['-Wl,--start-group'] + scalapack + libs + blacs + ['-Wl,--end-group']
        totest.append(libs)
        libs = ['-mkl=' + typ ] +  libs
        totest.append(libs)
    Logs.debug("\ntest: %r" % totest)
    while totest:
        self.env.stash()
        opts = totest.pop(0)
        if opts:
            self.env.append_value(var, opts)
        try:
            self.check_math_libs_call(color='YELLOW')
        except:
            self.env.revert()
            continue
        else:
            self.end_msg(self.env[var])
            self.define('_USE_MKL', 1)
            return True
    self.end_msg('no', color='YELLOW')
    return False

@Configure.conf
def detect_math_lib(self):
    opts = self.options
    embed = opts.embed_math or (opts.embed_all and not self.get_define('HAVE_MPI'))
    varlib = ('ST' if embed else '') + 'LIB_MATH'

    # blas
    blaslibs, lapacklibs = self.get_mathlib_from_numpy()
    self.check_math_libs('blas', list(BLAS) + blaslibs, embed)
    # lapack
    opt_lapack = False
    if 'openblas' in self.env.get_flat(varlib):
        try:
            self.check_math_libs_call(color='YELLOW')
            opt_lapack = True
        except:
            pass
    if not opt_lapack:
        self.check_math_libs('lapack', list(LAPACK) + lapacklibs, embed)

    def _scalapack():
        """Check scalapack"""
        libs = list(SCALAPACK)
        libs = libs + [''.join(n) for n in product(libs, ['mpi', '-mpi', 'openmpi', '-openmpi'])]
        return self.check_math_libs('scalapack', libs, embed)

    def _blacs():
        """Check blacs"""
        libs = list(BLACS)
        libs = libs + \
               [''.join(n) for n in product(libs, ['mpi', '-mpi', 'openmpi', '-openmpi'])] \
             + [''.join(n) for n in product(['mpi', 'mpi-', 'openmpi', 'openmpi-'], libs)] \
        # check the 3 blacs libs together: Cinit, F77init, ''
        ins = []
        for i in libs:
            ins.append([l.replace('blacs', 'blacs' + n) for l, n in \
                        product([i], ['Cinit', 'F77init', ''])])
        libs = ins + libs
        return self.check_math_libs('blacs', libs, embed)

    def _optional():
        """Check optional dependencies"""
        self.check_math_libs('optional', OPTIONAL_DEPS, embed, optional=True)

    # parallel
    if self.get_define('HAVE_MPI'):
        self.env.stash()
        try:
            _blacs() and _scalapack()
            _optional()
            self.check_math_libs_call()
        except:
            self.env.revert()
            _scalapack() and _blacs()
            _optional()
            self.check_math_libs_call()

    self.start_msg('Detected math libraries')
    self.end_msg(self.env[varlib])
    if self.get_define('HAVE_MPI') and embed:
        msg = "WARNING:\n"\
              "    Static link with MPI libraries is not recommended.\n"\
              "    Remove the option --embed-maths in case of link error.\n"\
              "    See http://www.open-mpi.org/faq/?category=mpi-apps#static-mpi-apps"
        Logs.warn(msg)
    if 'openblas' in self.env[varlib]:
        self.define('_USE_OPENBLAS', 1)

@Configure.conf
def check_math_libs(self, name, libs, embed, optional=False):
    """Check for library 'name', stop on first found"""
    check_maths = partial(self.check_cc, uselib_store='MATH', use='MATH MPI',
                          mandatory=False)
    if embed:
        check_lib = lambda lib: check_maths(stlib=lib)
    else:
        check_lib = lambda lib: check_maths(lib=lib)
    self.start_msg('Checking library %s' % name)
    found = None
    for lib in libs:
        if check_lib(lib=lib):
            self.end_msg('yes (%s)' % lib)
            found = lib
            break
    else:
        if not optional:
            self.fatal('Missing the %s library' % name)
        self.end_msg('not found', 'YELLOW')
    return found

@Configure.conf
def check_number_cores(self):
    """Check for the number of available cores."""
    self.start_msg('Checking for number of cores')
    try:
        self.find_program('nproc')
        try:
            res = self.cmd_and_log(['nproc'])
            nproc = int(res)
        except Errors.WafError:
            raise Errors.ConfigurationError
    except Errors.ConfigurationError:
        nproc = 1
    else:
        self.end_msg(nproc)
    self.env['NPROC'] = nproc

@Configure.conf
def get_mathlib_from_numpy(self):
    '''The idea is that numpy shall be linked to blas and lapack.
    So we will try to get then using ldd if available'''
    libblas = []
    liblapack = []

    self.load('python')

    self.check_python_module('numpy')
    pymodule_path = self.get_python_variables(
        ['lapack_lite.__file__'],
        ['from numpy.linalg import lapack_lite'])[0]

    self.find_program('ldd')
    ldd_env = {'LD_LIBRARY_PATH': ':'.join(self.env.LIBPATH)}
    cmd = self.env.LDD + [pymodule_path]
    out = Popen(cmd, stdout=PIPE, env=ldd_env).communicate()[0].decode()

    for line in out.split('\n'):
        lib = _detect_libnames_in_ldd_line(line, LAPACK)
        if lib:
            liblapack.append(lib)
            continue
        lib = _detect_libnames_in_ldd_line(line, BLAS)
        if lib:
            libblas.append(lib)
    return libblas, liblapack

def _detect_libnames_in_ldd_line(line, libnames):
    if not list(filter(line.__contains__, libnames)):
        return None
    lib = line.split()[0].split('.', 1)[0]
    return lib[3:]

@Configure.conf
def check_math_libs_call(self, color='RED'):
    """Compile and run a small blas/lapack program"""
    self.start_msg('Checking for a program using blas/lapack')
    try:
        ret = self.check_fc(fragment=blas_lapack_fragment, use='MATH OPENMP MPI',
                            mandatory=False, execute=True, define_ret=True)
        values = list(map(float, ret and ret.split() or []))
        ref = [10.0, 5.0]
        if list(values) != ref:
            raise Errors.ConfigurationError('invalid result: %r (expecting %r)' % (values, ref))
    except Exception as exc:
        # the message must be closed
        self.end_msg('no', color=color)
        raise Errors.ConfigurationError(str(exc))
    else:
        self.end_msg('yes')

    if self.get_define('HAVE_MPI'):
        self.start_msg('Checking for a program using blacs')
        try:
            ret = self.check_fc(fragment=blacs_fragment, use='MATH OPENMP MPI',
                                mandatory=True)
        except Exception as exc:
            # the message must be closed
            self.end_msg('no', color=color)
            raise Errors.ConfigurationError(str(exc))
        else:
            self.end_msg('yes')

    self.start_msg('Checking for a program using omp thread')
    try:
        ret = self.check_fc(fragment=omp_thread_fragment, use='MATH OPENMP MPI',
                            mandatory=True, execute=True, define_ret=True)
        nbThreads = int((ret and ret.split() or [])[-1])
        refe = min(self.env['NPROC'], 2) if self.env.BUILD_OPENMP else 1
        if nbThreads < refe:
            raise ValueError("expected at least {0} thread(s)".format(nbThreads))
    except Exception as exc:
        # the message must be closed
        self.end_msg('no', color=color)
        raise Errors.ConfigurationError(str(exc))
    else:
        self.end_msg('yes (on {0} threads)'.format(nbThreads))

# program testing a blas and a lapack call, output is 10.0 and 5.0
blas_lapack_fragment = r"""
subroutine test(res, res2)
    implicit none
    real(kind=8), intent(out) :: res, res2
!
    real(kind=8) :: ddot, dlapy2
    real(kind=8) :: a1(2), a2(2)
    integer  i
!
    do i = 1, 2
        a1(i) = 1.d0 * i
        a2(i) = 2.d0 * i
    end do
    res = ddot(2, a1, 1, a2,1)
    res2 = dlapy2(3.d0, 4.d0)
end subroutine test

program main
    real(kind=8) :: a, b
    call test(a, b)
    print *, a
    print *, b
end program main
"""

# program testing a blacs call, output is 0 and 1
blacs_fragment = r"""
program test_blacs
    integer iam, nprocs
end program test_blacs
"""

# program testing openmp theads
omp_thread_fragment = r"""
program hello
!$ use omp_lib
    integer total, thid
    total = 1
    thid = 0
!$omp parallel private(thid) shared(total)
!$ total = omp_get_num_threads()
!$ thid = omp_get_thread_num()
    print *, "Thread ", thid, "of ", total, "childs"
!$omp end parallel
    print *, total
end program hello
"""
