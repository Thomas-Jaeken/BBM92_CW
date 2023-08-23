from bbm92_cw.SKR import SKR
import numpy as np
import yaml

# read in the detector settings and such from a yml file
with open("settings.yml", "r") as config_file:
    params = yaml.safe_load(config_file)
for key, value in params.items():
    globals()[key] = value

# Loss profile in an overpass, just example data
loss_terrestrial = 20  # dB
loss_free_space = 40  # dB


link = secure_key_rates(
    name=f"sat overpass link",
    d=d,
    t_delta=jitters,
    eff_A=loss_terrestrial,
    eff_B=loss_free_space,
    DC_A=darkcounts_OGS,
    DC_B=darkcounts_SAT,
    e_b=bit_error,
    e_p=phase_error,
    f=f,
    t_dead=dead_times,
    loss_format="dB",
)

tcc, B = link.optimal_params
rate = link.optimal_key_rate
error = link.error_rate([tcc, B])

# We can also calculate the performance for non optimal parameters
tcc, B = 1e-9, 1e7
rate = link.custom_performance([tcc, B])
error = link.error_rate([tcc, B])
raw_rate = link.raw_rate([tcc, B])

# Often the laser doesn't allow for arbitrary tuning so it is useful
# to optimize only the coincidence window.
tcc, rate = link.optimize_tcc_given_B(B)
