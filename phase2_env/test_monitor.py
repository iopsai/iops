import unittest
from .monitor_test import *


class TestReadNonEmptyLine(unittest.TestCase):
    def test(self):
        import io
        src = io.StringIO("\na\nb\nc\n\nd\n\n")
        self.assertEqual(read_non_empty_line(src), "a")
        self.assertEqual(read_non_empty_line(src), "b")
        self.assertEqual(read_non_empty_line(src), "c")
        self.assertEqual(read_non_empty_line(src), "d")
        self.assertEqual(read_non_empty_line(src), None)
