# Cohort analysis

This project performs a cohort analysis on provided data.
It imports data from the files `customer.csv` and `orders.csv` to a SQLLite database (if
not already done) and accesses them via the Peewee ORM. It then processes the order & 
customer data to produce a file `analysis.csv` with a cohort analysis, with the cohorts
being bucketed into ISO weeks in the default timezone ('US/Pacific').

## Dependencies

This package uses [pipenv](https://github.com/pypa/pipenv) to install its dependencies.

```bash
pipenv install
```

## Usage

```bash
pipenv run python cohort_analysis.py
```

## Testing
```bash
pipenv install --dev
pipenv run py.test
```
Note that the current version of Peewee has a DeprecationWarning that [will be fixed in the next release
](https://github.com/coleifer/peewee/commit/49ca301f319a6a70d7acd1425b66fa5cbdf75d8e)
