Before contributing to the project, please take note of the following guidelines.

Development Environment Setup
-----------------------------
To do development locally, first clone the code from gitHub and set up a local development environment:

1. Clone the repository locally using the https link for GitHub repo.:
    ```
   $ git clone <link to clone repo>
   ```
2. Set up a virtual environment (or conda environment). Although not mandatory, it is highly
   recommended separating each project's python environment. To create a virtual environment
   in the project directory itself with the native Python environment manager `venv`:
    ```bash
    $ cd /path/to/project/directory
    $ python3 -m venv .venv #sets up a new virtual env called .venv
    ```
   Next, to activate the virtual environment (say `.venv`):
    ```bash
    $ source .venv/Scripts/activate
    ```
3. Run `pip install -r requirements.txt` to install dependencies
4. To run a python script
   ```bash
   $ python -m app -a <api_name> <other parameters to be passed>
   ```
   To see a list of possible parameters:
   ```bash
   $ python -m app --help
   ```
5. To deactivate the virtual environment, simply run `deactivate`


Sub-versioning Etiquette
------------------------
1. Fork out a local branch from local `develop` for local development or for new features. E.g. to make a local
   branch called `feature-123`:
    ```bash
    $ git checkout -b feature-1234
    ```
    1. To ensure that the local `develop` branch is up to date with remote, pull changes
       on `origin/develop` with `git pull` first, and merge it into local branch `develop`.
    2. Alternatively, a branch can also be created on gitHub website, by creating an issue and checking out a branch for
       the issue. Once a branch is created on origin, say `issue-1234` this can be pulled to local with:
       ```shell
       $ git fetch origin
       $ git checkout issue-1234
       ```
2. Commit changes locally. It is recommended to have only similar changes, or changes under
   only one topic in each commit. Changes for formatting and whitespaces e.g. should never go
   under the same commit as changes for logic. To check current status of changes on local branch:
   ```bash
   $ git status
   ```
   To commit changes on certain files, and then commit with commit message:
   ```bash
   $ git add /paths/to/files/separated/by/space
   $ git commit -m "meaningful commit message"
   ```
3. Set an upstream branch for local `feature-1234` and push changes to it
   ```bash
   $ git push -u origin feature-1234
   ```
   If an upstream has already been set up, then simply run `git push`
4. After making changes, summarize them using semantic-versioning on the [Changelog](../CHANGELOG.md) and ensure that
the version of the app has been appropriately bumped across the app-code.
5. Once all changes are ready to be merged to `origin/develop`, create a Pull-Request on
gitHub for merging changes from the feature/issue branch on origin e.g. `origin/feature-1234` or
`issue-1234` above into `origin/develop`. Assign the PR to a maintainer



Testing
-------
Tests are added in the `tests` dir, with similar directory structure as `app`.
1. To run all tests simply run:
   ```bash 
   $ pytest 
   ```
2. To run all the tests from one directory, use the directory as a parameter to pytest:
   ```bash
   $ pytest tests/my-directory
   ```
3. To run all tests in a file , list the file with the relative path as a parameter to pytest:
   ```bash
   $ pytest tests/my-directory/test_demo.py
   ```
4. To run a set of tests based on function names, the -k option can be used
   For example, to run all functions that have _raises in their name:
   ````shell
   $ pytest -v -k _raises
   ````
