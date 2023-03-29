from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest
from brim import (
    FlatGround,
    KnifeEdgeWheel,
    NonHolonomicTyreModel,
    RigidFrontFrame,
    RigidRearFrame,
)
from brim.bicycle import WhippleBicycle, WhippleBicycleMoore
from brim.utilities.utilities import cramer_solve, to_system
from sympy import Symbol, lambdify
from sympy.physics.mechanics import KanesMethod, dynamicsymbols

if TYPE_CHECKING:
    from sympy import Basic


class TestWhippleBicycle:
    def test_default(self) -> None:
        front = WhippleBicycle("bike")
        assert isinstance(front, WhippleBicycleMoore)

    @pytest.mark.parametrize("formulation_name, expected_class", [
        ("moore", WhippleBicycleMoore),
    ])
    def test_init(self, formulation_name, expected_class) -> None:
        front = WhippleBicycle("bike", formulation=formulation_name)
        assert isinstance(front, expected_class)

    def test_init_error(self) -> None:
        with pytest.raises(NotImplementedError):
            WhippleBicycle("bike", formulation="not_implemented")


class TestWhippleBicycleMoore:
    @staticmethod
    def _get_basu_mandal_values(bike: WhippleBicycleMoore
                                ) -> tuple[dict[Basic, float], dict[Basic, float]]:
        def get_inertia_matrix(model):
            return model.body.central_inertia.to_matrix(model.body.frame)

        constants = {
            bike.front_wheel.radius: 0.35,
            bike.rear_wheel.radius: 0.3,
            bike.rear_frame.lengths[0]: 0.9534570696121849,
            bike.front_frame.lengths[0]: 0.2676445084476887,
            bike.front_frame.lengths[1]: 0.03207142672761929,
            bike.rear_frame.lengths[1]: 0.4707271515135145,
            bike.rear_frame.lengths[2]: -0.47792881146460797,
            bike.front_frame.lengths[2]: -0.00597083392418685,
            bike.front_frame.lengths[3]: -0.3699518200282974,
            bike.rear_frame.body.mass: 85.0,
            bike.rear_wheel.body.mass: 2.0,
            bike.front_frame.body.mass: 4.0,
            bike.front_wheel.body.mass: 3.0,
            get_inertia_matrix(bike.rear_wheel)[0, 0]: 0.0603,
            get_inertia_matrix(bike.rear_wheel)[1, 1]: 0.12,
            get_inertia_matrix(bike.front_wheel)[0, 0]: 0.1405,
            get_inertia_matrix(bike.front_wheel)[1, 1]: 0.28,
            get_inertia_matrix(bike.rear_frame)[0, 0]: 7.178169776497895,
            get_inertia_matrix(bike.rear_frame)[1, 1]: 11.0,
            get_inertia_matrix(bike.rear_frame)[0, 2]: 3.8225535938357873,
            get_inertia_matrix(bike.rear_frame)[2, 2]: 4.821830223502103,
            get_inertia_matrix(bike.front_frame)[0, 0]: 0.05841337700152972,
            get_inertia_matrix(bike.front_frame)[1, 1]: 0.06,
            get_inertia_matrix(bike.front_frame)[0, 2]: 0.009119225261946298,
            get_inertia_matrix(bike.front_frame)[2, 2]: 0.007586622998470264,
            Symbol("g"): 9.81}
        initial_state = {
            **{qi: val for qi, val in zip(bike.q, (
                -0.0, -0.17447337661787718, -0.0, 0.6206670416476966,
                0.3300446174593725, -0.0, -0.2311385135743, -0.0))},
            **{ui: val for ui, val in zip(bike.u, (
                2.6703213326046784, -2.453592884421596e-14, -0.7830033527065,
                -0.6068425835418, 0.0119185528069, -8.912989661489, -0.4859824687093,
                -8.0133620584155))}}
        return constants, initial_state

    def test_basu_mandal(self) -> None:
        t = dynamicsymbols._t
        bike = WhippleBicycleMoore("bike")
        bike.ground = FlatGround("ground")
        bike.rear_frame = RigidRearFrame("rear_frame")
        bike.front_frame = RigidFrontFrame("front_frame")
        bike.rear_wheel = KnifeEdgeWheel("rear_wheel")
        bike.front_wheel = KnifeEdgeWheel("front_wheel")
        bike.rear_wheel.tyre_model = NonHolonomicTyreModel("rear_tyre")
        bike.front_wheel.tyre_model = NonHolonomicTyreModel("front_tyre")
        bike.define_kinematics()
        bike.define_loads()
        system = to_system(bike)
        system.apply_gravity(-Symbol("g") * bike.ground.normal)
        system.q_ind = [*bike.q[:4], *bike.q[5:]]
        system.q_dep = [bike.q[4]]
        system.u_ind = [bike.u[3], *bike.u[5:7]]
        system.u_dep = [*bike.u[:3], bike.u[4], bike.u[7]]
        system._eom_method = KanesMethod(
            system.frame, system.q_ind, system.u_ind, kd_eqs=system.kdes,
            q_dependent=system.q_dep, u_dependent=system.u_dep,
            configuration_constraints=system.holonomic_constraints,
            velocity_constraints=system.holonomic_constraints.diff(t).col_join(
                system.nonholonomic_constraints),
            forcelist=system.loads, bodies=system.bodies,
            explicit_kinematics=False, constraint_solver=cramer_solve)
        system.eom_method.kanes_equations()

        constants, initial_state = self._get_basu_mandal_values(bike)
        p, p_vals = zip(*constants.items())
        q0 = [initial_state[qi] for qi in system.q]
        u0 = [initial_state[ui] for ui in system.u]
        eval_sys = lambdify((system.q, system.u, p),
                            (system.mass_matrix, system.forcing), cse=True)
        eval_fnh = lambdify((system.q, system.u, p),
                            system.nonholonomic_constraints.xreplace(
                                system.eom_method.kindiffdict()), cse=True)
        assert np.allclose(eval_fnh(q0, u0, p_vals).ravel(), np.zeros(4))
        md, gd = eval_sys(q0, u0, p_vals)
        ud0 = np.linalg.solve(md.astype(np.float64), gd.astype(np.float64)).ravel()
        expected_state = {
            udi: val for udi, val in zip(bike.u.diff(t), (
                0.5903429412631302, -2.090870556233152, -0.8353281706376822,
                7.855528112824374, -0.12055438978863461, -1.8472554144218631,
                4.6198904039391895, -2.4548072904552343))
        }
        ud0_expected = [expected_state[udi] for udi in system.u.diff(t)]
        assert np.allclose(ud0, ud0_expected)

    def test_descriptions(self) -> None:
        bike = WhippleBicycleMoore("bike")
        for qi in bike.q:
            assert bike.descriptions[qi]
        for ui in bike.u:
            assert bike.descriptions[ui]
