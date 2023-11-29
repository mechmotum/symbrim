"""Module for simulating sympy.physics.mechanics.system.System objects."""
from __future__ import annotations

from typing import Callable

import numpy as np
import numpy.typing as npt
from scipy.integrate import solve_ivp

try:
    from scikits.odes import dae
except ImportError:  # pragma: no cover
    dae: Callable | None = None
from scipy.optimize import fsolve
from sympy import Basic, Function, lambdify
from sympy.physics.mechanics import (
    KanesMethod,
    System,
    dynamicsymbols,
    find_dynamicsymbols,
    msubs,
)

__all__ = ["Simulator"]


array_type = npt.NDArray[np.float64]


class Simulator:
    """Simulator for sympy.physics.mechanics.system.System object."""

    def __init__(self, system: System) -> None:
        if not isinstance(system, System):
            raise TypeError(
                f"System should be of type {type(System)} not {type(system)}.")
        self._system = system
        self._constants = {}
        self._initial_conditions = {}
        self._inputs = {}
        self._t, self._x = None, None
        self._p, self._p_vals = (), np.array([], dtype=np.float64)
        self._r, self._r_funcs = (), ()
        self._eval_configuration_constraints = None
        self._eval_velocity_constraints = None
        self._eval_eoms_matrices = None
        self._initialized = False
        self._n_qind, self._n_qdep, self._n_q, self._n_uind, self._n_udep, self._n_u = (
            None, None, None, None, None, None)
        self._n_x = None

    @property
    def t(self) -> array_type:
        """Time array of the simulation."""
        if self._t is None:
            raise ValueError("System has not been integrated yet.")
        return self._t

    @property
    def x(self) -> array_type:
        """State array of the simulation."""
        if self._x is None:
            raise ValueError("System has not been integrated yet.")
        return self._x

    @property
    def system(self) -> System:
        """System object of the simulator."""
        return self._system

    @property
    def constants(self) -> dict[Basic, float]:
        """Constants of the system."""
        return self._constants

    @constants.setter
    def constants(self, constants: dict[Basic, float]):
        if not isinstance(constants, dict):
            raise TypeError(f"Constants should be of type {type(dict)} not "
                            f"{type(constants)}.")
        old_constants = self._constants
        self._constants = constants
        if self._initialized:
            if set(old_constants.keys()) != set(constants.keys()):
                self._initialized = False
            else:
                self._p_vals = np.array(
                    [constants[pi] for pi in self._p], dtype=np.float64)
                self.solve_initial_conditions()

    @property
    def inputs(self
               ) -> dict[Function, Callable[[float, array_type], float]]:
        """Input of the system."""
        return self._inputs

    @inputs.setter
    def inputs(self, inputs: dict[Function, Callable[[float, array_type], float]]):
        if not isinstance(inputs, dict):
            raise TypeError(f"Inputs should be of type {type(dict)} not "
                            f"{type(inputs)}.")
        for ri in inputs.values():
            if not callable(ri):
                raise TypeError(
                    f"Inputs should be of type "
                    f"{type(Callable[[float, array_type], float])} not {type(ri)}.")
        old_inputs = self._inputs
        self._inputs = inputs
        if self._initialized:
            if set(old_inputs.keys()) != set(inputs.keys()):
                self._initialized = False
            else:
                self._r_funcs = tuple(inputs[fi] for fi in self._r)

    @property
    def initial_conditions(self) -> dict[Function, float]:
        """Initial conditions of the system."""
        return self._initial_conditions

    @initial_conditions.setter
    def initial_conditions(self, initial_conditions: dict[Function, float]):
        if not isinstance(initial_conditions, dict):
            raise TypeError(f"Initial condintions should be of type "
                            f"{type(dict)} not {type(initial_conditions)}.")
        old_initial_conditions = self._initial_conditions
        self._initial_conditions = initial_conditions
        if self._initialized:
            if set(old_initial_conditions.keys()) != set(initial_conditions.keys()):
                self._initialized = False
            else:
                self.solve_initial_conditions()

    def _eval_eoms_reshaped(self, t: float, x: array_type
                            ) -> tuple[array_type, array_type]:
        """Evaluate the equations of motion and reshape the output."""
        mass_matrix, forcing = self._eval_eoms_matrices(
            t, x, self._p_vals,
            np.array([cf(t, x) for cf in self._r_funcs], dtype=np.float64))
        return (mass_matrix.reshape((self._n_x, self._n_x)),
                forcing.reshape((self._n_x,)))

    def _solve_configuration_constraints(
            self, q_ind: array_type, q_dep_guess: array_type
    ) -> array_type:  # type: ignore
        """Solve the configuration constraints for the dependent coordinates."""
        if not self.system.q_dep:
            return np.array([])
        return np.array(fsolve(self._eval_configuration_constraints, q_dep_guess,
                               args=(q_ind, self._p_vals)))

    def _solve_velocity_constraints(
            self, q: array_type, u_ind: array_type, u_dep_guess: array_type
    ) -> array_type:
        """Solve the velocity constraints for the dependent speeds."""
        if not self.system.u_dep:
            return np.array([])
        return np.array(fsolve(self._eval_velocity_constraints, u_dep_guess,
                               args=(q, u_ind, self._p_vals)))

    def solve_initial_conditions(self) -> None:
        """Solve the initial conditions for the dependent coordinates and speeds."""
        if (self._eval_configuration_constraints is None or
                self._eval_velocity_constraints is None):
            raise ValueError("Simulator has not been initialized yet.")
        q_dep_guess = [self.initial_conditions.get(qi, 0.) for qi in self.system.q_dep]
        q_ind = [self.initial_conditions[qi] for qi in self.system.q_ind]
        q_dep = self._solve_configuration_constraints(
            np.array(q_ind), np.array(q_dep_guess))
        q0 = q_ind + list(q_dep)
        u_dep_guess = [self.initial_conditions.get(ui, 0.) for ui in self.system.u_dep]
        u_ind = [self.initial_conditions[ui] for ui in self.system.u_ind]
        u_dep = self._solve_velocity_constraints(
            np.array(q0), np.array(u_ind), np.array(u_dep_guess))
        u0 = u_ind + list(u_dep)
        for qi, q0i in zip(self.system.q, q0):
            self.initial_conditions[qi] = q0i
        for ui, u0i in zip(self.system.u, u0):
            self.initial_conditions[ui] = u0i

    def initialize(self, check_parameters: bool = False) -> None:
        """Initialize the simulator.

        Parameters
        ----------
        check_parameters : bool, optional
            Whether the constants and initial conditions should be checked for
            consistency with the system, by default False.
        """
        if self._initialized:
            raise RuntimeError("Simulator has already been initialized.")
        if self.system.eom_method is None:
            raise ValueError("Equations of motion have not been formed yet.")
        if self.constants is None:
            raise ValueError("Simulator has not been given any constants.")
        if self.initial_conditions is None:
            raise ValueError("Simulator has not been given any initial conditions.")
        if check_parameters:
            free_constants = self.system.mass_matrix_full.free_symbols.union(
                self.system.forcing_full.free_symbols)
            free_dyn = find_dynamicsymbols(self.system.mass_matrix_full).union(
                find_dynamicsymbols(self.system.forcing_full))
            state = set(self.system.q.col_join(self.system.u))
            inputs = set(self.inputs.keys())

            free_dyn = free_dyn.difference(state, inputs)
            free_symbols = free_constants.union(free_dyn).difference(
                {dynamicsymbols._t})
            missing = free_symbols.difference(self.constants.keys())
            if missing:
                raise ValueError(f"Simulator is missing the following constants: "
                                 f"{missing}.")
            missing = set(self.system.q_ind.col_join(self.system.u_ind)).difference(
                self.initial_conditions.keys())
            if missing:
                raise ValueError(f"Simulator is missing the following initial "
                                 f"conditions: {missing}.")

        qdot_to_u = self.system.eom_method.kindiffdict() if isinstance(
            self.system.eom_method, KanesMethod) else {}
        t = dynamicsymbols._t
        self._n_qind, self._n_qdep = len(self.system.q_ind), len(self.system.q_dep)
        self._n_uind, self._n_udep = len(self.system.u_ind), len(self.system.u_dep)
        self._n_q, self._n_u = self._n_qind + self._n_qdep, self._n_uind + self._n_udep
        self._n_x = self._n_q + self._n_u
        self._p, self._p_vals = zip(*self.constants.items())
        self._p_vals = np.array(self._p_vals, dtype=np.float64)
        if self.inputs:
            self._r, self._r_funcs = zip(*self.inputs.items())
        else:
            self._r, self._r_funcs = (), ()
        velocity_constraints = msubs(self.system.holonomic_constraints.diff(t).col_join(
            self.system.nonholonomic_constraints), qdot_to_u)
        self._eval_configuration_constraints = lambdify(
            (self.system.q_dep, self.system.q_ind, self._p),
            self.system.holonomic_constraints[:], cse=True)
        self._eval_velocity_constraints = lambdify(
            (self.system.u_dep, self.system.q, self.system.u_ind, self._p),
            velocity_constraints[:], cse=True)
        # Fix for https://github.com/numba/numba/issues/3709
        self._eval_eoms_matrices = lambdify(
            (t, self.system.q.col_join(self.system.u), self._p, self._r),
            (self.system.mass_matrix_full.reshape(1, self._n_x * self._n_x),
             self.system.forcing_full.reshape(1, self._n_x)), cse=True)
        self.solve_initial_conditions()
        self._initialized = True

    def eval_rhs(self, t: np.float64, x: array_type) -> array_type:
        """Evaluate the right-hand side of the equations of motion."""
        mass_matrix, forcing = self._eval_eoms_reshaped(t, x)
        return np.linalg.solve(mass_matrix, forcing)

    def _eval_eoms(self, t: float, x: array_type, xd: array_type, residual: array_type
                   ) -> None:
        """Evaluate the residual vector of the equations of motion."""
        mass_matrix, forcing = self._eval_eoms_reshaped(t, x)

        n_nh = self._n_udep - self._n_qdep
        q, u = x[:self._n_q], x[self._n_q:]
        q_ind, q_dep = q[:self._n_qind], q[self._n_qind:]
        u_ind, u_dep = u[:-self._n_udep], u[-self._n_udep:]

        residual[:self._n_x] = mass_matrix @ xd - forcing
        if self._n_qdep != 0:
            residual[self._n_x - self._n_udep:-n_nh] = (
                self._eval_configuration_constraints(q_dep, q_ind, self._p_vals))
        if n_nh != 0:
            residual[-n_nh:] = self._eval_velocity_constraints(
                u_dep, q, u_ind, self._p_vals)[-n_nh:]

    def solve(self, t_span: tuple[float, float] | array_type, solver: str = "solve_ivp",
              **kwargs) -> tuple[array_type, array_type]:
        """Simulate the system.

        Parameters
        ----------
        t_span : tuple[float, float] | array_type
            The start and end times of the simulation or the times at which to
            evaluate the solution in case of a DAE solver.
        solver : str, optional
            The solver to use, by default "solve_ivp".
        **kwargs
            Keyword arguments to pass to `scipy.integrate.solve_ivp`.

        Returns
        -------
        tuple[array_type, array_type]
            The times and the solution of the system, where the solution has the shape
            ``(n_x, n_t)``.
        """
        if not self._initialized:
            raise RuntimeError("Simulator has not been initialized yet.")
        x0 = np.array([self.initial_conditions[xi] for xi in self.system.q.col_join(
            self.system.u)])
        if solver == "solve_ivp":
            sol = solve_ivp(self.eval_rhs, t_span, x0, **kwargs)
            self._t = sol.t
            self._x = sol.y
        elif solver == "dae":  # pragma: no cover
            if dae is None:
                raise ImportError("scikits.odes is not installed.")
            integrator_name = kwargs.pop("integrator_name", "ida")
            n_constrs = len(self.system.holonomic_constraints) + len(
                self.system.nonholonomic_constraints)
            dae_solver = dae(
                integrator_name, self._eval_eoms,
                algebraic_vars_idx=range(len(x0) - n_constrs, len(x0)), old_api=False,
                **kwargs)
            sol = dae_solver.solve(t_span, x0, self.eval_rhs(t_span[0], x0))
            self._t = sol.values.t
            self._x = sol.values.y.T
        else:
            raise ValueError(f"Unknown solver {solver}.")
        return self.t, self.x
