# SymBRiM
A Modular and Extensible Open-Source Framework for Creating Symbolic Bicycle-Rider
Models.

As of October 2024, BRiM has been renamed to SymBRiM.

Links with more information:

- [Online documentation](https://mechmotum.github.io/symbrim/)
- [SymBRiM paper publication](https://doi.org/10.59490/6504c5a765e8118fc7b106c3) ([source](https://github.com/TJStienstra/brim-bmd-2023-paper))
- [BMD 2023 conference PowerPoint](https://docs.google.com/presentation/d/1ogz0Qs-t8bQT-2uk8gyYo40WmO387zIf/edit?usp=share_link&ouid=104124211006373398120&rtpof=true&sd=true)

This package is still under development, therefore there is no guarantee on backward
compatibility.

## Installation
`SymBRiM` is currently available on `PyPI`.
```bash
pip install symbrim
```
The optional dependencies can be installed with:
```bash
pip install bicycleparameters
pip install symmeplot
```

## Contributing
Contributions are welcome! Please refer to the [contributing page] for more information.

## Citing
If you use `SymBRiM` in your research, please cite the following paper:
```bibtex
@inproceedings{stienstra_2023_brim,
    title = {BRiM: A Modular Bicycle-Rider Modeling Framework},
    abstract = {The development of computationally efficient and validated single-track vehicle-rider models has traditionally required handcrafted one-off models. Here we introduce BRiM, a software package that facilitates building these models in a modular fashion while retaining access to the mathematical elements for handcrafted modeling when desired. We demonstrate the flexibility of the software by constructing the Carvallo-Whipple bicycle model with different numerical parameters representing different bicycles, modifying it with a front fork suspension travel model, and extending it with moving rider arms driven by joint torques at the elbows. Using these models we solve a lane-change optimal control problem for six different model variations which solve in mere seconds on a modern personal computer. Our tool enables flexible and rapid modeling of single-track vehicle-rider models that give precise results at high computational efficiency.},
    keywords = {Bicycle Dynamics, BRiM, Computational Modeling, Open-source, SymPy, Simulation, Trajectory Tracking Problem},
    author = {Timótheüs J. Stienstra and Samuel G. Brockie and Jason K. Moore},
    booktitle = {The Evolving Scholar - BMD 2023, 5th Edition},
    year = {2023},
    language = {en},
    doi = "10.59490/6504c5a765e8118fc7b106c3",
}
```

[contributing page]: https://mechmotum.github.io/symbrim/contributing/index.html
