# Assignment 4: Futures Settlement and IFR Yield Curves

FRE-GY 9743

## Submission contents

- `Assignment_4_Submission.pdf`: written solution, methodology and numerical results (included at the top level of the submission package).
- `hw4_ifr_yield_curve.ipynb`: completed notebook with saved execution outputs.
- `fixedincomelib/`: completed course library, including the IFR interpolator, analytic gradients and recursive discount factors.
- `static_files/`: model configuration data.
- `tests/test_ifr.py`: numerical and reference-chain tests.

## Execution

Install `requirements.txt` and run the notebook from this directory. The specified course environment is Python 3.11. Validation was performed with Python 3.12.14, NumPy 1.26.4, pandas 2.3.1 and QuantLib 1.41.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

The notebook computes analytic sensitivities per unit decimal IFR, holding node times and the cashflow fixed. Finite differences are used only in validation, not in the submitted risk calculation.
