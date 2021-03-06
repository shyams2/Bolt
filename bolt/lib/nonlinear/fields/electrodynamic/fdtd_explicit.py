#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import arrayfire as af

from bolt.lib.nonlinear.communicate import communicate_fields
from ..boundaries import apply_bcs_fields

def fdtd_evolve_E(self, dt):
    
    if(self.performance_test_flag == True):
        tic = af.time()

    dq1 = self.dq1
    dq2 = self.dq2

    B1 = self.yee_grid_EM_fields[3]
    B2 = self.yee_grid_EM_fields[4]
    B3 = self.yee_grid_EM_fields[5]

    # dE1/dt = + dB3/dq2
    # dE2/dt = - dB3/dq1
    # dE3/dt = dB2/dq1 - dB1/dq2

    B1_shifted_q2 = af.shift(B1, 0, 0, 0, 1)

    B2_shifted_q1 = af.shift(B2, 0, 0, 1, 0)

    B3_shifted_q1 = af.shift(B3, 0, 0, 1, 0)
    B3_shifted_q2 = af.shift(B3, 0, 0, 0, 1)

    self.yee_grid_EM_fields[0] +=   (dt / dq2) * (B3 - B3_shifted_q2) - self.J1 * dt
    self.yee_grid_EM_fields[1] +=  -(dt / dq1) * (B3 - B3_shifted_q1) - self.J2 * dt
    self.yee_grid_EM_fields[2] +=   (dt / dq1) * (B2 - B2_shifted_q1) \
                                  - (dt / dq2) * (B1 - B1_shifted_q2) \
                                  - dt * self.J3

    af.eval(self.yee_grid_EM_fields)

    if(self.performance_test_flag == True):
        af.sync()
        toc = af.time()
        self.time_fieldsolver += toc - tic

    return

def fdtd_evolve_B(self, dt):
    
    if(self.performance_test_flag == True):
        tic = af.time()

    dq1 = self.dq1
    dq2 = self.dq2

    E1 = self.yee_grid_EM_fields[0]
    E2 = self.yee_grid_EM_fields[1]
    E3 = self.yee_grid_EM_fields[2]

    # dB1/dt = - dE3/dq2
    # dB2/dt = + dE3/dq1
    # dB3/dt = - (dE2/dq1 - dE1/dq2)

    E1_shifted_q2 = af.shift(E1, 0, 0, 0, -1)

    E2_shifted_q1 = af.shift(E2, 0, 0, -1, 0)

    E3_shifted_q1 = af.shift(E3, 0, 0, -1, 0)
    E3_shifted_q2 = af.shift(E3, 0, 0, 0, -1)

    self.yee_grid_EM_fields[3] += -(dt / dq2) * (E3_shifted_q2 - E3)
    self.yee_grid_EM_fields[4] +=  (dt / dq1) * (E3_shifted_q1 - E3)
    self.yee_grid_EM_fields[5] += - (dt / dq1) * (E2_shifted_q1 - E2) \
                                  + (dt / dq2) * (E1_shifted_q2 - E1)

    af.eval(self.yee_grid_EM_fields)

    if(self.performance_test_flag == True):
        af.sync()
        toc = af.time()
        self.time_fieldsolver += toc - tic

    return


def fdtd(self, dt):
    """
    Evolves the EM fields variables on a Yee-Grid using FDTD:
    E's and B's are staggered in time such that
    B's are defined at (n + 1/2), and E's are defined at n

    Positions of grid point where field quantities are defined:
    B1 --> (i, j + 1/2)
    B2 --> (i + 1/2, j)
    B3 --> (i + 1/2, j + 1/2)

    E1 --> (i + 1/2, j)
    E2 --> (i, j + 1/2)
    E3 --> (i, j)

    J1 --> (i + 1/2, j)
    J2 --> (i, j + 1/2)
    J3 --> (i, j)
    
    Parameters
    ----------

    dt : double
         Time-step size to evolve the system
    """

    # The communicate function transfers the data from the 
    # local vectors to the global vectors, in addition to  
    # dealing with periodic boundary conditions:
    communicate_fields(self, True)
    apply_bcs_fields(self, True)
    fdtd_evolve_E(self, dt)
    
    communicate_fields(self, True)
    apply_bcs_fields(self, True)
    fdtd_evolve_B(self, dt)
    
    return
