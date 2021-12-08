import os
import unittest
from shutil import copyfile


class Test(unittest.TestCase):

    @staticmethod
    def output(path):
        out_string = ''
        with open(path, 'r') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                out_string += line.strip()
        return out_string.strip('\n')

    def test_sample_1(self):
        for i in range(1, 11):
            with self.subTest(i=i):
                copyfile(f'PA1_testcases1.3/T{i:02d}/input.txt', 'input.txt')
                os.system('python compiler.py')
                self.assertMultiLineEqual(Test.output(f'PA1_testcases1.3/T{i:02d}/symbol_table.txt'), Test.output('symbol_table.txt'))
                self.assertMultiLineEqual(Test.output(f'PA1_testcases1.3/T{i:02d}/tokens.txt'), Test.output('tokens.txt'))
                self.assertMultiLineEqual(Test.output(f'PA1_testcases1.3/T{i:02d}/lexical_errors.txt'), Test.output('lexical_errors.txt'))

    def test_sample_2(self):
        for i in range(11, 16):
            with self.subTest(i=i):
                copyfile(f'PA1_testcases1.3/T{i:02d}/input.txt', 'input.txt')
                os.system('python compiler.py')
                self.assertMultiLineEqual(Test.output(f'PA1_testcases1.3/T{i:02d}/tokens.txt'), Test.output('tokens.txt'))
                self.assertMultiLineEqual(Test.output(f'PA1_testcases1.3/T{i:02d}/lexical_errors.txt'), Test.output('lexical_errors.txt'))
                self.assertMultiLineEqual(Test.output(f'PA1_testcases1.3/T{i:02d}/symbol_table.txt'), Test.output('symbol_table.txt'))





