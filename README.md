# BRiM
A Modular and Extensible Open-Source Framework for Creating Bicycle-Rider Models.

Links with more information:

- [Online documentation](https://tjstienstra.github.io/brim/)
- [BRiM paper publication](https://doi.org/10.59490/6504c5a765e8118fc7b106c3) ([source](https://github.com/TJStienstra/brim-bmd-2023-paper))
- [BMD 2023 conference PowerPoint](https://docs.google.com/presentation/d/1ogz0Qs-t8bQT-2uk8gyYo40WmO387zIf/edit?usp=share_link&ouid=104124211006373398120&rtpof=true&sd=true)

This package is still under development, therefore there is no guarantee on backward
compatibility.

## Installation
`BRiM` is currently not available on `PyPI`. Therefore, you'll need to install the
development version from GitHub using:
```bash
pip install git+https://github.com/TJStienstra/brim.git
```
The optional dependencies can be installed with:
```bash
pip install git+https://github.com/moorepants/BicycleParameters.git
pip install git+https://github.com/TJStienstra/symmeplot.git
```

## Contributing
Contributions are welcome! Please refer to the [contributing page] for more information.

## Citing
If you use `BRiM` in your research, please cite the following paper:
```bibtex
@inproceedings{stienstra_2023_brim,
    title = {BRiM: A Modular Bicycle-Rider Modeling Framework},
    abstract = {The development of computationally efficient and validated single-track vehicle-rider models has traditionally required handcrafted one-off models. Here we introduce BRiM, a software package that facilitates building these models in a modular fashion while retaining access to the mathematical elements for handcrafted modeling when desired. We demonstrate the flexibility of the software by constructing the Carvallo-Whipple bicycle model with different numerical parameters representing different bicycles, modifying it with a front fork suspension travel model, and extending it with moving rider arms driven by joint torques at the elbows. Using these models we solve a lane-change optimal control problem for six different model variations which solve in mere seconds on a modern laptop. Our tool enables flexible and rapid modeling of single-track vehicle-rider models that give precise results at high computational efficiency.},
    keywords = {Bicycle Dynamics, BRiM, Computational Modeling, Open-source, SymPy, Simulation, Trajectory Tracking Problem},
    author = {Timótheüs J. Stienstra and Samuel G. Brockie and Jason K. Moore},
    booktitle = {The Evolving Scholar - BMD 2023, 5th Edition},
    year = {2023},
    language = {en},
    url = {https://dapp.orvium.io/deposits/6504c5a765e8118fc7b106c3/view},
}
```

[contributing page]: https://tjstienstra.github.io/brim/contributing/index.html
