import arrayfire as af
import numpy as np
import math
from petsc4py import PETSc

from bolt.lib.physical_system import physical_system

from bolt.lib.nonlinear_solver.nonlinear_solver \
    import nonlinear_solver

import domain
import boundary_conditions
import params
import initialize

import bolt.src.nonrelativistic_boltzmann.advection_terms as advection_terms

import bolt.src.nonrelativistic_boltzmann.collision_operator \
    as collision_operator

import bolt.src.nonrelativistic_boltzmann.moment_defs as moment_defs

# Defining the physical system to be solved:
system = physical_system(domain,
                         boundary_conditions,
                         params,
                         initialize,
                         advection_terms,
                         collision_operator.BGK,
                         moment_defs
                        )

# Declaring a nonlinear system object which will evolve the defined physical system:
nls = nonlinear_solver(system)
# Timestep as set by the CFL condition:
dt = params.N_cfl * min(nls.dq1, nls.dq2) \
                  / max(domain.p1_end, domain.p2_end, domain.p3_end)

if(params.t_restart == 0):
    time_elapsed = 0
    nls.dump_distribution_function('dump_f/t=0.000')
    nls.dump_moments('dump_moments/t=0.000')

else:
    time_elapsed = params.t_restart
    nls.load_distribution_function('dump_f/t=' + '%.3f'%time_elapsed)

while(time_elapsed < params.t_final):
    
    nls.strang_timestep(dt)
    time_elapsed += dt

    if(params.dt_dump_moments != 0):
        # Checking that the file writing intervals are greater than dt:
        assert(params.dt_dump_moments > dt)

        # We step by delta_dt to get the values at dt_dump
        delta_dt =   (1 - math.modf(time_elapsed/params.dt_dump_moments)[0]) \
                   * params.dt_dump_moments

        if(delta_dt<dt):
            nls.strang_timestep(delta_dt)
            time_elapsed += delta_dt
            nls.dump_moments('dump_moments/t=' + '%.3f'%time_elapsed)

    if(math.modf(time_elapsed/params.dt_dump_f)[0] < 1e-12):
        nls.dump_distribution_function('dump_f/t=' + '%.3f'%time_elapsed)

    PETSc.Sys.Print('Time = %.5f'%time_elapsed)
