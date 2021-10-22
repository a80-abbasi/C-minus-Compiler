import unittest
from shutil import copyfile

class Test(unittest.TestCase):

    @staticmethod
    def output(path):
        with open(path, 'r') as f:
            out_string = f.read()
        return out_string.strip('\n')

    def test_sample_1(self):
        for i in range(1, 11):
            copyfile(f'PA1_testcases1.3/T{i:02d}/input.txt', 'input.txt')
            with open('compiler.py') as compiler:
                exec(compiler.read())
            self.assertEqual(Test.output(f'PA1_testcases1.3/T{i:02d}/symbol_table.txt'), Test.output('symbol_table.txt'))
            self.assertEqual(Test.output(f'PA1_testcases1.3/T{i:02d}/tokens.txt'), Test.output('tokens.txt'))
            self.assertEqual(Test.output(f'PA1_testcases1.3/T{i:02d}/lexical_errors.txt'), Test.output('lexical_errors.txt'))
            print(f'Test {i} Passed!')




