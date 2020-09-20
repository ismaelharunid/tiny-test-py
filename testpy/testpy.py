

import inspect
try:
    from collections.abc import Mapping, MutableSequence, Sequence
except:
    from collections import Mapping, MutableSequence, Sequence



def argsrepr(l):
    return ', '.join("{:}".format(repr(v)) for v in l)

def kwargsrepr(d):
    return ', '.join("{:}={:}".format(n, repr(v))
                     for (n, v) in d.items())

def shortrepr(value, maxlen=10):
    return shorten(repr(value), maxlen)

def shorten(text, maxlen=10):
    assert isinstance(text, str), "text must be string-like"
    l_text = len(text)
    if "\n" in text:
        i0, i1 = text.index("\n"), text.rindex("\n")
        if i0 > maxlen:
            l0 = max(0, maxlen - 3, maxlen - min(maxlen, l_text - i1))
        i1 = l_text - min(maxlen - i0, l_text - i1)
        return text[:i0+1] + text[i1+1:]
    elif len(text) > maxlen:
        i0 = (maxlen + 1) // 2
        i1 = l_text - max(0, maxlen-i0)
        return ''.join((text[:i0], '..', text[i1:]))
    return text


def argrepr(args=(), kwargs={}, maxlen=18):
    text = ', '.join(tuple(repr(v) for v in args)
                    + tuple("{:}={:}".format(n, repr(v))
                            for (n, v) in kwargs.items()))
    if maxlen:
        return shorten(text, maxlen)
    return text


TAGTESTS = dict(BOOL=(lambda a, b: bool(a) == b),
                INT=(lambda a, b: int(a) == b),
                FLOAT=(lambda a, b: int(a) == b),
                STR=(lambda a, b: str(a) == b),
                REPR=(lambda a, b: repr(a) == b),
                EQ=(lambda a, b: a == b),
                NE=(lambda a, b: a != b),
                IS=(lambda a, b: a is b),
                ISNOT=(lambda a, b: a is not b),
                INSTANCE=(lambda a, b: isinstance(a, b)),
                NOTINSTANCE=(lambda a, b: not isinstance(a, b)),
                SUBCLASS=(lambda a, b: issubclass(a, b)),
                NOTSUBCLASS=(lambda a, b: not issubclass(a, b)),
                RAISE=(lambda a, b=Exception: isinstance(a, b)),
                ELSE=(lambda a, b=Exception: not isinstance(a, b)))


def runtest_item(function, tag, args, kwargs, expects,
                 verbosity=1, results=None, shortenargs=18):
    funcname = function.__code__.co_name
    if not callable(tag):
        if type(tag) is not str or not tag in TAGTESTS:
            raise ValueError("for {:}, tag {:} is not supported"
                             .format(funcname, tag))
        tag = TAGTESTS[tag]
    if not isinstance(args, Sequence):
        raise ValueError(("for {:}, args must be a "
                          "Sequence, not {:}")
                         .format(funcname, type(args).__name__))
    if not isinstance(kwargs, Mapping):
        raise ValueError(("for {:}, kwargs must be a "
                          "Mapping, not {:}")
                         .format(funcname, type(kwargs).__name__))
    code = "{}({})" \
            .format(funcname, argrepr(args, kwargs, maxlen=shortenargs))
    count = succ = fail = errors = 0
    try:
        #with testlocals:
        #    result = function(*args, **kwargs)
        result = function(*args, **kwargs)
        if isinstance(expects, Exception) or result != expects:
            fail += 1
            if verbosity > 1:
                print("[FAIL] \"{:}\" expects {:}, actual {:}"
                      .format(code, expects, result))
        else:
            succ += 1
            if verbosity > 2:
                print("[PASS] \"{:}\" expects {:}, actual {:}"
                      .format(code, expects, result))
    except Exception as exc:
        if issubclass(expects, Exception) and isinstance(exc, expects):
            succ += 1
            if verbosity > 2:
                print("[PASS] \"{:}\" {:}".format(code, exc))
        else:
            errors += 1
            if verbosity > 0:
                print("[ERROR]\"{:}\" {:}".format(code, exc))
    count += 1
    if isinstance(results, Mapping):
        results.update(count=count,
                       success=succ,
                       failures=fail,
                       errors=errors)
        if "functions" in results:
            res = results["functions"].setdefault(function, {})
            res.update(count=res.get("count", 0)+count,
                       success=res.get("success", 0)+succ,
                       failures=res.get("failures", 0)+fail,
                       errors=res.get("errors", 0)+errors)
    return (function, code, count, succ, fail, errors)


def runtest(function, testvalues, verbosity=1, shortenargs=18, results=None):
    testname = inspect.currentframe().f_back.f_code.co_name
    if verbosity > 2:
        print("Running {:}".format(testname))
    if isinstance(results, Mapping):
        results = results.setdefault("tests", {}).setdefault(testname, {})
        results.update(count=results.get("count", 0),
                       success=results.get("success", 0),
                       failures=results.get("failures", 0),
                       errors=results.get("errors", 0),
                       functions=results.get("functions", {}),
                       tests=results.get("tests", {}))
    counts = successes = failures = errors = 0
    for (line, (tag, args, kwargs, expects)) in enumerate(testvalues):
        func, code, count, succ, fail, err = \
                runtest_item(function, tag, args, kwargs, expects,
                             verbosity=verbosity, results=results,
                             shortenargs=shortenargs)
        counts += count
        successes += succ
        failures += fail
        errors += err
    if (counts != successes and verbosity > 0) or verbosity > 1:
        print("{:s}: {:d} tests\n{:7d} passed\n{:7d} failed\n{:7d} errors"
              .format(testname, counts, successes, failures, errors))
    return (testname, counts, successes, failures, errors)


OP = type('OPS', (), TAGTESTS)


