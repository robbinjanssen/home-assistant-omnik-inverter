# Contributing

Contributions are **welcome** and will be fully **credited**.

We accept contributions via Pull Requests on [Github](https://github.com/robbinjanssen/home-assistant-omnik-inverter).

## Development environment

This project uses [uv](https://docs.astral.sh/uv/) and
[prek](https://github.com/j178/prek). Install uv, then:

```sh
uv sync                        # install Home Assistant and the development tools
uv run prek install            # run all checks on every commit
uv run prek run --all-files    # run all checks manually
uv run pytest                  # run the tests
```

## Pull Requests

- **[PEP 8 Coding Standard](https://www.python.org/dev/peps/pep-0008/)**.

- **Document any change in behaviour** - Make sure the `README.md` and any other relevant documentation are kept up-to-date.

- **Consider our release cycle** - We try to follow [SemVer v2.0.0](http://semver.org/). Randomly breaking public code is not an option.

- **Create feature branches** - Don't ask us to pull from your master branch.

- **One pull request per feature** - If you want to do more than one thing, send multiple pull requests.

- **Send coherent history** - Make sure each individual commit in your pull request is meaningful. If you had to make multiple intermediate commits while developing, please [squash them](http://www.git-scm.com/book/en/v2/Git-Tools-Rewriting-History#Changing-Multiple-Commit-Messages) before submitting.

---

**Happy coding**!
