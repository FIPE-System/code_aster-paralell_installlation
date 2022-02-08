# encoding: utf-8


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
#    opts.embed_mumps = True

    print('##############################################################')
    print('checkpoint enable_mumps')
    print('##############################################################')

    opts.enable_petsc = True
    opts.petsc_libs='petsc HYPRE ml'
#    opts.petsc_libs='petsc'
    # opts.embed_petsc = True

    print('##############################################################')
    print('checkpoint petsc')
    print('##############################################################')

#    opts.enable_parmetis  = True
    self.env.append_value('LIB_METIS', ('parmetis'))
    self.env.append_value('LIB_SCOTCH', ('ptscotch','ptscotcherr','ptscotcherrexit','ptesmumps'))

    print('##############################################################')
    print('checkpoint finished')
    print('##############################################################')