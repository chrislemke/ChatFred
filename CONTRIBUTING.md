# How to contribute
Thank 🙏 you for your interest in contributing to this project! Please read this document to get started.

## Pre-commit hooks
We are using [pre-commit](https://pre-commit.com/) to ensure a consistent code style and to avoid common mistakes. Please install the [pre-commit](https://pre-commit.com/#installation) and install the hook with:
```bash
pre-commit install
pre-commit install --hook-type commit-msg
```

## Conventional Commits
We are using [Conventional Commits](https://www.conventionalcommits.org) to ensure a consistent commit message style. Please use the following commit message format:
```bash
<type>[optional scope]: <description>
```
E.g.:
```bash
add: new fantastic feature
```

## How to contribute
The following steps will give a short guide on how to contribute to this project:

- Create a personal [fork](https://github.com/chrislemke/ChatFred/fork) of the project on [GitHub](https://github.com/).
- Clone the fork on your local machine. Your remote repo on [GitHub](https://github.com/) is called `origin`.
- Add the original repository as a remote called `upstream`.
- If you created your fork a while ago be sure to pull upstream changes into your local repository.
- Create a new branch to work on! Start from `develop`.
- Implement/fix your feature, comment your code, and add some examples.
- Follow the code style of the project, including indentation. [Black](https://github.com/psf/black), [Ruff](https://github.com/charliermarsh/ruff), [mypy](https://github.com/python/mypy), and [ssort](https://github.com/bwhmather/ssort) can help you with it.
- Run all tests - if available.
- Write or adapt tests as needed.
- Add or change the documentation as needed. Please follow the "[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)".
- Squash your commits into a single commit with git's [interactive rebase](https://help.github.com/articles/interactive-rebase). Create a new branch if necessary.
- Push your branch to your fork on [GitHub](https://github.com/), the remote `origin`.
- From your fork open a pull request in the correct branch. Target the project's `develop` branch!
- Once the pull request is approved and merged you can pull the changes from `upstream` to your local repo and delete
your extra branch(es).
