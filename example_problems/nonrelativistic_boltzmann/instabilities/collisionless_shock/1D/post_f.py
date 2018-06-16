import numpy as np
import matplotlib
matplotlib.use('agg')
import pylab as pl

import h5py
import domain
import params

# Optimized plot parameters to make beautiful plots:
pl.rcParams['figure.figsize']  = 16, 10
pl.rcParams['figure.dpi']      = 80
pl.rcParams['image.cmap']      = 'jet'
pl.rcParams['lines.linewidth'] = 1.5
pl.rcParams['font.family']     = 'serif'
pl.rcParams['font.weight']     = 'bold'
pl.rcParams['font.size']       = 30
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

N_q1 = domain.N_q1
N_q2 = domain.N_q2
N_p1 = domain.N_p1
N_p2 = domain.N_p2
N_p3 = domain.N_p3
N_g  = domain.N_ghost

dq1 = (domain.q1_end - domain.q1_start) / N_q1
dq2 = (domain.q2_end - domain.q2_start) / N_q2

dp1 = (domain.p1_end[0] - domain.p1_start[0]) / N_p1
dp2 = (domain.p2_end[0] - domain.p2_start[0]) / N_p2
dp3 = (domain.p3_end[0] - domain.p3_start[0]) / N_p3

q1 = domain.q1_start + (0.5 + np.arange(N_q1)) * dq1
q2 = domain.q2_start + (0.5 + np.arange(N_q2)) * dq2

p1 = domain.p1_start[0] + (0.5 + np.arange(N_p1)) * dp1
p2 = domain.p2_start[0] + (0.5 + np.arange(N_p2)) * dp2
p3 = domain.p3_start[0] + (0.5 + np.arange(N_p3)) * dp3

p1, q2 = np.meshgrid(p1, q2)

# Declaration of the time array:
time_array = np.arange(0, params.t_final + params.dt_dump_f, 
                       params.dt_dump_f
                      )

h5f = h5py.File('dump_f/t=%.3f'%(t0) + '.h5', 'r')
f0  = np.mean(np.swapaxes(h5f['distribution_function'][:], 0, 1).reshape(N_q1, N_q2, N_p1, N_p2, N_p3), (0, 3, 4))
h5f.close()

for time_index, t0 in enumerate(time_array):
    
    h5f = h5py.File('dump_f/t=%.3f'%(t0) + '.h5', 'r')
    f   = np.mean(np.swapaxes(h5f['distribution_function'][:], 0, 1).reshape(N_q1, N_q2, N_p1, N_p2, N_p3), (0, 3, 4))
    h5f.close()

    pl.contourf(p1, q2, f, 100)
    pl.title('Time = %.2f'%t0)
    pl.savefig('images_f/%04d'%time_index + '.png')
    pl.close(fig)
    pl.clf()
