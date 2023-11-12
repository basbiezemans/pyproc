from unittest import TestCase
from operator import add
from functools import reduce

from src.proc import Proc

class TestProc(TestCase):

    def test_calling_proc_as_function(self):
        f = Proc(lambda x: x * x)
        g = Proc(lambda x: x + x)
        h = Proc(lambda a, b: [a,b])
        v = Proc(lambda *a: reduce(add, a, 0))
        self.assertEqual(n := f(2), 4, f"4 expected, got: {n}")
        self.assertEqual(n := g(3), 6, f"3 expected, got: {n}")
        self.assertEqual(a := h(1, 2), [1,2], f"[1,2] expected, got: {a}")
        self.assertEqual(n := v(1, 2, 3), 6, f"6 expected, got: {n}")
        with self.assertRaises(TypeError):
            h(1, 2, 3) # too many arguments

    def test_proc_arity(self):
        f = Proc(lambda: None)
        g = Proc(lambda x: x + x)
        h = Proc(lambda a, b: [a,b])
        v = Proc(lambda *a: a)
        self.assertEqual(n := f.arity, 0, f"0 expected, got: {n}")
        self.assertEqual(n := g.arity, 1, f"1 expected, got: {n}")
        self.assertEqual(n := h.arity, 2, f"2 expected, got: {n}")
        self.assertEqual(n := v.arity, 1, f"1 expected, got: {n}")

    def test_curried_proc_is_variadic(self):
        b = Proc(lambda x, y, z: x + y + z)
        v = Proc(lambda *a: a)
        self.assertTrue(v.curry(None).is_variadic)
        self.assertFalse(b.curry(None).is_variadic)

    def test_curried_proc(self):
        b = Proc(lambda x, y, z: x + y + z)
        self.assertEqual(n := b.curry(1)(2)(3), 6, f"6 expected, got: {n}")
        self.assertEqual(n := b.curry(1, 2)(3), 6, f"6 expected, got: {n}")
        self.assertEqual(n := b.curry(1)(2, 3), 6, f"6 expected, got: {n}")
        self.assertEqual(n := b.curry()(1,2,3), 6, f"6 expected, got: {n}")
        with self.assertRaises(TypeError):
            b.curry(1)(2)(3)(4) # too many arguments

    def test_double_curried_proc(self):
        b = Proc(lambda x, y, z: x + y + z)
        c = b.curry(1).curry(2,3) # creates 2 curried versions of b
        self.assertEqual(n := c.call(4), 9, f"9 expected, got: {n}")

    def test_curried_proc_composition(self):
        proc = Proc(lambda x, y, z: x + y + z)
        add2 = Proc(add).curry(2)
        have = (proc.curry(1,2) << add2).call(3)
        self.assertEqual(have, 8, f"8 expected, got: {have}")

    def test_variadic_curried_proc(self):
        b = Proc(lambda x, y, z, *w: x + y + z + reduce(add, w, 0))
        v = Proc(lambda *a: a)
        self.assertEqual(t := v.curry(1)(), (1,), f"(1,) expected, got: {t}")
        self.assertEqual(t := v.curry()(1)(2)(), (1,2), f"(1,2) expected, got: {t}")
        self.assertEqual(t := v.curry(1)(2)(3)(), (1,2,3), f"(1,2,3) expected, got: {t}")
        self.assertEqual(n := b.curry(1)(2)(3)(), 6, f"6 expected, got: {n}")
        self.assertEqual(n := b.curry(1, 2)(3, 4)(), 10, f"10 expected, got: {n}")
        self.assertEqual(n := b.curry(1)(2)(3)(4)(5)(), 15, f"15 expected, got: {n}")
        self.assertEqual(n := b.curry(1, 2)(3, 4)(5)(), 15, f"15 expected, got: {n}")

    def test_proc_composition(self):
        f = Proc(lambda x: x * x)
        g = Proc(lambda x: x + x)
        self.assertEqual(n := (f >> g).call(2), 8,  f"8 expected, got: {n}")
        self.assertEqual(n := (f << g).call(2), 16, f"16 expected, got: {n}")

    def test_proc_variable_args(self):
        proc = Proc(lambda scalar, *values: list(map(lambda v: v * scalar, values)))
        want = [9, 18, 27]
        have = proc.call(9, 1, 2, 3)
        self.assertEqual(want, have, f"{want} expected, got {have}")

    def test_proc_object_as_closure(self):
        def gen_times(factor):
            return Proc(lambda n: n * factor)
        times3 = gen_times(3)
        times5 = gen_times(5)
        a = times3.call(12)
        b = times5.call(5)
        c = times3.call(times5.call(4))
        self.assertEqual(a, 36, f"36 expected, got: {a}")
        self.assertEqual(b, 25, f"25 expected, got: {b}")
        self.assertEqual(c, 60, f"60 expected, got: {c}")

    def test_create_proc_with_decorator(self):
        @Proc
        def add2(x):
            return x + 2
        self.assertEqual(n := add2.call(1), 3, f"3 expected, got: {n}")

    def test_create_proc_with_callable(self):
        class Multiplier:
            def __init__(self, factor):
                self.factor = factor
            def __call__(self, n):
                return n * self.factor
        times3 = Proc(Multiplier(3))
        self.assertEqual(n := times3.arity, 1, f"1 expected, got: {n}")
        self.assertEqual(n := times3.call(12), 36, f"36 expected, got: {n}")