import numpy as np
from scipy.optimize import minimize
from math import erf


class SKR:
    def __init__(
        self,
        name,
        d,
        t_delta,
        eff_A,
        eff_B,
        DC_A,
        DC_B,
        e_b,
        e_p,
        f=1.1,
        eps_tot=0.01,
        eps_EC=0.01,
        t_dead=0,
        loss_format="loss",
        custom=False,
        B0=1,
    ):
        self.f = f
        self.name = name
        self.d = d  # number of detectors per communication partner.
        self.bit_error = e_b
        self.phase_error = e_p
        if isinstance(eff_A, float) or isinstance(eff_A, int):
            self.efficiencies_A = eff_A * np.ones(d)
        else:
            self.efficiencies_A = eff_A
        if isinstance(eff_B, float) or isinstance(eff_B, int):
            self.efficiencies_B = eff_B * np.ones(d)
        else:
            self.efficiencies_B = eff_B
        if isinstance(DC_A, int) or isinstance(DC_A, float):
            self.dark_counts_A = DC_A * np.ones(d)
        else:
            self.dark_counts_A = DC_A
        if isinstance(DC_B, int) or isinstance(DC_B, float):
            self.dark_counts_B = DC_B * np.ones(d)
        else:
            self.dark_counts_B = DC_B
        if isinstance(t_delta, float) or isinstance(t_delta, int):
            self.timing_imprecision = t_delta * np.ones(d**2)
        else:
            self.timing_imprecision = t_delta
        if isinstance(t_dead, float) or isinstance(t_dead, int):
            self.t_dead = t_dead * np.ones(d**2)
        else:
            self.t_dead = t_dead

        if loss_format == "dB":
            self.__dB_to_loss__()

        self.eps_tot = eps_tot
        self.eps_EC = eps_EC
        if not custom:
            self.optimal_params, self.optimal_key_rate = self.optimize_performance(B0)

    def set_loss(self, eff_A, eff_B, loss_format="loss"):
        if isinstance(eff_A, float) or isinstance(eff_A, int):
            self.efficiencies_A = eff_A * np.ones(self.d)
        else:
            self.efficiencies_A = eff_A
        if isinstance(eff_B, float) or isinstance(eff_B, int):
            self.efficiencies_B = eff_B * np.ones(self.d)
        else:
            self.efficiencies_B = eff_B
        if loss_format == "dB":
            self.__dB_to_loss__()
        self.optimal_params, self.optimal_key_rate = self.optimize_performance()

    def __str__(self):
        return f"Object {self.name} representing a QKD link with {self.d} detectors per partner"

    def __dB_to_loss__(self):
        self.efficiencies_A = 10 ** (-np.array(self.efficiencies_A) / 10)
        self.efficiencies_B = 10 ** (-np.array(self.efficiencies_B) / 10)

    def __coincidence_window_loss__(self, x, j, k):
        """x is a coincidence window"""
        return erf(np.sqrt(np.log(2)) * (x / self.timing_imprecision[j + k * self.d]))

    def __total_efficiency__(self, eff, b, j, k):
        return eff / (1 + b * eff * self.t_dead[j + k * self.d] / self.d)

    def __dead_efficiency__(self, eff, b, j, k):
        return 1 / (1 + b * eff * self.t_dead[j + k * self.d] / self.d)

    def __coincidences_measured__(self, x):
        """x is an array of t_CC and brightness"""
        result = 0
        for j in range(self.d):
            for k in range(self.d):
                # the contribution of true CC
                result += (
                    self.__coincidence_window_loss__(x[0], j, k)
                    * x[1]
                    * self.__total_efficiency__(self.efficiencies_A[j], x[1], j, k)
                    * self.__total_efficiency__(self.efficiencies_B[k], x[1], j, k)
                )
                # Contribution of accidental CC
                result += (
                    x[0]
                    * (
                        x[1] * self.__total_efficiency__(self.efficiencies_A[j], x[1], j, k)
                        + self.dark_counts_A[j]
                    )
                    * (
                        x[1] * self.__total_efficiency__(self.efficiencies_B[k], x[1], j, k)
                        + self.dark_counts_B[k]
                    )
                    / self.__dead_efficiency__(self.efficiencies_B[k], x[1], j, k)
                    / self.__dead_efficiency__(self.efficiencies_A[j], x[1], j, k)
                )

        return result

    def __coincidences_erroneous__(self, x, error_rate):
        """x is an array of t_CC and brightness"""
        result = 0
        for j in range(self.d):
            for k in range(self.d):
                if not j == k:
                    # the contribution of true CC
                    result += (
                        error_rate
                        * self.__coincidence_window_loss__(x[0], j, k)
                        * x[1]
                        * self.__total_efficiency__(self.efficiencies_A[j], x[1], j, k)
                        * self.__total_efficiency__(self.efficiencies_B[k], x[1], j, k)
                    )
                    # Contribution of accidental CC
                    result += (
                        x[0]
                        * (
                            x[1] * self.__total_efficiency__(self.efficiencies_A[j], x[1], j, k)
                            + self.dark_counts_A[j]
                        )
                        * (
                            x[1] * self.__total_efficiency__(self.efficiencies_B[k], x[1], j, k)
                            + self.dark_counts_B[k]
                        )
                        / self.__dead_efficiency__(self.efficiencies_B[k], x[1], j, k)
                        / self.__dead_efficiency__(self.efficiencies_A[j], x[1], j, k)
                    )
                    # there's a factor 1/2 here usually but not according to eq.B13
        return result

    def __binary_entropy__(self, x):
        """x is a value between 0 and 1"""
        return -x * np.log2(x) - (1 - x) * np.log2(1 - x)

    def raw_rate(self, x):
        return 0.5 * self.__coincidences_measured__(x)

    def error_rate(self, x):
        return self.__coincidences_erroneous__(x, self.bit_error) / self.__coincidences_measured__(
            x
        )

    def __objective__(self, x):
        """x is an array of t_CC and brightness"""
        q = 0.5

        CC_m = self.__coincidences_measured__(x)
        E_b = self.__coincidences_erroneous__(x, self.bit_error) / CC_m
        E_p = self.__coincidences_erroneous__(x, self.phase_error) / CC_m

        return (
            -q * CC_m * (1.0 - self.f * self.__binary_entropy__(E_b) - self.__binary_entropy__(E_p))
        )

    def custom_performance(self, x):
        """x is an array of t_CC and brightness"""
        return -self.__objective__(x)

    def optimize_performance(self, B0=1):
        """rescaling the params to ease the optimization."""

        def obj(x):
            return self.__objective__([x[0] * self.timing_imprecision[0], x[1] * 1e9])

        result = minimize(obj, [1, B0], bounds=[(0.001, 10), (1e-9, 1e3)])
        return [result.x[0] * self.timing_imprecision[0], result.x[1] * 1e9], -result.fun

    def optimize_tcc_given_B(self, B):
        """rescaling the params to ease the optimization."""

        def obj(x):
            return self.__objective__([x * self.timing_imprecision[0], B])

        result = minimize(obj, [1], bounds=[(0.001, 100)])
        return result.x * self.timing_imprecision[0], -result.fun
