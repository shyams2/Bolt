#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from petsc4py import PETSc
import numpy as np
import arrayfire as af

def dump_moments(self, file_name):
    """
    This function is used to dump variables to a file for later usage.

    Parameters
    ----------

    file_name : str
                The variables will be dumped to this provided file name.

    Returns
    -------

    This function returns None. However it creates a file 'file_name.h5',
    containing all the moments that were defined under moments_defs in
    physical_system.

    Examples
    --------

    >> solver.dump_variables('boltzmann_moments_dump')

    The above set of statements will create a HDF5 file which contains the
    all the moments which have been defined in the physical_system object.
    The data is always stored with the key 'moments' inside the HDF5 file.
    Suppose 'density' and 'energy' are two these moments, and are declared
    the first and second in the moment_exponents object:

    These variables can then be accessed from the file using
    
    >> import h5py
    
    >> h5f = h5py.File('boltzmann_moments_dump.h5', 'r')
    
    >> rho = h5f['moments'][:][:, :, 0]
    
    >> E   = h5f['moments'][:][:, :, 1]
    
    >> h5f.close()
    """
    N_g_q = self.N_ghost_q

    i = 0
    for key in self.physical_system.moment_exponents:
        if(i == 0):
            array_to_dump = self.compute_moments(key)[:, N_g_q:-N_g_q,N_g_q:-N_g_q]
        else:
            array_to_dump = af.join(0, array_to_dump,
                                    self.compute_moments(key)[:, N_g_q:-N_g_q,N_g_q:-N_g_q]
                                   )
        i += 1

    af.flat(array_to_dump).to_ndarray(self._glob_moments_array)
    viewer = PETSc.Viewer().createHDF5(file_name + '.h5', 'w', comm=self._comm)
    viewer(self._glob_moments)

def dump_distribution_function(self, file_name):
    """
    This function is used to dump distribution function to a file for
    later usage.This dumps the complete 5D distribution function which
    can be used for post-processing

    Parameters
    ----------

    file_name : The distribution_function array will be dumped to this
                provided file name.

    Returns
    -------

    This function returns None. However it creates a file 'file_name.h5',
    containing the data of the distribution function

    Examples
    --------
    
    >> solver.dump_distribution_function('distribution_function')

    The above statement will create a HDF5 file which contains the
    distribution function. The data is always stored with the key 
    'distribution_function'

    This can later be accessed using

    >> import h5py
    
    >> h5f = h5py.File('distribution_function', 'r')
    
    >> f   = h5f['distribution_function'][:]
    
    >> h5f.close()
    """
    N_g_q = self.N_ghost_q
    N_g_p = self.N_ghost_p
    
    N_q1_local = self.f.shape[2]
    N_q2_local = self.f.shape[3]

    # The dumped array shouldn't be inclusive of velocity ghost zones:
    if(N_g_p != 0):
        array_to_dump = self._convert_to_p_expanded(self.f)[N_g_p:-N_g_p, 
                                                            N_g_p:-N_g_p,
                                                            N_g_p:-N_g_p
                                                           ]
        array_to_dump = af.moddims(array_to_dump, 
                                   self.N_p1 * self.N_p2 * self.N_p3,
                                   self.N_species,
                                   N_q1_local,
                                   N_q2_local
                                  )                                           
    
    else:
        array_to_dump = self.f
    
    array_to_dump = af.flat(array_to_dump[:, :, N_g_q:-N_g_q, N_g_q:-N_g_q])
    array_to_dump.to_ndarray(self._glob_dump_f_array)
    viewer = PETSc.Viewer().createHDF5(file_name + '.h5', 'w', comm=self._comm)
    viewer(self._glob_dump_f)

    return

def dump_EM_fields(self, file_name):

    N_g_q = self.N_ghost_q
    flattened_global_EM_fields_array = af.flat(self.yee_grid_EM_fields[:, N_g_q:-N_g_q, N_g_q:-N_g_q])
    flattened_global_EM_fields_array.to_ndarray(self._glob_fields_array)
    viewer = PETSc.Viewer().createHDF5(file_name + '.h5', 'w', comm=self._comm)
    viewer(self._glob_fields)

    return
