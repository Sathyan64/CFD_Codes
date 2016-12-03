"""
Author: Rohan
Date: 01/09/16

This file contains a class used to simulate a 1D shock tube problem using a Godunov method Riemann solution. The code in
this file should replicate the results from Toro - Chapter 6
"""

import numpy as np
from matplotlib import pyplot as plt

from CFD_Projects.riemann_solvers.eos.thermodynamic_state import ThermodynamicState
from CFD_Projects.riemann_solvers.simulations.analytic_shock_tube import AnalyticShockTube
from CFD_Projects.riemann_solvers.simulations.base_simulation import BaseSimulation1D
from CFD_Projects.riemann_solvers.flux_calculator.flux_calculator import FluxCalculator
from CFD_Projects.riemann_solvers.controller import Controller1D


class ShockTube1D(BaseSimulation1D):
    def __init__(self, left_state, right_state, membrane_location, final_time, CFL, flux_calculator):
        assert(isinstance(left_state, ThermodynamicState))
        assert(isinstance(right_state, ThermodynamicState))
        assert(isinstance(membrane_location, float))
        assert(isinstance(CFL, float))
        assert(isinstance(final_time, float))
        assert(0.0 < membrane_location < 1.0)
        assert(0.0 < CFL < 1.0)

        super(ShockTube1D, self).__init__()

        self.mesh = np.linspace(0.005, 0.995, 100)
        self.dx = self.mesh[0] * 2
        self.final_time = final_time
        self.CFL = CFL
        self.flux_calculator = flux_calculator

        # Initialise physical states
        self.densities = list()
        self.pressures = list()
        self.velocities = list()
        self.internal_energies = list()
        self.gamma = left_state.gamma
        for x_loc in self.mesh:
            if x_loc < membrane_location:
                self.densities.append(left_state.rho)
                self.pressures.append(left_state.p)
                self.velocities.append(left_state.u)
                self.internal_energies.append(left_state.e_int)
            else:
                self.densities.append(right_state.rho)
                self.pressures.append(right_state.p)
                self.velocities.append(right_state.u)
                self.internal_energies.append(right_state.e_int)
        self.densities = np.asarray(self.densities)
        self.pressures = np.asarray(self.pressures)
        self.velocities = np.asarray(self.velocities)
        self.internal_energies = np.asarray(self.internal_energies)

        self.is_initialised = True


def example():
    """
    Runs the problems from Toro Chapter 6 to validate this simulation
    """
    gamma = 1.4
    p_left = [1.0, 0.4, 1000.0, 460.894, 1000.0]
    rho_left = [1.0, 1.0, 1.0, 5.99924, 1.0]
    u_left = [0.75, -2.0, 0.0, 19.5975, -19.5975]
    p_right = [0.1, 0.4, 0.01, 46.0950, 0.01]
    rho_right = [0.125, 1.0, 1.0, 5.99242, 1.0]
    u_right = [0.0, 2.0, 0.0, -6.19633, -19.59745]
    membrane_location = [0.3, 0.5, 0.5, 0.4, 0.8]
    end_times = [0.25, 0.15, 0.012, 0.035, 0.012]

    for i in range(0, 5):
        left_state = ThermodynamicState(p_left[i], rho_left[i], u_left[i], gamma)
        right_state = ThermodynamicState(p_right[i], rho_right[i], u_right[i], gamma)

        shock_tube_god = ShockTube1D(left_state, right_state, membrane_location[i],
                                     final_time=end_times[i], CFL=0.9,
                                     flux_calculator=FluxCalculator.GODUNOV)
        shock_tube_rc = ShockTube1D(left_state, right_state, membrane_location[i],
                                    final_time=end_times[i], CFL=0.9,
                                    flux_calculator=FluxCalculator.RANDOM_CHOICE)

        # Get Godunov and Random Choice solutions
        godunov_sim = Controller1D(shock_tube_god)
        random_choice_sim = Controller1D(shock_tube_rc)
        (times_god, x_god, densities_god, pressures_god, velocities_god, internal_energies_god) = godunov_sim.run_sim()
        (times_rc, x_rc, densities_rc, pressures_rc, velocities_rc, internal_energies_rc) = random_choice_sim.run_sim()

        # Get analytic solution
        sod_test = AnalyticShockTube(left_state, right_state, membrane_location[i], 1000)
        x_sol, rho_sol, u_sol, p_sol, e_sol = sod_test.get_solution(times_god[-1], membrane_location[i])

        # Plot results
        title = "Sod Test: {}".format(i + 1)
        num_plts_x = 2
        num_plts_y = 2
        plt.figure(figsize=(20, 10))
        plt.suptitle(title)
        plt.subplot(num_plts_x, num_plts_y, 1)
        plt.title("Density")
        plt.plot(x_sol, rho_sol)
        plt.scatter(x_god, densities_god, c='g')
        plt.scatter(x_rc, densities_rc, c='r')
        plt.xlim([0.0, 1.0])
        plt.subplot(num_plts_x, num_plts_y, 2)
        plt.title("Velocity")
        plt.plot(x_sol, u_sol)
        plt.scatter(x_god, velocities_god, c='g')
        plt.scatter(x_rc, velocities_rc, c='r')
        plt.xlim([0.0, 1.0])
        plt.subplot(num_plts_x, num_plts_y, 3)
        plt.title("Pressure")
        plt.plot(x_sol, p_sol)
        plt.scatter(x_god, pressures_god, c='g')
        plt.scatter(x_rc, pressures_rc, c='r')
        plt.xlim([0.0, 1.0])
        plt.subplot(num_plts_x, num_plts_y, 4)
        plt.title("Internal Energy")
        plt.plot(x_sol, e_sol)
        plt.scatter(x_god, internal_energies_god, c='g')
        plt.scatter(x_rc, internal_energies_rc, c='r')
        plt.xlim([0.0, 1.0])
        plt.show()


if __name__ == '__main__':
    example()