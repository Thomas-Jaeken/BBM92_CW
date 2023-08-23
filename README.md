# BBM92_CW
This project is an implementation of the model laid out in [Neumann et al.](https://link.aps.org/doi/10.1103/PhysRevA.104.022406)
The model treats a Continuous Wave (CW) source of photon pairs that are perfectly correlated in time, 
and formalises what the expected asymptotic secure key rate (AKR) is if you use them to perform passive BBM92.

The package is meant to calculate the optimal brightness, coincidence window and corresponding AKR for a given link loss.


# Installation
```
pip install bbm92_cw
```

# Examples
You can now use the module like you would any other python package.
To understand better what the functionality offers, have a look at the following examples:

## satellite overpass
In an overpass, we assume a constant loss of 20 dB on the terrestrial arm, and a variable loss on the free-space arm. The specs of the detectors are read out from [a yaml file](https://github.com/Thomas-Jaeken/BBM92_CW/blob/4760e5c2bc902244f3baf6900378bd0f3ad4bebf/bbm92_cw/example/settings.yml)

https://github.com/Thomas-Jaeken/BBM92_CW/blob/4760e5c2bc902244f3baf6900378bd0f3ad4bebf/bbm92_cw/example/example_overpass.py#L1-L42

Resulting in the following instantaneous key generation rate, which integrates to 27.6 kbit.

![image](https://github.com/Thomas-Jaeken/BBM92_CW/blob/0c4e2c0795cc8039ef8f2fad56d3dcdfef53e8bf/bbm92_cw/example/figures/example_overpass.png)

## Instantaneous figures
Here we illustrate all interesting values that can be extracted from the calculation

https://github.com/Thomas-Jaeken/BBM92_CW/blob/f0b9f06dabc51a2d63a1b51fb51689080ad01214/bbm92_cw/example/example_figures.py#L31-L43
