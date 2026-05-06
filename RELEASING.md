
Releasing pysem
===============

- Run tests with coverage and make sure statement coverage is 100%:
  ```shell
  pytest
  ```

- Make sure pylint passes with a score of 10:
  ```shell
  pylint src/
  ```

- Do platform test via tox:
  ```shell
  tox -r
  ```

- Dump latest version of concepticon to the repo:
  ```
  concepticon --repos-version=vLATEST dump --destination=src/pysem/data/concepticon.zip
  ```

- Update the version number, by removing the trailing `.dev0` in:
  - `pyproject.toml`
  - `src/pysem/__init__.py`
  - `README.md` (in citation)

- Update information on Concepticon version in:
  - `src/pysem/glosses.py` (`to_concepticon` function)
  - `README.md` (right on top)

- Create the release commit:
  ```shell script
  git commit -a -m "release <VERSION>"
  ```

- Create a release tag:
  ```shell script
  git tag -a v<VERSION> -m"<VERSION> release"
  ```

- Release to PyPI:
  ```shell script
  rm dist/*
  python -m build -n
  twine upload dist/*
  ```

- Push to github:
  ```shell script
  git push origin
  git push --tags
  ```

- Change version for the next release cycle, i.e. incrementing and adding .dev0
  - `pyproject.toml`
  - `src/pysem/__init__.py`

- Commit/push the version change:
  ```shell script
  git commit -a -m "bump version for development"
  git push origin
  ```
