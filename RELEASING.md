
Releasing pysem
===============

- Do platform test via tox:
  ```shell script
  tox -r
  ```

- Make sure statement coverage >= 99%
- Use black to make the code unified:
  ```
  black src/pysem/*.py
  ```

- Dump latest version of concepticon to the repo:
  ```
  concepticon --repos-version=vLATEST dump --destination=src/pysem/data/concepticon.zip
  ```

- Update the version number, by removing the trailing `.dev0` in:
  - `setup.cfg`
  - `src/pysem/__init__.py`
  - `README.md` (in citation)

- Update information on Concepticon version in:
  - `src/glosses.py` (`to_concepticon` function)
  - `README.md` (right on top)

- Create the release commit:
  ```shell script
  git commit -a -m "release <VERSION>"
  ```

- Create a release tag:
  ```shell script
  git tag -a v<VERSION> -m"<VERSION> release"
  ```

- Release to PyPI (see https://github.com/di/markdown-description-example/issues/1#issuecomment-374474296):
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
  - `setup.cfg`
  - `src/pysem/__init__.py`

- Commit/push the version change:
  ```shell script
  git commit -a -m "bump version for development"
  git push origin
  ```
