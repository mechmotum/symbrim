=========
Tutorials
=========

BRiM has several available tutorials. Each tutorial is a Jupyter notebook, which can be
downloaded as exercise locally and run on your own computer. The web version of the
tutorials each show the full solution, so you can also just read through them.

The tutorials are ordered with increasing depth and complexity.

.. toctree::
    :maxdepth: 1

    four_bar_linkage.ipynb
    my_first_bicycle.ipynb

Installation
------------
To run the tutorials locally, you need to install BRiM and various dependencies. The
easiest way to do this is to use the provided
:download:`yml file <./tutorial_environment.yml>`. The environment can be created using
conda or mamba:

.. code-block:: bash

    conda env create -f tutorial_environment.yml
    conda activate brim_tutorials


.. _general SymPy tutorials: https://docs.sympy.org/dev/tutorial/index.html
.. _SymPy mechanics tutorials: https://docs.sympy.org/dev/modules/physics/mechanics/examples.html
