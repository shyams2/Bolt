import numpy as np
import arrayfire as af
import pylab as pl

# Optimized plot parameters to make beautiful plots:
pl.rcParams['figure.figsize']  = 12, 7.5
pl.rcParams['figure.dpi']      = 300
pl.rcParams['image.cmap']      = 'jet'
pl.rcParams['lines.linewidth'] = 1.5
pl.rcParams['font.family']     = 'serif'
pl.rcParams['font.weight']     = 'bold'
pl.rcParams['font.size']       = 20  
pl.rcParams['font.sans-serif'] = 'serif'
pl.rcParams['text.usetex']     = True
pl.rcParams['axes.linewidth']  = 1.5
pl.rcParams['axes.titlesize']  = 'medium'
pl.rcParams['axes.labelsize']  = 'medium'

pl.rcParams['xtick.major.size'] = 8     
pl.rcParams['xtick.minor.size'] = 4     
pl.rcParams['xtick.major.pad']  = 8     
pl.rcParams['xtick.minor.pad']  = 8     
pl.rcParams['xtick.color']      = 'k'     
pl.rcParams['xtick.labelsize']  = 'medium'
pl.rcParams['xtick.direction']  = 'in'    

pl.rcParams['ytick.major.size'] = 8     
pl.rcParams['ytick.minor.size'] = 4     
pl.rcParams['ytick.major.pad']  = 8     
pl.rcParams['ytick.minor.pad']  = 8     
pl.rcParams['ytick.color']      = 'k'     
pl.rcParams['ytick.labelsize']  = 'medium'
pl.rcParams['ytick.direction']  = 'in' 

import non_linear_solver.convert
import non_linear_solver.compute_moments
import non_linear_solver.communicate

# Importing interpolation routines:
from non_linear_solver.interpolation_routines import f_interp_2d, f_interp_vel_3d

# Importing the fields solvers:
from non_linear_solver.EM_fields_solver.electrostatic import solve_electrostatic_fields, fft_poisson
from non_linear_solver.EM_fields_solver.fdtd import fdtd, fdtd_grid_to_ck_grid

# Importing the collision operators:
from non_linear_solver.collision_operators.BGK import collision_step_BGK

def fields_step(da, args, local, glob, dt):

  config  = args.config
  N_ghost = config.N_ghost

  charge_electron = config.charge_electron

  # Obtaining the left-bottom corner coordinates 
  # of the left-bottom corner cell in the local zone considered:
  ((j_bottom, i_left), (N_y_local, N_x_local)) = da.getCorners()

  vel_x = args.vel_x
  vel_y = args.vel_y
  vel_z = args.vel_z

  # Convert to velocitiesExpanded:
  args.log_f = non_linear_solver.convert.to_velocitiesExpanded(da, config, args.log_f)

  if(config.fields_solver == 'electrostatic'):
    E_x = af.constant(0, N_y_local + 2*N_ghost, N_x_local + 2*N_ghost, dtype = af.Dtype.f64)
    E_y = af.constant(0, N_y_local + 2*N_ghost, N_x_local + 2*N_ghost, dtype = af.Dtype.f64)
    E_z = af.constant(0, N_y_local + 2*N_ghost, N_x_local + 2*N_ghost, dtype = af.Dtype.f64)
    
    B_x = af.constant(0, N_y_local + 2*N_ghost, N_x_local + 2*N_ghost, dtype = af.Dtype.f64)
    B_y = af.constant(0, N_y_local + 2*N_ghost, N_x_local + 2*N_ghost, dtype = af.Dtype.f64)
    B_z = af.constant(0, N_y_local + 2*N_ghost, N_x_local + 2*N_ghost, dtype = af.Dtype.f64)

    rho_array = charge_electron * (non_linear_solver.compute_moments.calculate_density(args) - \
                                   config.rho_background
                                  )#(i + 1/2, j + 1/2)
    
    # Passing the values non-inclusive of the ghost zones:
    rho_array = af.moddims(rho_array,\
                           N_y_local + 2 * N_ghost,\
                           N_x_local + 2 * N_ghost
                          )

    # rho_array = np.array(rho_array)[N_ghost:-N_ghost,\
    #                                 N_ghost:-N_ghost
    #                                ]
    
    # E_x, E_y =\
    # solve_electrostatic_fields(da, config, rho_array)

    rho_array = (rho_array)[N_ghost:-N_ghost,\
                                    N_ghost:-N_ghost
                                   ]

    args.E_x[3:-3, 3:-3], args.E_y[3:-3, 3:-3] = fft_poisson(rho_array, config.dx, config.dy)
    args = non_linear_solver.communicate.communicate_fields(da, args, local, glob)

    E_x = args.E_x 
    E_y = args.E_y

  else:
    # Will returned a flattened array containing the values of J_x,y,z in 2D space:
    args.J_x = charge_electron * non_linear_solver.compute_moments.calculate_mom_bulk_x(args) #(i + 1/2, j + 1/2)
    args.J_y = charge_electron * non_linear_solver.compute_moments.calculate_mom_bulk_y(args) #(i + 1/2, j + 1/2)
    args.J_z = charge_electron * non_linear_solver.compute_moments.calculate_mom_bulk_z(args) #(i + 1/2, j + 1/2)

    # We'll convert these back to 2D arrays to be able to perform FDTD:
    args.J_x = af.moddims(args.J_x,\
                          N_y_local + 2 * N_ghost,\
                          N_x_local + 2 * N_ghost
                         )
    
    args.J_y = af.moddims(args.J_y,\
                          N_y_local + 2 * N_ghost,\
                          N_x_local + 2 * N_ghost
                         )

    args.J_z = af.moddims(args.J_z,\
                          N_y_local + 2 * N_ghost,\
                          N_x_local + 2 * N_ghost
                         )

    # Obtaining the values for current density on the Yee-Grid:
    args.J_x = 0.5 * (args.J_x + af.shift(args.J_x, 1, 0)) #(i + 1/2, j)
    args.J_y = 0.5 * (args.J_y + af.shift(args.J_y, 0, 1)) #(i, j + 1/2)
    args.J_z = 0.25 * (args.J_z + af.shift(args.J_z, 1, 0) +\
                       af.shift(args.J_z, 0, 1) + af.shift(args.J_z, 1, 1)
                      ) #(i, j)

    # Storing the values for the previous half-time step:
    # We do this since the B values on the CK grid are defined at time t = n
    # While the B values on the FDTD grid are defined at t = n + 1/2
    B_x_old, B_y_old, B_z_old = args.B_x.copy(), args.B_y.copy(), args.B_z.copy()
    
    args = fdtd(da, args, local, glob, 0.5*dt)

    E_x, E_y, E_z, B_x, B_y, B_z = fdtd_grid_to_ck_grid(args.E_x, args.E_y, args.E_z,\
                                                        B_x_old, B_y_old, B_z_old
                                                       )
    args = fdtd(da, args, local, glob, 0.5*dt)

  # Tiling such that E_x, E_y and B_z have the same array dimensions as f:
  # This is required to perform the interpolation in velocity space:
  # NOTE: Here we are making the assumption that when mode == '2V'/'1V', N_vel_z = 1
  # If otherwise code will break here.
  if(config.mode == '3V'):
    E_x = af.tile(af.flat(E_x), 1, args.log_f.shape[1], args.log_f.shape[2], args.log_f.shape[3]) #(i + 1/2, j + 1/2)
    E_y = af.tile(af.flat(E_y), 1, args.log_f.shape[1], args.log_f.shape[2], args.log_f.shape[3]) #(i + 1/2, j + 1/2)
    E_z = af.tile(af.flat(E_z), 1, args.log_f.shape[1], args.log_f.shape[2], args.log_f.shape[3]) #(i + 1/2, j + 1/2)

    B_x = af.tile(af.flat(B_x), 1, args.log_f.shape[1], args.log_f.shape[2], args.log_f.shape[3]) #(i + 1/2, j + 1/2)
    B_y = af.tile(af.flat(B_y), 1, args.log_f.shape[1], args.log_f.shape[2], args.log_f.shape[3]) #(i + 1/2, j + 1/2)
    B_z = af.tile(af.flat(B_z), 1, args.log_f.shape[1], args.log_f.shape[2], args.log_f.shape[3]) #(i + 1/2, j + 1/2)
 
  else:
    E_x = af.tile(af.flat(E_x), 1, args.log_f.shape[1], args.log_f.shape[2], 1) #(i + 1/2, j + 1/2)
    E_y = af.tile(af.flat(E_y), 1, args.log_f.shape[1], args.log_f.shape[2], 1) #(i + 1/2, j + 1/2)
    E_z = af.tile(af.flat(E_z), 1, args.log_f.shape[1], args.log_f.shape[2], 1) #(i + 1/2, j + 1/2)

    B_x = af.tile(af.flat(B_x), 1, args.log_f.shape[1], args.log_f.shape[2], 1) #(i + 1/2, j + 1/2)
    B_y = af.tile(af.flat(B_y), 1, args.log_f.shape[1], args.log_f.shape[2], 1) #(i + 1/2, j + 1/2)
    B_z = af.tile(af.flat(B_z), 1, args.log_f.shape[1], args.log_f.shape[2], 1) #(i + 1/2, j + 1/2)

  F_x = charge_electron * (E_x + vel_y * B_z - vel_z * B_y) #(i + 1/2, j + 1/2)
  F_y = charge_electron * (E_y - vel_x * B_z + vel_z * B_x) #(i + 1/2, j + 1/2)
  F_z = charge_electron * (E_z - vel_y * B_x + vel_x * B_y) #(i + 1/2, j + 1/2)

  args.log_f = f_interp_vel_3d(args, F_x, F_y, F_z, dt)

  # Convert to positionsExpanded:
  args.log_f = non_linear_solver.convert.to_positionsExpanded(da, args.config, args.log_f)

  af.eval(args.log_f)
  return(args)

def time_integration(da, da_fields, args, time_array):

  data = np.zeros(time_array.size)

  glob  = da.createGlobalVec()
  local = da.createLocalVec()

  glob_field  = da_fields.createGlobalVec()
  local_field = da_fields.createLocalVec()

  # Convert to velocitiesExpanded:
  args.log_f = non_linear_solver.convert.to_velocitiesExpanded(da, args.config, args.log_f)

  # Storing the value of density amplitude at t = 0
  data[0] = af.sum(args.E_x**2)

  # Convert to positionsExpanded:
  args.log_f = non_linear_solver.convert.to_positionsExpanded(da, args.config, args.log_f)
  x = (0.5 + np.arange(128))*(1/128)
  v = -9 + (0.5 + np.arange(128))*(18/128)

  x, v = np.meshgrid(x, v)
  for time_index, t0 in enumerate(time_array[1:]):
    # Printing progress every 10 iterations
    # Printing only at rank = 0 to avoid multiple outputs:
    if(time_index%1 == 0 and da.getComm().rank == 0):
        print("Computing for Time =", t0)

    dt = time_array[1] - time_array[0]

    # Advection in position space:
    args.log_f = f_interp_2d(da, args, 0.25*dt)
    args.log_f = non_linear_solver.communicate.communicate_distribution_function(da, args, local, glob)
    # Collision-Step:
    args.log_f = collision_step_BGK(da, args, 0.5*dt)
    args.log_f = non_linear_solver.communicate.communicate_distribution_function(da, args, local, glob)
    # Advection in position space:
    args.log_f = f_interp_2d(da, args, 0.25*dt)
    args.log_f = non_linear_solver.communicate.communicate_distribution_function(da, args, local, glob)
    # Fields Step(Advection in velocity space):
    args       = fields_step(da_fields, args, local_field, glob_field, dt)
    args.log_f = non_linear_solver.communicate.communicate_distribution_function(da, args, local, glob)
    # Advection in position space:
    args.log_f = f_interp_2d(da, args, 0.25*dt)
    args.log_f = non_linear_solver.communicate.communicate_distribution_function(da, args, local, glob)
    # Collision-Step:
    args.log_f = collision_step_BGK(da, args, 0.5*dt)
    args.log_f = non_linear_solver.communicate.communicate_distribution_function(da, args, local, glob)
    # Advection in position space:
    args.log_f = f_interp_2d(da, args, 0.25*dt)
    args.log_f = non_linear_solver.communicate.communicate_distribution_function(da, args, local, glob)
    
    # Convert to velocitiesExpanded:

    data[time_index + 1] = af.sum(args.E_x**2)

    # if(time_index%100==0):
    #   f = np.array(af.exp(args.log_f))
    #   f = f.reshape([9, 134, 1, 128, 1])
    #   f = np.swapaxes(f, 1, 0)
    #   f = np.swapaxes(f, 3, 1)[:, :, 0, 0, 0]

    #   pl.contourf(v, x, np.swapaxes(f[3:-3, :], 0, 1), 100)
    #   pl.colorbar()
    #   pl.xlabel(r'$v$')
    #   pl.ylabel(r'$x$')
    #   pl.title('Time =' + str(t0))
    #   pl.savefig('images/' + '%04d'%(time_index/100) + '.png')
    #   pl.clf()   
    
    # Convert to positionsExpanded:

    print(af.max(args.log_f))
    print(af.min(args.log_f))

  
  glob.destroy()
  local.destroy()
  glob_field.destroy()
  local_field.destroy()

  return(data, af.exp(args.log_f))
