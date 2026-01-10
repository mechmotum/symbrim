# Benchmarks

This directory contains performance benchmarks for SymBRiM models.

## Running Benchmarks

```bash
# Run all benchmarks
poetry run pytest ./benchmarks/

# Run specific benchmark
poetry run pytest ./benchmarks/test_rolling_disc.py --benchmark-only

# Save benchmark results
poetry run pytest ./benchmarks/ --benchmark-autosave
```

## Operation Counts

Each benchmark displays:
- **#Ops**: Number of operations in equations of motion (before CSE)
- **#Ops (CSE)**: Number of operations after common subexpression elimination

Lower operation counts indicate more efficient symbolic computations.

## Regression Testing

The benchmarks include automatic regression detection:
- Baseline operation counts are stored in `.benchmarks/baseline.json`
- Tests fail if operation counts increase
- Update baseline when intentional changes increase counts

## GitHub Actions

Benchmarks run automatically on PRs and:
- Display results in PR comments
- Check for regressions
- Upload results as artifacts
