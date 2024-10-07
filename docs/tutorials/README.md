Tutorials
=========

SymBRiM has several available tutorials. Each tutorial is a Jupyter notebook, which can
be downloaded as exercise locally and run on your own computer. The web version of the
tutorials each show the full solution, so you can also just read through them.

The tutorials are ordered with increasing depth and complexity. The tutorials are:

- `four_bar_linkage.ipynb`: Hands-on introduction to SymPy by modeling and simulating a
  four-bar linkage.
- `my_first_bicycle.ipynb`: Hands-on introduction to SymBRiM by modeling and simulating
  a bicycle and bicycle-rider model using the implemented components in SymBRiM.

Installation
------------
To run the tutorials locally, you need to install SymBRiM and various dependencies. The
easiest way to do this is to use the provided `tutorials_environment.yml>`. The
environment can be created using conda or mamba:

```bash
conda env create -f tutorials_environment.yml
conda activate brim_tutorials
```
