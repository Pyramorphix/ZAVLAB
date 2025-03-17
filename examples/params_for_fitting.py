from lmfit import Parameters
  
fit_params = Parameters()
fit_params.add('phi_p_Z', value=2.382900352788632e-05, vary=True, min=0, max=1)
fit_params.add('OMEGA', value=412093.13062991505, vary=True, min=0)
fit_params.add('omega_0', value=4.796090379904101 * 1e9, vary=False, max=5*1e10)
fit_params.add('G_phi', value=1346512.1547580766, vary=True)

