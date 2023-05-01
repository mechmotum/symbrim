"""Module helping with the parametrization of models."""
from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from sympy.utilities.iterables import iterable
from yeadon.inertia import rotate_inertia

if TYPE_CHECKING:
    from sympy import Symbol
    from sympy.physics.mechanics import RigidBody
__all__ = ["get_inertia_vals", "get_inertia_vals_from_yeadon"]


def get_inertia_vals(body: RigidBody, *args, **kwargs):
    """Get the inertia values of a rigid body."""
    params = {}
    i_mat = body.central_inertia.to_matrix(body.frame)
    if args:
        if iterable(args[0]):
            mat = np.matrix(args[0]).reshape(3, 3)
            kwargs["ixx"] = mat[0, 0]
            kwargs["iyy"] = mat[1, 1]
            kwargs["izz"] = mat[2, 2]
            kwargs["ixy"] = mat[0, 1]
            kwargs["iyz"] = mat[1, 2]
            kwargs["izx"] = mat[0, 2]
        else:
            for arg, term in zip(args, ("ixx", "iyy", "izz", "ixy", "iyz", "izx")):
                kwargs[term] = arg
    if "ixx" in kwargs:
        params[i_mat[0, 0]] = kwargs["ixx"]
    if "iyy" in kwargs:
        params[i_mat[1, 1]] = kwargs["iyy"]
    if "izz" in kwargs:
        params[i_mat[2, 2]] = kwargs["izz"]
    if "ixy" in kwargs or "iyx" in kwargs:
        params[i_mat[0, 1]] = kwargs.get("ixy", kwargs.get("iyx"))
    if "iyz" in kwargs or "izy" in kwargs:
        params[i_mat[1, 2]] = kwargs.get("iyz", kwargs.get("izy"))
    if "izx" in kwargs or "ixz" in kwargs:
        params[i_mat[0, 2]] = kwargs.get("izx", kwargs.get("ixz"))
    if 0 in params:
        params.pop(0)
    return params


def get_inertia_vals_from_yeadon(body: RigidBody, inertia: np.matrix
                                 ) -> dict[Symbol, float]:
    """Get the inertia values of a rigid body from the Yeadon matrix.

    Explanation
    -----------
    While yeadon has defined the z axis as vertical up and the y axis as pointing to the
    back of the rider. The human in brim generally defines the z axis as pointing down
    and the x axis point to the front.
    """
    rot_mat = np.matrix([[0.0, -1.0, 0.0],
                         [-1.0, 0.0, 0.0],
                         [0.0, 0.0, -1.0]])
    return get_inertia_vals(body, rotate_inertia(rot_mat, inertia))
