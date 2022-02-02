from typing import Any

class SymbolTable:
    def __init__(self):
        self.table = []
        self.addr = 100

    def add_var(self, lexeme, type, scope):
        self.table.append({'lexeme': lexeme, 'type': type, 'scope': scope, 'kind': 'var', 'addr': self.addr})
        self.update_addr(type)

    def add_arr(self, lexeme, type, num, scope):
        self.table.append(
            {'lexeme': lexeme, 'type': type + '*', 'num': num, 'scope': scope, 'kind': 'var', 'addr': self.addr})
        self.update_addr(type, int(num))

    def add_func(self, lexeme, type, scope):
        self.table.append({'lexeme': lexeme, 'type': type, 'scope': scope, 'kind': 'func', 'addr': self.addr})
        self.update_addr(type)

    def add_var_param(self, lexeme, type, scope):
        self.table.append({'lexeme': lexeme, 'type': type, 'scope': scope, 'kind': 'param', 'addr': self.addr})
        self.update_addr(type)

    def add_arr_param(self, lexeme, type, scope):
        self.table.append({'lexeme': lexeme, 'type': type + '*', 'scope': scope, 'kind': 'param', 'addr': self.addr})
        self.update_addr(type)

    def update_addr(self, type, num=1):
        self.addr += 4 * num

    def get_row(self, id):
        one = True
        for i, row in zip(range(len(self.table) - 1, -1, -1), self.table[::-1]):
            if row['scope'] == 0:
                one = False
                if row['lexeme'] == id:
                    return i, row
            elif one:
                if row['lexeme'] == id:
                    return i, row


class CodeGenerator:
    def __init__(self):
        self.table = SymbolTable()
        self.stack = []
        self.pb = []
        self.scope = 0
        self.i = 0
        self.arg_counter = 0
        self.func_row = None
        self.temp = 996

    def get_temp(self):
        self.temp += 4
        return self.temp

    def push(self, val):
        self.stack.append(val)

    def pop(self, n=1):
        for i in range(n):
            self.stack.pop()

    def add_op(self, op, x: Any = '', y: Any = '', z: Any = '', i: int = None):
        self.add_code(f'({op}, {x}, {y}, {z})', i)

    def add_code(self, code, i=None):
        if i is None:
            self.pb.append(code)
            self.i += 1
        else:
            self.pb[i] = code

    def code_gen(self, action: str, look_ahead):
        if action == 'push':
            self.push(look_ahead)
        elif action == 'var_declare':
            self.table.add_var(self.stack[-1], self.stack[-2], self.scope)
            self.pop(2)
        elif action == 'arr_declare':
            # todo: void error
            self.table.add_arr(self.stack[-2], self.stack[-3], self.stack[-1], self.scope)
            # todo: take space for array?
            self.pop(3)
        elif action == 'scope+':
            self.scope += 1
        elif action == 'scope-':
            self.scope -= 1
        elif action == 'var_param':
            self.table.add_var_param(self.stack[-1], 'int', self.scope)
            self.arg_counter += 1
            self.pop(1)
        elif action == 'arr_param':
            self.table.add_arr_param(self.stack[-1], 'int', self.scope)
            self.arg_counter += 1
            self.pop(1)
        elif action == 'func_declare':
            self.table.add_func(self.stack[-1], self.stack[-2], self.scope)
            self.func_row = self.table.table[-1]
            self.arg_counter = 0
            self.pop(2)
        elif action == 'process_func':
            self.func_row['num'] = self.arg_counter
            self.func_row['code_adrr'] = self.i
            self.arg_counter = 0
            self.func_row = None
        elif action == 'save':
            self.push(self.i)
            self.i += 1
        elif action == 'jpf':
            self.add_op('JPF', self.stack[-2], self.i, i=self.stack[-1])
            self.pop(2)
        elif action == 'jp':
            self.add_op('JP', self.i, i=self.stack[-1])
            self.pop(1)
        elif action == 'jpf_save':
            self.add_op('JPF', self.stack[-2], self.i + 1, i=self.stack[-1])
            self.pop(2)
            self.push(self.i)
            self.i += 1
        elif action == 'pid':
            _, row = self.table.get_row(look_ahead)
            self.push(row['addr'])
        elif action == 'assign':
            self.add_op('ASSIGN', self.stack[-1], self.stack[-2])
            self.pop(2)
        elif action == 'get_arr':
            t = self.get_temp()
            self.add_op('MULT', self.stack[-1], 4, t)
            self.pop()
            t2 = self.get_temp()
            self.add_op('ADD', t, f'#{self.stack[-1]}', t2)
            self.pop()
            self.push(t2)
        elif action == 'relop':
            a, relop, b = self.stack[-3:]
            t = self.get_temp()
            if relop == '==':
                self.add_op('EQ', a, b, t)
            else:
                self.add_op('LT', a, b, t)
            self.pop(3)
            self.push(t)
        elif action == 'add_sub':
            a, add_sub, b = self.stack[-3:]
            t = self.get_temp()
            if add_sub == '+':
                self.add_op('ADD', a, b, t)
            else:
                self.add_op('SUB', a, b, t)
            self.pop(3)
            self.push(t)
        elif action == 'mult':
            a, b = self.stack[-2:]
            t = self.get_temp()
            self.add_op('SUB', a, b, t)
            self.pop(2)
            self.push(t)
        # elif action ==