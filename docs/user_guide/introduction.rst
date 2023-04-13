.. _introduction_to_brim:

====================
Introduction to BRiM
====================
At its core, BRiM facilitates the construction of a base bicycle model, which is
compatible with modular modelling extensions. This model is also composable with other
extensions, such as models of the rider. The base bicycle model can either be the
Whipple bicycle :cite:p:`whipple1899stability`, useful in simulations that require the
dynamics of the bicycle, or a stationary bicycle model, suitable for simulations that
focus only on the rider's pedalling. The modular extensions are divided in two
categories: kinematic extensions and load extensions. The former alter the kinematic
behaviour of the bicycle and are strongly coupled to the geometry of the bicycle model.
Examples include toroidal shaped wheels, which include the crown curvature radius of the
tyres, and a leaning rider model, which adds at least one extra degree of freedom. Load
extensions on the other hand define the forces and torques that act upon the system. The
most common example is gravity, but more complex loads are lateral and longitudinal tyre
forces. BRiM also supports biomechanical modelling of the rider. These can be torque- or
muscle-driven, and can consist of pedalling lower limbs connected to the pedals,
steering-capable upper bodies, or both combined. After composing a bicycle-rider model
from BRiM's library of components and extensions, the system's equations of motion can
be formed automatically and used for simulation.

It leverages the open-source Python package :mod:`sympy` :cite:p:`Meurer2017`, a
computer algebra system with a module, \code{sympy.physics.mechanics}, that allows
dynamical systems to be defined and their equations of motion derived in symbolic form.
Symbolic equations of motion were chosen because they are analytically exact, have the
potential to be mathematically efficient, and can be used to generate high-performance
numeric code, all of which lead to accurate and fast simulations.

..
    explain the concept of using subsystems by choosing and uniting a system boundaries

One of the fundamental concepts in BRiM is the flexibility in the selection of the
system's boundary when modeling a mechanical system. In general, a system boundary is
chosen such that it excludes other system parts that are not of interest. For example,
when modelling a bicycle, one can choose to exclude the rider and only add additional
loads on the system boundary. This vastly simplifies the analysis. It is of course also
possible to also solely model the rider without the bicycle. To model bicycle and the
rider together, one will choose a system boundary that is the union of both systems.
Therefore, it is possible to use the descriptions of both subsystems to construct an
overarching bicycle-rider system, which additionally describes the interactions between
the two. This is the approach that BRiM takes. It breaks down a model of a bicycle-rider
system into smaller models, which can be combined to form a larger model.

..
    Mention the following thing about the above approach:
    - Simplification: the subsystems do not describe their interactions at the system
      boundary with another system, as this can be more easily done in the overarching
      system.
    - Advantages of tree structure
    - Need for connections
    - Need for mixins
    - Final summarizing paragraph also mentioning when to use what

.. bibliography::
