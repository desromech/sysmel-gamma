#!/usr/bin/env python3

import unittest
from parser import parser

class TestParser(unittest.TestCase):
    def parseString(self, string):
        return parser.parse(string)
        
    def test_empty(self):
        print(self.parseString(''))

if __name__ == '__main__':
    unittest.main()