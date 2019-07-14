import json
import unittest

import quickjs


class LoadModule(unittest.TestCase):
    def test_42(self):
        self.assertEqual(quickjs.test(), 42)


class Context(unittest.TestCase):
    def setUp(self):
        self.context = quickjs.Context()

    def test_eval_int(self):
        self.assertEqual(self.context.eval("40 + 2"), 42)

    def test_eval_float(self):
        self.assertEqual(self.context.eval("40.0 + 2.0"), 42.0)

    def test_eval_str(self):
        self.assertEqual(self.context.eval("'4' + '2'"), "42")

    def test_eval_bool(self):
        self.assertEqual(self.context.eval("true || false"), True)

    def test_eval_null(self):
        self.assertIsNone(self.context.eval("null"))

    def test_eval_undefined(self):
        self.assertIsNone(self.context.eval("undefined"))

    def test_wrong_type(self):
        with self.assertRaises(TypeError):
            self.assertEqual(self.context.eval(1), 42)

    def test_context_between_calls(self):
        self.context.eval("x = 40; y = 2;")
        self.assertEqual(self.context.eval("x + y"), 42)

    def test_function(self):
        self.context.eval("""
            function special(x) {
                return 40 + x;
            }
            """)
        self.assertEqual(self.context.eval("special(2)"), 42)

    def test_error(self):
        with self.assertRaisesRegex(quickjs.JSException, "ReferenceError: missing is not defined"):
            self.context.eval("missing + missing")


class Object(unittest.TestCase):
    def setUp(self):
        self.context = quickjs.Context()

    def test_function_is_object(self):
        f = self.context.eval("""
            a = function(x) {
                return 40 + x;
            }
            """)
        self.assertIsInstance(f, quickjs.Object)

    def test_function_call_int(self):
        f = self.context.eval("""
            f = function(x) {
                return 40 + x;
            }
            """)
        self.assertEqual(f(2), 42)

    def test_function_call_int_two_args(self):
        f = self.context.eval("""
            f = function(x, y) {
                return 40 + x + y;
            }
            """)
        self.assertEqual(f(3, -1), 42)

    def test_function_call_str(self):
        f = self.context.eval("""
            f = function(a) {
                return a + " hej";
            }
            """)
        self.assertEqual(f("1"), "1 hej")

    def test_function_call_str_three_args(self):
        f = self.context.eval("""
            f = function(a, b, c) {
                return a + " hej " + b + " ho " + c;
            }
            """)
        self.assertEqual(f("1", "2", "3"), "1 hej 2 ho 3")

    def test_function_call_object(self):
        d = self.context.eval("d = {data: 42};")
        f = self.context.eval("""
            f = function(d) {
                return d.data;
            }
            """)
        self.assertEqual(f(d), 42)
        # Try again to make sure refcounting works.
        self.assertEqual(f(d), 42)
        self.assertEqual(f(d), 42)

    def test_function_call_unsupported_arg(self):
        f = self.context.eval("""
            f = function(x) {
                return 40 + x;
            }
            """)
        with self.assertRaisesRegex(ValueError, "Unsupported type"):
            self.assertEqual(f({}), 42)

    def test_json(self):
        d = self.context.eval("d = {data: 42};")
        self.assertEqual(json.loads(d.json()), {"data": 42})
