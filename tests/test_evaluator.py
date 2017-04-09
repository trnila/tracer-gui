from unittest import TestCase

from tracergui.evaluator import evalme
from tracergui.objects.descriptor import Descriptor
from tracergui.objects.process import Process
from tracergui.objects.system import System


class TestEvaluator(TestCase):
    def setUp(self):
        self.sys = System("/tmp", {'processes': {}})

    def test_true(self):
        proc = Process(self.sys, {'descriptors': []})

        self.assertTrue(evalme("True", process=proc))
        self.assertFalse(evalme("False", process=proc))

    def test_is_file_exact_match(self):
        proc = Process(self.sys, {'descriptors': []})
        desc = Descriptor(proc, {'type': 'file', 'path': '/etc/hosts'})

        self.assertTrue(evalme("is_file('/etc/hosts')", descriptor=desc))
        self.assertTrue(evalme("is_file(exactmatch('/etc/hosts'))", descriptor=desc))
        self.assertFalse(evalme("is_file('/etc/passwd')", descriptor=desc))
        self.assertFalse(evalme("is_file(exactmatch('/etc/passwd'))", descriptor=desc))

    def test_is_file_contains(self):
        proc = Process(self.sys, {'descriptors': []})
        desc = Descriptor(proc, {'type': 'file', 'path': '/lib/libc.so.1'})

        self.assertTrue(evalme("is_file(contains('.so'))", descriptor=desc))
        self.assertFalse(evalme("is_file(contains('.dll'))", descriptor=desc))

    def test_is_file_startswith(self):
        proc = Process(self.sys, {'descriptors': []})
        desc = Descriptor(proc, {'type': 'file', 'path': '/lib/libc.so.1'})

        self.assertTrue(evalme("is_file(startswith('/lib'))", descriptor=desc))
        self.assertFalse(evalme("is_file(startswith('/usr/lib'))", descriptor=desc))

    def test_is_file_not(self):
        proc = Process(self.sys, {'descriptors': []})
        desc = Descriptor(proc, {'type': 'file', 'path': '/lib/libc.so.1'})

        self.assertFalse(evalme("is_file(Not(contains('.so')))", descriptor=desc))
        self.assertTrue(evalme("is_file(Not(contains('.dll')))", descriptor=desc))
        self.assertFalse(evalme("is_file(~contains('.so'))", descriptor=desc))
        self.assertTrue(evalme("is_file(Not(contains('.dll')))", descriptor=desc))
        self.assertTrue(evalme("is_file(~~contains('.so'))", descriptor=desc))
        self.assertTrue(evalme("is_file(Not(Not(contains('.so'))))", descriptor=desc))

    def test_is_file_and(self):
        proc = Process(self.sys, {'descriptors': []})
        desc = Descriptor(proc, {'type': 'file', 'path': '/lib/libc.so.1'})

        self.assertTrue(evalme("is_file(And(contains('.so'), contains('lib')))", descriptor=desc))
        self.assertFalse(evalme("is_file(And(contains('.so'), contains('dll')))", descriptor=desc))
        self.assertTrue(evalme("is_file(contains('.so') & contains('lib'))", descriptor=desc))
        self.assertFalse(evalme("is_file(contains('.so') & contains('dll'))", descriptor=desc))

    def test_is_file_or(self):
        proc = Process(self.sys, {'descriptors': []})
        desc = Descriptor(proc, {'type': 'file', 'path': '/lib/libc.so.1'})

        self.assertTrue(evalme("is_file(Or(contains('.so'), contains('dll')))", descriptor=desc))
        self.assertTrue(evalme("is_file(Or(contains('dll'), contains('.so')))", descriptor=desc))
        self.assertTrue(evalme("is_file(contains('.so') | contains('dll'))", descriptor=desc))
        self.assertTrue(evalme("is_file(contains('dll') | contains('.so'))", descriptor=desc))
        self.assertFalse(evalme("is_file(contains('x') | contains('z'))", descriptor=desc))

    def test_is_file_complex(self):
        proc = Process(self.sys, {'descriptors': []})
        desc = Descriptor(proc, {'type': 'file', 'path': '/lib/libc.so.1'})

        self.assertTrue(evalme("is_file(contains('.so') & (startswith('/lib') & ~contains('dll')) | endswith('.dll'))",
                               descriptor=desc))
        self.assertFalse(evalme("is_file(contains('.so') & (startswith('/lib') & ~contains('dll')) & endswith('.dll'))",
                                descriptor=desc))

    def test_use_and_or(self):
        proc = Process(self.sys, {'descriptors': []})
        desc = Descriptor(proc, {'type': 'file', 'path': '/lib/libc.so.1'})

        for expr in ["is_file(not contains('.so'))", "is_file(contains('.so') and contains('.so'))",
                     "is_file(contains('.so') or contains('.so'))"]:
            with self.assertRaisesRegex(SyntaxError, "operators not allowed"):
                self.assertTrue(evalme(expr, descriptor=desc))
