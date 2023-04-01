# How to develop on this project

DeveloperGPT welcomes contributions from the community.

This instructions are for linux base systems. (Linux, MacOS, BSD, etc.)
## Setting up your own fork of this repo.

- On github interface click on `Fork` button.
- Clone your fork of this repo. `git clone git@github.com:YOUR_GIT_USERNAME/DeveloperGPT.git`
- Enter the directory `cd developergpt`
- Add upstream repo `git remote add upstream https://github.com/luo-anthony/DeveloperGPT`

## Setting up your own virtual environment

Run `make virtualenv` to create a virtual environment.
then activate it with `source .venv/bin/activate`.

## Install the project in develop mode

Run `make install` to install the project in develop mode.

## Run the tests to ensure everything is working

Run `make test` to run the tests.

## Create a new branch to work on your contribution

Run `git checkout -b my_contribution`

## Make your changes

Edit the files using your preferred editor.

## Format the code

Run `make fmt` to format the code.

## Run the linter

Run `make lint` to run the linter.

## Test your changes

Tests will be added soon!
<!-- 
Run `make test` to run the tests.

Ensure code coverage report shows `> 70%` coverage, add tests to your PR. -->

<!-- ## Build the docs locally

Run `make docs` to build the docs.

Ensure your new changes are documented. -->

## Commit your changes

Use any descriptive commit message! 

## Push your changes to your fork

Run `git push origin my_contribution`

## Submit a pull request

On github interface, click on `Pull Request` button.

Wait CI to run and one of the developers will review your PR.
## Makefile utilities

This project comes with a `Makefile` that contains a number of useful utility.

```bash 
❯ make
Usage: make <target>

Targets:
help:             ## Show the help.
install:          ## Install the project in dev mode.
fmt:              ## Format code using black & isort.
lint:             ## Run pep8, black, mypy linters.
test: lint        ## Run tests and generate coverage report.
watch:            ## Run tests on every change.
clean:            ## Clean unused files.
virtualenv:       ## Create a virtual environment.
release:          ## Create a new tag for release.
docs:             ## Build the documentation.
switch-to-poetry: ## Switch to poetry package manager.
init:             ## Initialize the project based on an application template.
```

## Making a New Release
This project uses [semantic versioning](https://semver.org/) and tags releases with `X.Y.Z`
Every time a new tag is created and pushed to the remote repo, github actions will
automatically create a new release on github and trigger a release on PyPI.


For this to work you need to setup a secret called `PIPY_API_TOKEN` on the project settings>secrets, 
this token can be generated on [pypi.org](https://pypi.org/account/).

To trigger a new release:
1. Bump the version number in `developergpt/VERSION`
2. Run formatting + linting + tests to make sure everything works 
3. Add and commit all changes 
4. Run `git tag v[new-version-number]` (should match the version number in `developergpt/VERSION`)
5. Push changes to Github with tags: `git push origin main --tags`


