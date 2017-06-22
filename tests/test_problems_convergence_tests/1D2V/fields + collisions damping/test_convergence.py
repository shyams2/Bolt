import h5py
import numpy as np

def test_case():

  error     = np.zeros(5)
  error_rho = np.zeros(5)
  N_x       = 2**(np.arange(5, 10))

  for i in range(len(N_x)):

    h5f  = h5py.File('distribution_function_data_files/lt/lt_distribution_function_' \
                      + str(N_x[i]) + '.h5', 'r'
                    )
    f_lt = h5f['distribution_function'][:]
    h5f.close()


    h5f  = h5py.File('distribution_function_data_files/ck/ck_distribution_function_' \
                      + str(N_x[i]) + '.h5', 'r'
                    )
    f_ck = h5f['distribution_function'][:]
    h5f.close()

    f_ck = np.swapaxes(f_ck, 0, 1).reshape(f_lt.shape[0], f_lt.shape[1], f_lt.shape[4], f_lt.shape[3], f_lt.shape[2])
    f_ck = np.swapaxes(f_ck, 4, 2)
    
    rho_ck = np.sum(np.sum(np.sum(f_ck, 4), 3), 2)
    rho_lt = np.sum(np.sum(np.sum(f_lt, 4), 3), 2)
     
    diff     = abs(f_ck - f_lt)
    error[i] = np.sum(diff)/f_ck.size

    error_rho[i] = np.sum(abs(rho_ck - rho_lt))/rho_ck.size

  poly = np.polyfit(np.log10(N_x), np.log10(error), 1)
  assert(abs(poly[0]+1)<0.2)