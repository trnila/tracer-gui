from unittest import TestCase

from Evaluator import evalme
from TracedData import Process, System, Descriptor


class TestEvaluator(TestCase):
    def test_true(self):
        sys = System("/tmp", {})
        proc = Process(sys, {'descriptors': []})

        self.assertTrue(evalme("True", process=proc))
        self.assertFalse(evalme("False", process=proc))

    def test_is_file_exact_match(self):
        sys = System("/tmp", {})
        proc = Process(sys, {'descriptors': []})
        desc = Descriptor(proc, {'type': 'file', 'path': '/etc/hosts'})

        self.assertTrue(evalme("is_file('/etc/hosts')", descriptor=desc))
        self.assertTrue(evalme("is_file(exactmatch('/etc/hosts'))", descriptor=desc))
        self.assertFalse(evalme("is_file('/etc/passwd')", descriptor=desc))
        self.assertFalse(evalme("is_file(exactmatch('/etc/passwd'))", descriptor=desc))

    def test_is_file_contains(self):
        sys = System("/tmp", {})
        proc = Process(sys, {'descriptors': []})
        desc = Descriptor(proc, {'type': 'file', 'path': '/lib/libc.so.1'})

        self.assertTrue(evalme("is_file(contains('.so'))", descriptor=desc))
        self.assertFalse(evalme("is_file(contains('.dll'))", descriptor=desc))

    def test_is_file_startswith(self):
        sys = System("/tmp", {})
        proc = Process(sys, {'descriptors': []})
        desc = Descriptor(proc, {'type': 'file', 'path': '/lib/libc.so.1'})

        self.assertTrue(evalme("is_file(startswith('/lib'))", descriptor=desc))
        self.assertFalse(evalme("is_file(startswith('/usr/lib'))", descriptor=desc))

    def test_is_file_not(self):
        sys = System("/tmp", {})
        proc = Process(sys, {'descriptors': []})
        desc = Descriptor(proc, {'type': 'file', 'path': '/lib/libc.so.1'})

        self.assertFalse(evalme("is_file(Not(contains('.so')))", descriptor=desc))
        self.assertTrue(evalme("is_file(Not(contains('.dll')))", descriptor=desc))
        self.assertFalse(evalme("is_file(~contains('.so'))", descriptor=desc))
        self.assertTrue(evalme("is_file(Not(contains('.dll')))", descriptor=desc))
        self.assertTrue(evalme("is_file(~~contains('.so'))", descriptor=desc))
        self.assertTrue(evalme("is_file(Not(Not(contains('.so'))))", descriptor=desc))
