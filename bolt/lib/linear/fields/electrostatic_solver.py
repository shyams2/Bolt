#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import arrayfire as af

from bolt.lib.linear.utils.fft_funcs import fft2, ifft2
from bolt.lib.linear.utils.broadcasted_primitive_operations import multiply

# TODO: Change docstring to reflect change in function: accepts rho_hat, not rho
# and computes fields_hat
def compute_electrostatic_fields(self, rho_hat):
    """
    Computes the electrostatic fields by making use of FFTs by solving
    the Poisson equation: div^2 phi = rho

    Parameters
    ----------

    rho : af.Array
          Charge density for each of the species.
          shape:(1, N_s, N_q1, N_q2)
    """

    # Summing over all the species:
    phi_hat = af.sum(multiply(rho_hat, 1 / (self.k_q1**2 + self.k_q2**2)), 1) # (1, 1, N_q1, N_q2)

    # Setting the background electric potential to zero:
    phi_hat[: , :, 0, 0] = 0

    self.E1_hat = -phi_hat * 1j * self.k_q1
    self.E2_hat = -phi_hat * 1j * self.k_q2
    self.E3_hat = 0 * self.E1_hat 
    
    self.B1_hat = 0 * self.E1_hat
    self.B2_hat = 0 * self.E1_hat
    self.B3_hat = 0 * self.E1_hat

    af.eval(self.E1_hat, self.E2_hat, self.E3_hat,
            self.B1_hat, self.B2_hat, self.B3_hat
           )

    return
