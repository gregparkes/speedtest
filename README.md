# 🚀 speedtest

Performance profiling of code snippets in a PyTest-style format.

## 🙌 Features

* 👍 Automatic discovery and execution of speedtest functions.
* 👍 Intuitive / clean format with fixtures and parametrization capabilities.
* 👍 Automatic integration with project tools, such as pyproject.toml, .INI files, environment variables, dotenv... etc.
* 👍 Exporting of runs into CSV or TXT format.

## ✨ Inspiration

Python has the builtin `time` and `timeit` modules which in theory handle the heavy lifting of measuring a functions' execution time, but in practice I've often written lots of boilerplate to perform measurement of snippets in a more systematic way.

More often than not, I also don't want to embed profiling code within my Python module (such as wrapping methods with `time.perf_counter()`) for the purposes of testing development implementations.

## 👋 Hello World

Imagine using pytest, but instead of unit testing your codebase, it would perform speed testing on functions for you!

Define a Python source file 🐍 with the following code:

```python
# in speed_test.py
def speed_square():
    _ = [x ** 2 for x in range(1000000)]
```

To run speedtest ⚡, navigate to the directory containing your code and simply call it from command-line:

```bash
speedtest .
```

Producing the following result:

```bash
🐳sharksurf@Home:~/projects/test_project$ speedtest example
================================================= test session starts =================================================
Platform Linux -- Python 3.13.5, speedtest 0.1.0
collected 1 item, best of 3:

example/speed_square.py:speed_my_squarer ------------------- 20 loops  , 12.5 msec / loop
```

## 📋 Installation

Clone the repository to your local area and then install into your virtual environment, Poetry or uv using `pip`:

```bash
git clone https://github.com/gregparkes/speedtest.git
pip3 install .
```

The base installation has *no 3rd party dependencies*, however it is recommended to use some quality of life packages such as Rich, python-dotenv, use:

```
pip3 install .[all]
```

## 🔆 Examples

All examples must run within a `speed_`-named Python file.

### Basic test

Define any code within a `speed_` function to be activated with a speedtest:

```python
# speed_script.py
def speed_squarer():
    _ = [x ** 2 for x in range(1000000)]
```

Any function name can be **marked** for speed testing using a decorator:

```python
import speedtest

@speedtest.mark
def random_method():
    _ = [x ** 2 for x in range(1000000)]
```

### Fixtures

speedtest supports fixtures which run setup code prior to running the session. This is handy for any long computations like reading in files or network I/O which are a pre-requisite to getting any objects in an appropriate state for benchmarking.

```python
import speedtest

@speedtest.fixture
def purpose_of_life():
    return 42

def speed_mult(purpose_of_life):
    # dict is provided as input.
    _ = [x * purpose_of_life for x in range(1000)]
```

The same fixture can be used with multiple test functions:

```python
@speedtest.fixture
def a():
    return 42

def speed_b(a):
    return x ** a

def speed_c(a):
    return x // a
```

Or multiple different fixtures can be used within the same speedtest:

```python
@speedtest.fixture
def a():
    return 42

@speedtest.fixture
def b():
    return 69

def speed_c(a, b):
    return a + b
```

Fixtures MUST be defined in the file in which they are used. Fixtures can only be defined on non-speed tested functions.

### Parametrization

speedtest ⚡ supports the capability to provide different *basic* arguments to your speed testing, for example it is a common use-case to vary over 1 or more parameters and test the speed relative to each parameter combination.

```python
import speedtest
# speed_param.py
@speedtest.parametrize("n", [1000, 10000, 100000])
def speed_square(n):
    _ = [x ** 2 for x in range(n)]
```

In the above example, we vary over the range parameter and speed-test each instance, this would produce the following result (timings may vary):

```bash
sharksurf@Home:~/projects/test_project$ uv run speedtest example2
================================================= test session starts =================================================
Platform Linux -- Python 3.13.5, speedtest 0.1.0
collected 1 item, best of 3:

example2/speed_param.py:speed_square[n=1000] -------------- 5000 loops, 88.1 μsec / loop
example2/speed_param.py:speed_square[n=10000] ------------- 500 loops , 917.6 μsec / loop
example2/speed_param.py:speed_square[n=100000] ------------ 20 loops  , 12.3 msec / loop
```

#### Multiple arguments

speedtest ⚡ supports multiple arguments, supplied as a list of tuples:

```python
@speedtest.parametrize("n, pow_fac", [(1000, 2), (10000, 3), (100000, 4)])
def speed_my_squarer2(n, pow_fac):
    _ = [x ** pow_fac for x in range(n)]
```

Leading to:

```bash
example2/speed_param.py:speed_squarer2[n=1000,pow_fac=2] --- 5000 loops, 87.3 μsec / loop
example2/speed_param.py:speed_squarer2[n=10000,pow_fac=3] -- 200 loops , 1395.0 μsec / loop
example2/speed_param.py:speed_squarer2[n=100000,pow_fac=4] - 10 loops  , 21.0 msec / loop
```

Combinations of arguments can be combined more easily using `itertools.product`:

```python
import itertools as it

@speedtest.parametrize("n, pow_fac", it.product([1000, 10000, 100000],[2, 3, 4]))
def speed_squarer3(n, pow_fac):
    _ = [x ** pow_fac for x in range(n)]
```

Leading to 3x3 speed-tests.

### Other useful arguments 🔑

#### Compare Time units

By default, speedtest will print/display timing units that is closest to the relevant precision using `--unit auto`; to enable comparison along one unit scale (i.e 'ms') set `--unit ms`.

#### Parallelism

speedtest ⚡ supports parallel computation out-of-the-box using the `--parallel` flag. Unfortunately print statements do not appear when using multiprocessing until the end of the run.

#### CSV output

Tabulated results by name, time taken and parameter are provided using the `--tocsv` flag. This produces a file called `runX.csv` in the immediate directory.

#### TXT output

Logged results as displayed in the console can be produced using the `--totxt` flag. This produces a file called `runX.txt` in the immediate directory.

#### Printing

Print commands can be enhanced using `--verbose` or suppressed using `--quiet`.

## 🔨 Configuration

Setting up your project to use speedtest has never been easier - use one or more of the following approaches depending on how you've set up a project:

### `pyproject.toml`

Arguments passed to `speedtest` can be defined in the `pyproject.toml` file of a project you're working on instead of directly, use `tool.speedtest`:

```toml
# pyproject.toml
[tool.speedtest]
unit = ms
parallel = true
```

Note that arguments defined in the command-line will override arguments defined in the TOML.

### `.ini` files

A more old-fashioned but certainly valid way to pass parameter is using a custom .INI file. Create a `speedtest.ini` in your directory and populate it with:

```ini
# speedtest.ini
[speedtest]
unit = ms
parallel = true
```

### Environment variables

If `python-dotenv` is installed, speedtest ⚡ will automatically search for a `.env` file in the local directory of the speedtest run. Environment variables must begin with the "**SPEEDTEST_**" prefix. This `.env` can include things like:

```bash
# .env
SPEEDTEST_PARALLEL=1
```

### Caching

speedtest ⚡ will create a '.speedtest_cache' directory in the local directory where speedtest is executed. This cache helps to accelerate multiple calls to `speedtest` by storing the best nloops and other parameters. To stop this cache creation, use the `--no-cache` flag.

## ❓ FAQ

#### Q: Number of loops abnormally low/high after I've made changes to the speed function?

A: speedtest caches the best `nloops` the first time the function is run, and stores it in the `.speedtest_cache` folder. This helps to speed up repetitive calls to speedtest, but can mis-calibrate your speedtest run if significant code changes are made to the underlying function.

You can either:

* Delete `.speedtest_cache/` folder.
* Use `--ignore-cache` flag to ignore the cache file and override it.

## License

This project is distributed under the MIT license. For further details read [LICENSE.txt](license.txt).