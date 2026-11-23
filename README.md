# LocalPlayer

## Install and run

This project uses a `src/` package layout. Install it once in the Python
environment you want to use, from the project root:

```bash
python -m pip install -e .
```

The `-e` option installs the project in editable mode: Python can import the
`localplayer` package from `src/`, and changes to the source files take effect
without reinstalling.

After installation, run the app from the project root or another directory:

```bash
python -m localplayer
```

The package also provides this command:

```bash
localplayer
```

If using the project's virtual environment, activate it before installing and
running. On Linux and macOS:

```bash
source .venv/bin/activate
python -m pip install -e .
python -m localplayer
```

You can also use the environment's Python directly:

```bash
.venv/bin/python -m pip install -e .
.venv/bin/python -m localplayer
```

## How Python imports work here

`src/localplayer/` is the package directory. The import name is `localplayer`,
not `src` and not `localplayer/src`. For example, code inside the project can
import another module with:

```python
from localplayer.core.paths import get_app_dir
```

Python looks for import names in its module search path (`sys.path`). When a
file is started directly, Python puts that file's directory on the path; this
does not reliably make the sibling package directory `src/` available. Editable
installation tells Python where this project's package lives, so imports work
from scripts and the app can be launched from any working directory.

For code that belongs to the package, prefer package imports such as
`from localplayer.core.paths import get_app_dir`, and run package entry points
with `python -m localplayer`. Avoid changing `sys.path` inside each new file:
that hides the packaging issue and makes imports depend on how the file was
launched.

For a module inside the package, relative imports also work, for example
`from .paths import get_app_dir` from another module in `localplayer.core`.
Absolute package imports are used in this project so the full package path is
clear.