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
time_step = 5
time = np.arange(-100, 100, step=time_step)
loss_free_space = -10 * np.log10(1e-4 / ((time / 40) ** 2 + 1))  # dB

# Loop through the loss evolution
rate_curve = []
for i, loss_free in enumerate(loss_free_space):
    link = secure_key_rates(
        name=f"sat overpass link",
        d=d,
        t_delta=jitters,
        eff_A=loss_terrestrial,
        eff_B=loss_free,
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
    rate_curve.append(rate)

# integrate to find the total key size
integrated_key = (
    sum([rate_curve[i] if rate_curve[i] > 0 else 0 for i in range(len(rate_curve))]) * time_step
)
print(f"total asymptotic secure key of {integrated_key:.2e}")
