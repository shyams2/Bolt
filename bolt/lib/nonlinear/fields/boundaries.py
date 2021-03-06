#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import arrayfire as af

def apply_shearing_box_bcs_fields(self, boundary, on_fdtd_grid):
    """
    Applies the shearing box boundary conditions along boundary specified 
    for the EM fields
    
    Parameters
    ----------
    boundary: str
              Boundary along which the boundary condition is to be applied.
    
    on_fdtd_grid: bool
                  Flag which dictates if boundary conditions are to be applied to the 
                  fields on the Yee grid or on the cell centered grid.
    """

    N_g_q = self.N_ghost_q
    q     = self.physical_system.params.q 
    omega = self.physical_system.params.omega
    
    L_q1  = self.q1_end - self.q1_start
    L_q2  = self.q2_end - self.q2_start

    if(boundary == 'left'):
        sheared_coordinates = self.q2_center[:, :, :N_g_q] - q * omega * L_q1 * self.time_elapsed
        
        # Applying periodic boundary conditions to the points which are out of domain:
        while(af.sum(sheared_coordinates>self.q2_end) != 0):
            sheared_coordinates = af.select(sheared_coordinates>self.q2_end,
                                            sheared_coordinates - L_q2,
                                            sheared_coordinates
                                           )

        while(af.sum(sheared_coordinates<self.q2_start) != 0):
            sheared_coordinates = af.select(sheared_coordinates<self.q2_start,
                                            sheared_coordinates + L_q2,
                                            sheared_coordinates
                                           )
        if(on_fdtd_grid == True):
            # Reordering from (N_p, N_s, N_q1, N_q2) --> (N_q1, N_q2, N_p, N_s)
            # and reordering back from (N_q1, N_q2, N_p, N_s) --> (N_p, N_s, N_q1, N_q2)
            self.yee_grid_EM_fields[:, :, :N_g_q] = \
                af.reorder(af.approx2(af.reorder(self.yee_grid_EM_fields[:, :, :N_g_q], 2, 3, 0, 1),
                                      af.reorder(self.q1_center[:, :, :N_g_q], 2, 3, 0, 1),
                                      af.reorder(sheared_coordinates, 2, 3, 0, 1),
                                      af.INTERP.BICUBIC_SPLINE,
                                      xp = af.reorder(self.q1_center[:, :, :N_g_q], 2, 3, 0, 1),
                                      yp = af.reorder(self.q2_center[:, :, :N_g_q], 2, 3, 0, 1)
                                     ),
                           2, 3, 0, 1
                          )

        else:
            # Reordering from (N_p, N_s, N_q1, N_q2) --> (N_q1, N_q2, N_p, N_s)
            # and reordering back from (N_q1, N_q2, N_p, N_s) --> (N_p, N_s, N_q1, N_q2)
            self.cell_centered_EM_fields[:, :, :N_g_q] = \
                af.reorder(af.approx2(af.reorder(self.cell_centered_EM_fields[:, :, :N_g_q], 2, 3, 0, 1),
                                      af.reorder(self.q1_center[:, :, :N_g_q], 2, 3, 0, 1),
                                      af.reorder(sheared_coordinates, 2, 3, 0, 1),
                                      af.INTERP.BICUBIC_SPLINE,
                                      xp = af.reorder(self.q1_center[:, :, :N_g_q], 2, 3, 0, 1),
                                      yp = af.reorder(self.q2_center[:, :, :N_g_q], 2, 3, 0, 1)
                                     ),
                           2, 3, 0, 1
                          )
        
    elif(boundary == 'right'):
        sheared_coordinates = self.q2_center[:, :, -N_g_q:] + q * omega * L_q1 * self.time_elapsed

        # Applying periodic boundary conditions to the points which are out of domain:
        while(af.sum(sheared_coordinates>self.q2_end) != 0):
            sheared_coordinates = af.select(sheared_coordinates>self.q2_end,
                                            sheared_coordinates - L_q2,
                                            sheared_coordinates
                                           )

        while(af.sum(sheared_coordinates<self.q2_start) != 0):
            sheared_coordinates = af.select(sheared_coordinates<self.q2_start,
                                            sheared_coordinates + L_q2,
                                            sheared_coordinates
                                           )

        if(on_fdtd_grid == True):
            # Reordering from (N_p, N_s, N_q1, N_q2) --> (N_q1, N_q2, N_p, N_s)
            # and reordering back from (N_q1, N_q2, N_p, N_s) --> (N_p, N_s, N_q1, N_q2)
            self.yee_grid_EM_fields[:, :, -N_g_q:] = \
                af.reorder(af.approx2(af.reorder(self.yee_grid_EM_fields[:, :, -N_g_q:], 2, 3, 0, 1),
                                      af.reorder(self.q1_center[:, :, -N_g_q:], 2, 3, 0, 1),
                                      af.reorder(sheared_coordinates, 2, 3, 0, 1),
                                      af.INTERP.BICUBIC_SPLINE,
                                      xp = af.reorder(self.q1_center[:, :, -N_g_q:], 2, 3, 0, 1),
                                      yp = af.reorder(self.q2_center[:, :, -N_g_q:], 2, 3, 0, 1)
                                     ),
                           2, 3, 0, 1
                          )


        else:
            # Reordering from (N_p, N_s, N_q1, N_q2) --> (N_q1, N_q2, N_p, N_s)
            # and reordering back from (N_q1, N_q2, N_p, N_s) --> (N_p, N_s, N_q1, N_q2)
            self.cell_centered_EM_fields[:, :, -N_g_q:] = \
                af.reorder(af.approx2(af.reorder(self.cell_centered_EM_fields[:, :, -N_g_q:],2, 3, 0, 1),
                                      af.reorder(self.q1_center[:, :, -N_g_q:], 2, 3, 0, 1),
                                      af.reorder(sheared_coordinates, 2, 3, 0, 1),
                                      af.INTERP.BICUBIC_SPLINE,
                                      xp = af.reorder(self.q1_center[:, :, -N_g_q:], 2, 3, 0, 1),
                                      yp = af.reorder(self.q2_center[:, :, -N_g_q:], 2, 3, 0, 1)
                                     ),
                           2, 3, 0, 1
                          )

    elif(boundary == 'bottom'):

        sheared_coordinates = self.q1_center[:, :, :, :N_g_q] - q * omega * L_q2 * self.time_elapsed

        # Applying periodic boundary conditions to the points which are out of domain:
        while(af.sum(sheared_coordinates>self.q1_end) != 0):
            sheared_coordinates = af.select(sheared_coordinates>self.q1_end,
                                            sheared_coordinates - L_q1,
                                            sheared_coordinates
                                           )

        while(af.sum(sheared_coordinates<self.q1_start) != 0):
            sheared_coordinates = af.select(sheared_coordinates<self.q1_start,
                                            sheared_coordinates + L_q1,
                                            sheared_coordinates
                                           )

        if(on_fdtd_grid == True):
            # Reordering from (N_p, N_s, N_q1, N_q2) --> (N_q1, N_q2, N_p, N_s)
            # and reordering back from (N_q1, N_q2, N_p, N_s) --> (N_p, N_s, N_q1, N_q2)
            self.yee_grid_EM_fields[:, :, :, :N_g_q] = \
                af.reorder(af.approx2(af.reorder(self.yee_grid_EM_fields[:, :, :, :N_g_q], 2, 3, 0, 1),
                                      af.reorder(sheared_coordinates, 2, 3, 0, 1),
                                      af.reorder(self.q2_center[:, :, :, :N_g_q], 2, 3, 0, 1),
                                      af.INTERP.BICUBIC_SPLINE,
                                      xp = af.reorder(self.q1_center[:, :, :, :N_g_q], 2, 3, 0, 1),
                                      yp = af.reorder(self.q2_center[:, :, :, :N_g_q], 2, 3, 0, 1)
                                     ),
                           2, 3, 0, 1
                          )

        else:
            # Reordering from (N_p, N_s, N_q1, N_q2) --> (N_q1, N_q2, N_p, N_s)
            # and reordering back from (N_q1, N_q2, N_p, N_s) --> (N_p, N_s, N_q1, N_q2)
            self.cell_centered_EM_fields[:, :, :, :N_g_q] = \
                af.reorder(af.approx2(af.reorder(self.cell_centered_EM_fields[:, :, :, :N_g_q], 2, 3, 0, 1),
                                      af.reorder(sheared_coordinates, 2, 3, 0, 1),
                                      af.reorder(self.q2_center[:, :, :, :N_g_q], 2, 3, 0, 1),
                                      af.INTERP.BICUBIC_SPLINE,
                                      xp = af.reorder(self.q1_center[:, :, :, :N_g_q], 2, 3, 0, 1),
                                      yp = af.reorder(self.q2_center[:, :, :, :N_g_q], 2, 3, 0, 1)
                                     ),
                           2, 3, 0, 1
                          )

    elif(boundary == 'top'):

        sheared_coordinates = self.q1_center[:, :, :, -N_g_q:] + q * omega * L_q2 * self.time_elapsed

        # Applying periodic boundary conditions to the points which are out of domain:
        while(af.sum(sheared_coordinates>self.q1_end) != 0):
            sheared_coordinates = af.select(sheared_coordinates>self.q1_end,
                                            sheared_coordinates - L_q1,
                                            sheared_coordinates
                                           )

        while(af.sum(sheared_coordinates<self.q1_start) != 0):
            sheared_coordinates = af.select(sheared_coordinates<self.q1_start,
                                            sheared_coordinates + L_q1,
                                            sheared_coordinates
                                           )

        if(on_fdtd_grid == True):
            # Reordering from (N_p, N_s, N_q1, N_q2) --> (N_q1, N_q2, N_p, N_s)
            # and reordering back from (N_q1, N_q2, N_p, N_s) --> (N_p, N_s, N_q1, N_q2)
            self.yee_grid_EM_fields[:, :, :, -N_g_q:] = \
                af.reorder(af.approx2(af.reorder(self.yee_grid_EM_fields[:, :, :, -N_g_q:], 2, 3, 0, 1),
                                      af.reorder(sheared_coordinates, 2, 3, 0, 1),
                                      af.reorder(self.q2_center[:, :, :, -N_g_q:], 2, 3, 0, 1),
                                      af.INTERP.BICUBIC_SPLINE,
                                      xp = af.reorder(self.q1_center[:, :, :, -N_g_q:], 2, 3, 0, 1),
                                      yp = af.reorder(self.q2_center[:, :, :, -N_g_q:], 2, 3, 0, 1)
                                     ),
                           2, 3, 0, 1
                          )

        
        else:
            # Reordering from (N_p, N_s, N_q1, N_q2) --> (N_q1, N_q2, N_p, N_s)
            # and reordering back from (N_q1, N_q2, N_p, N_s) --> (N_p, N_s, N_q1, N_q2)
            self.cell_centered_EM_fields[:, :, :, -N_g_q:] = \
                af.reorder(af.approx2(af.reorder(self.cell_centered_EM_fields[:, :, :, -N_g_q:], 2, 3, 0, 1),
                                      af.reorder(sheared_coordinates, 2, 3, 0, 1),
                                      af.reorder(self.q2_center[:, :, :, -N_g_q:], 2, 3, 0, 1),
                                      af.INTERP.BICUBIC_SPLINE,
                                      xp = af.reorder(self.q1_center[:, :, :, -N_g_q:], 2, 3, 0, 1),
                                      yp = af.reorder(self.q2_center[:, :, :, -N_g_q:], 2, 3, 0, 1)
                                     ),
                           2, 3, 0, 1
                          )

    else:
        raise Exception('Invalid choice for boundary')

    return

def apply_dirichlet_bcs_fields(self, boundary, on_fdtd_grid):
    """
    Applies the dirichlet boundary conditions along boundary specified 
    for the EM fields
    
    Parameters
    ----------
    boundary: str
              Boundary along which the boundary condition is to be applied.
    
    on_fdtd_grid: bool
                  Flag which dictates if boundary conditions are to be applied to the 
                  fields on the Yee grid or on the cell centered grid.
    """
    
    N_g_q = self.N_ghost_q

    # These arguments are defined since they are required by all the function calls:
    # So the functions can be called instead using function(*args)
    args = (self.time_elapsed, self.q1_center, self.q2_center, self.physical_system.params)
    
    if(boundary == 'left'):
        if(on_fdtd_grid == True):
            E1 = self.boundary_conditions.\
                 E1_left(self.yee_grid_EM_fields[0],*args)[:, :, :N_g_q]

            E2 = self.boundary_conditions.\
                 E2_left(self.yee_grid_EM_fields[1],*args)[:, :, :N_g_q]

            E3 = self.boundary_conditions.\
                 E3_left(self.yee_grid_EM_fields[2],*args)[:, :, :N_g_q]
            
            B1 = self.boundary_conditions.\
                 B1_left(self.yee_grid_EM_fields[3],*args)[:, :, :N_g_q]

            B2 = self.boundary_conditions.\
                 B2_left(self.yee_grid_EM_fields[4],*args)[:, :, :N_g_q]

            B3 = self.boundary_conditions.\
                 B3_left(self.yee_grid_EM_fields[5],*args)[:, :, :N_g_q]

            self.yee_grid_EM_fields[:, :, :N_g_q] = \
                    af.join(0, E1, E2, E3, af.join(0, B1, B2, B3))

        else:
            E1 = self.boundary_conditions.\
                 E1_left(self.cell_centered_EM_fields[0],*args)[:, :, :N_g_q]

            E2 = self.boundary_conditions.\
                 E2_left(self.cell_centered_EM_fields[1],*args)[:, :, :N_g_q]

            E3 = self.boundary_conditions.\
                 E3_left(self.cell_centered_EM_fields[2],*args)[:, :, :N_g_q]
            
            B1 = self.boundary_conditions.\
                 B1_left(self.cell_centered_EM_fields[3],*args)[:, :, :N_g_q]

            B2 = self.boundary_conditions.\
                 B2_left(self.cell_centered_EM_fields[4],*args)[:, :, :N_g_q]

            B3 = self.boundary_conditions.\
                 B3_left(self.cell_centered_EM_fields[5],*args)[:, :, :N_g_q]

            self.cell_centered_EM_fields[:, :, :N_g_q] = \
                    af.join(0, E1, E2, E3, af.join(0, B1, B2, B3))

    elif(boundary == 'right'):
        if(on_fdtd_grid == True):
            E1 = self.boundary_conditions.\
                 E1_right(self.yee_grid_EM_fields[0],*args)[:, :, -N_g_q:]
            
            E2 = self.boundary_conditions.\
                 E2_right(self.yee_grid_EM_fields[1],*args)[:, :, -N_g_q:]

            E3 = self.boundary_conditions.\
                 E3_right(self.yee_grid_EM_fields[2],*args)[:, :, -N_g_q:]
            
            B1 = self.boundary_conditions.\
                 B1_right(self.yee_grid_EM_fields[3],*args)[:, :, -N_g_q:]
            
            B2 = self.boundary_conditions.\
                 B2_right(self.yee_grid_EM_fields[4],*args)[:, :, -N_g_q:]
            
            B3 = self.boundary_conditions.\
                 B3_right(self.yee_grid_EM_fields[5],*args)[:, :, -N_g_q:]

            self.yee_grid_EM_fields[:, :, -N_g_q:] = \
                af.join(0, E1, E2, E3, af.join(0, B1, B2, B3))

        else:
            E1 = self.boundary_conditions.\
                 E1_right(self.cell_centered_EM_fields[0],*args)[:, :, -N_g_q:]
            
            E2 = self.boundary_conditions.\
                 E2_right(self.cell_centered_EM_fields[1],*args)[:, :, -N_g_q:]

            E3 = self.boundary_conditions.\
                 E3_right(self.cell_centered_EM_fields[2],*args)[:, :, -N_g_q:]
            
            B1 = self.boundary_conditions.\
                 B1_right(self.cell_centered_EM_fields[3],*args)[:, :, -N_g_q:]
            
            B2 = self.boundary_conditions.\
                 B2_right(self.cell_centered_EM_fields[4],*args)[:, :, -N_g_q:]
            
            B3 = self.boundary_conditions.\
                 B3_right(self.cell_centered_EM_fields[5],*args)[:, :, -N_g_q:]

            self.cell_centered_EM_fields[:, :, -N_g_q:] = \
                af.join(0, E1, E2, E3, af.join(0, B1, B2, B3))

    elif(boundary == 'bottom'):
        if(on_fdtd_grid == True):
            
            E1 = self.boundary_conditions.\
                 E1_bottom(self.yee_grid_EM_fields[0],*args)[:, :, :, :N_g_q]

            E2 = self.boundary_conditions.\
                 E2_bottom(self.yee_grid_EM_fields[1],*args)[:, :, :, :N_g_q]
            
            E3 = self.boundary_conditions.\
                 E3_bottom(self.yee_grid_EM_fields[2],*args)[:, :, :, :N_g_q]
           
            B1 = self.boundary_conditions.\
                 B1_bottom(self.yee_grid_EM_fields[3],*args)[:, :, :, :N_g_q]

            B2 = self.boundary_conditions.\
                 B2_bottom(self.yee_grid_EM_fields[4],*args)[:, :, :, :N_g_q]

            B3 = self.boundary_conditions.\
                 B3_bottom(self.yee_grid_EM_fields[5],*args)[:, :, :, :N_g_q]

            self.yee_grid_EM_fields[:, :, :, :N_g_q] = \
                af.join(0, E1, E2, E3, af.join(0, B1, B2, B3))

        else:
            E1 = self.boundary_conditions.\
                 E1_bottom(self.cell_centered_EM_fields[0],*args)[:, :, :, :N_g_q]

            E2 = self.boundary_conditions.\
                 E2_bottom(self.cell_centered_EM_fields[1],*args)[:, :, :, :N_g_q]
            
            E3 = self.boundary_conditions.\
                 E3_bottom(self.cell_centered_EM_fields[2],*args)[:, :, :, :N_g_q]
           
            B1 = self.boundary_conditions.\
                 B1_bottom(self.cell_centered_EM_fields[3],*args)[:, :, :, :N_g_q]

            B2 = self.boundary_conditions.\
                 B2_bottom(self.cell_centered_EM_fields[4],*args)[:, :, :, :N_g_q]

            B3 = self.boundary_conditions.\
                 B3_bottom(self.cell_centered_EM_fields[5],*args)[:, :, :, :N_g_q]

            self.cell_centered_EM_fields[:, :, :, :N_g_q] = \
                af.join(0, E1, E2, E3, af.join(0, B1, B2, B3))

    elif(boundary == 'top'):
        if(on_fdtd_grid == True):
            E1 = self.boundary_conditions.\
                 E1_top(self.yee_grid_EM_fields[0],*args)[:, :, :, -N_g_q:]

            E2 = self.boundary_conditions.\
                 E2_top(self.yee_grid_EM_fields[1],*args)[:, :, :, -N_g_q:]

            E3 = self.boundary_conditions.\
                 E3_top(self.yee_grid_EM_fields[2],*args)[:, :, :, -N_g_q:]
            
            B1 = self.boundary_conditions.\
                 B1_top(self.yee_grid_EM_fields[3],*args)[:, :, :, -N_g_q:]

            B2 = self.boundary_conditions.\
                 B2_top(self.yee_grid_EM_fields[4],*args)[:, :, :, -N_g_q:]

            B3 = self.boundary_conditions.\
                 B3_top(self.yee_grid_EM_fields[5],*args)[:, :, :, -N_g_q:]
            
            self.yee_grid_EM_fields[:, :, :, -N_g_q:] = \
                af.join(0, E1, E2, E3, af.join(0, B1, B2, B3))

        else:
            E1 = self.boundary_conditions.\
                 E1_top(self.cell_centered_EM_fields[0],*args)[:, :, :, -N_g_q:]

            E2 = self.boundary_conditions.\
                 E2_top(self.cell_centered_EM_fields[1],*args)[:, :, :, -N_g_q:]

            E3 = self.boundary_conditions.\
                 E3_top(self.cell_centered_EM_fields[2],*args)[:, :, :, -N_g_q:]
            
            B1 = self.boundary_conditions.\
                 B1_top(self.cell_centered_EM_fields[3],*args)[:, :, :, -N_g_q:]

            B2 = self.boundary_conditions.\
                 B2_top(self.cell_centered_EM_fields[4],*args)[:, :, :, -N_g_q:]

            B3 = self.boundary_conditions.\
                 B3_top(self.cell_centered_EM_fields[5],*args)[:, :, :, -N_g_q:]
            
            self.cell_centered_EM_fields[:, :, :, -N_g_q:] = \
                af.join(0, E1, E2, E3, af.join(0, B1, B2, B3))
    
    else:
        raise Exception('Invalid choice for boundary')

    return

def apply_mirror_bcs_fields(self, boundary, on_fdtd_grid):
    """
    Applies the mirror boundary conditions along boundary specified 
    for the EM fields
    
    Parameters
    ----------
    boundary: str
              Boundary along which the boundary condition is to be applied.
    
    on_fdtd_grid: bool
                  Flag which dictates if boundary conditions are to be applied to the 
                  fields on the Yee grid or on the cell centered grid.
    """

    N_g_q = self.N_ghost_q

    if(boundary == 'left'):
        # x-0-x-0-x-0-|-0-x-0-x-0-x-....
        #   0   1   2   3   4   5
        # For mirror boundary conditions:
        # 0 = 5; 1 = 4; 2 = 3;
        if(on_fdtd_grid == True):
            self.yee_grid_EM_fields[:, :, :N_g_q] = \
                af.flip(self.yee_grid_EM_fields[:, :, N_g_q:2 * N_g_q], 2)
        else:
            self.cell_centered_EM_fields[:, :, :N_g_q] = \
                af.flip(self.cell_centered_EM_fields[:, :, N_g_q:2 * N_g_q], 2)

    elif(boundary == 'right'):
        # ...-x-0-x-0-x-0-|-0-x-0-x-0-x
        #      -6  -5  -4  -3  -2  -1
        # For mirror boundary conditions:
        # -1 = -6; -2 = -5; -3 = -4;
        
        if(on_fdtd_grid == True):
            self.yee_grid_EM_fields[:, :, -N_g_q:] = \
                af.flip(self.yee_grid_EM_fields[:, :, -2 * N_g_q:-N_g_q], 2)
        else:
            self.cell_centered_EM_fields[:, :, -N_g_q:] = \
                af.flip(self.cell_centered_EM_fields[:, :, -2 * N_g_q:-N_g_q], 2)

    elif(boundary == 'bottom'):
        # x-0-x-0-x-0-|-0-x-0-x-0-x-....
        #   0   1   2   3   4   5
        # For mirror boundary conditions:
        # 0 = 5; 1 = 4; 2 = 3;

        if(on_fdtd_grid == True):
            self.yee_grid_EM_fields[:, :, :, :N_g_q] = \
                af.flip(self.yee_grid_EM_fields[:, :, :, N_g_q:2 * N_g_q], 3)

        else:
            self.cell_centered_EM_fields[:, :, :, :N_g_q] = \
                af.flip(self.cell_centered_EM_fields[:, :, :, N_g_q:2 * N_g_q], 3)

    elif(boundary == 'top'):
        # ...-x-0-x-0-x-0-|-0-x-0-x-0-x
        #      -6  -5  -4  -3  -2  -1
        # For mirror boundary conditions:
        # -1 = -6; -2 = -5; -3 = -4;

        if(on_fdtd_grid == True):
            self.yee_grid_EM_fields[:, :, :, -N_g_q:] = \
                af.flip(self.yee_grid_EM_fields[:, :, :, -2 * N_g_q:-N_g_q], 3)
        
        else:
            self.cell_centered_EM_fields[:, :, :, -N_g_q:] = \
                af.flip(self.cell_centered_EM_fields[:, :, :, -2 * N_g_q:-N_g_q], 3)

    else:
        raise Exception('Invalid choice for boundary')

    return

def apply_bcs_fields(self, on_fdtd_grid = False):
    """
    Applies boundary conditions to the EM fields as specified by 
    the user in params.
    """

    if(self.performance_test_flag == True):
        tic = af.time()

    # Obtaining start coordinates for the local zone
    # Additionally, we also obtain the size of the local zone
    ((i_q1_start, i_q2_start), (N_q1_local, N_q2_local)) = self._da_fields.getCorners()
    # Obtaining the end coordinates for the local zone
    (i_q1_end, i_q2_end) = (i_q1_start + N_q1_local - 1, i_q2_start + N_q2_local - 1)

    # If local zone includes the left physical boundary:
    if(i_q1_start == 0):

        if(self.boundary_conditions.in_q1_left == 'dirichlet'):
            apply_dirichlet_bcs_fields(self, 'left', on_fdtd_grid)

        elif(self.boundary_conditions.in_q1_left == 'mirror'):
            apply_mirror_bcs_fields(self, 'left', on_fdtd_grid)            

        elif(self.boundary_conditions.in_q1_left == 'mirror+dirichlet'):
            apply_mirror_bcs_fields(self, 'left', on_fdtd_grid)            
            apply_dirichlet_bcs_fields(self, 'left', on_fdtd_grid)
        
        # This is automatically handled by the PETSc function globalToLocal()
        elif(self.boundary_conditions.in_q1_left == 'periodic'):
            pass

        elif(self.boundary_conditions.in_q1_left == 'shearing-box'):
            apply_shearing_box_bcs_fields(self, 'left', on_fdtd_grid)

        else:
            raise NotImplementedError('Unavailable/Invalid boundary condition')
    
    # If local zone includes the right physical boundary:
    if(i_q1_end == self.N_q1 - 1):

        if(self.boundary_conditions.in_q1_right == 'dirichlet'):
            apply_dirichlet_bcs_fields(self, 'right', on_fdtd_grid)

        elif(self.boundary_conditions.in_q1_right == 'mirror'):
            apply_mirror_bcs_fields(self, 'right', on_fdtd_grid)
        
        elif(self.boundary_conditions.in_q1_right == 'mirror+dirichlet'):
            apply_mirror_bcs_fields(self, 'right', on_fdtd_grid)            
            apply_dirichlet_bcs_fields(self, 'right', on_fdtd_grid)
        
        # This is automatically handled by the PETSc function globalToLocal()
        elif(self.boundary_conditions.in_q1_right == 'periodic'):
            pass

        elif(self.boundary_conditions.in_q1_right == 'shearing-box'):
            apply_shearing_box_bcs_fields(self, 'right', on_fdtd_grid)

        else:
            raise NotImplementedError('Unavailable/Invalid boundary condition')

    # If local zone includes the bottom physical boundary:
    if(i_q2_start == 0):

        if(self.boundary_conditions.in_q2_bottom == 'dirichlet'):
            apply_dirichlet_bcs_fields(self, 'bottom', on_fdtd_grid)

        elif(self.boundary_conditions.in_q2_bottom == 'mirror'):
            apply_mirror_bcs_fields(self, 'bottom', on_fdtd_grid)            

        elif(self.boundary_conditions.in_q2_bottom == 'mirror+dirichlet'):
            apply_mirror_bcs_fields(self, 'bottom', on_fdtd_grid)            
            apply_dirichlet_bcs_fields(self, 'bottom', on_fdtd_grid)
        
        # This is automatically handled by the PETSc function globalToLocal()
        elif(self.boundary_conditions.in_q2_bottom == 'periodic'):
            pass

        elif(self.boundary_conditions.in_q2_bottom == 'shearing-box'):
            apply_shearing_box_bcs_fields(self, 'bottom', on_fdtd_grid)

        else:
            raise NotImplementedError('Unavailable/Invalid boundary condition')

    # If local zone includes the top physical boundary:
    if(i_q2_end == self.N_q2 - 1):

        if(self.boundary_conditions.in_q2_top == 'dirichlet'):
            apply_dirichlet_bcs_fields(self, 'top', on_fdtd_grid)

        elif(self.boundary_conditions.in_q2_top == 'mirror'):
            apply_mirror_bcs_fields(self, 'top', on_fdtd_grid)
        
        elif(self.boundary_conditions.in_q2_top == 'mirror+dirichlet'):
            apply_mirror_bcs_fields(self, 'top', on_fdtd_grid)            
            apply_dirichlet_bcs_fields(self, 'top', on_fdtd_grid)
        
        # This is automatically handled by the PETSc function globalToLocal()
        elif(self.boundary_conditions.in_q2_top == 'periodic'):
            pass

        elif(self.boundary_conditions.in_q2_top == 'shearing-box'):
            apply_shearing_box_bcs_fields(self, 'top', on_fdtd_grid)

        else:
            raise NotImplementedError('Unavailable/Invalid boundary condition')

    af.eval(self.cell_centered_EM_fields)

    if(self.performance_test_flag == True):
        af.sync()
        toc = af.time()
        self.time_apply_bcs_fields += toc - tic

    return
