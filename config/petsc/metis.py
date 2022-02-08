import config.package

class Configure(config.package.CMakePackage):
  def __init__(self, framework):
    config.package.CMakePackage.__init__(self, framework)
    self.gitcommit         = 'v5.1.0-p5'
    self.download          = ['git://https://bitbucket.org/petsc/pkg-metis.git','https://bitbucket.org/petsc/pkg-metis/get/'+self.gitcommit+'.tar.gz']
    self.downloaddirnames  = ['petsc-pkg-metis']
    self.functions         = ['METIS_PartGraphKway']
    self.includes          = ['metis.h']
    self.liblist           = [['libmetis.a'],['libmetis.a','libexecinfo.a']]
    self.hastests          = 1
    return

  def setupDependencies(self, framework):
    config.package.CMakePackage.setupDependencies(self, framework)
    self.compilerFlags = framework.require('config.compilerFlags', self)
    self.mathlib       = framework.require('config.packages.mathlib',self)
    self.deps          = [self.mathlib]
    return

  def formCMakeConfigureArgs(self):
    if not self.cmake.found:
      raise RuntimeError('CMake > 2.5 is needed to build METIS\nSuggest adding --download-cmake to ./configure arguments')

    args = config.package.CMakePackage.formCMakeConfigureArgs(self)
    args.append('-DGKLIB_PATH=../GKlib')
    # force metis/parmetis to use a portable random number generator that will produce the same partitioning results on all systems
    args.append('-DGKRAND=1')
    if self.checkSharedLibrariesEnabled():
      args.append('-DSHARED=1')
    if self.compilerFlags.debugging:
      args.append('-DDEBUG=1')
    if self.getDefaultIndexSize() == 64:
      args.append('-DMETIS_USE_LONGINDEX=1')
    args.append('-DMATH_LIB="'+self.libraries.toStringNoDupes(self.mathlib.lib)+'"')
    return args

  def configureLibrary(self):
    config.package.Package.configureLibrary(self)
    oldFlags = self.compilers.CPPFLAGS
    self.compilers.CPPFLAGS += ' '+self.headers.toString(self.include)
    # if not self.checkCompile('#include "metis.h"', '#if (IDXTYPEWIDTH != '+ str(self.getDefaultIndexSize())+')\n#error incompatible IDXTYPEWIDTH\n#endif'):
    #   if self.defaultIndexSize == 64:
    #     msg= '--with-64-bit-indices option requires a metis build with IDXTYPEWIDTH=64.\n'
    #   else:
    #     msg= 'IDXTYPEWIDTH=64 metis build appears to be specified for a default 32-bit-indices build of PETSc.\n'
    #   raise RuntimeError('Metis specified is incompatible!\n'+msg+'Suggest using --download-metis for a compatible metis')

    self.compilers.CPPFLAGS = oldFlags
    return
