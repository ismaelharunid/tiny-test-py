# tiny-test-py
A tiny unit test that can batch function testings  by supplying a set of args and kwargs per function w/ optional tree.

# Installation
```
git clone <this repo url>
cd ./tiny-test-py
cp -r ./testpy /some/where/in/your/module/path/
```

# Usage as module
```
from testpy import *

def prod(*args):
    result = 1
    for v in args:
        result *= v
    return result

testitems = (
    # Op    args         kwargs  expected
    (OP.EQ, (1,2,3),     {},       6),
    (OP.EQ, (1,2,3,4,5), {},     120))

results = runtest(prod, testitems, verbosity=3)
Running <module>
[PASS] "prod(1, 2, 3)" expects 6, actual 6
[PASS] "prod(1, 2, 3, 4, 5)" expects 120, actual 120
<module>: 2 tests
```

Note that the test name ends up being reported as \<module\> because we ran the test from the console, instead of our test case function.  

# Usage from commandline
```
testpy
```
