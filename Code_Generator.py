from typing import Any


class SymbolTable:
    def __init__(self):
        self.table = []
        self.return_addr = 3000
        self.addr = 500
        self.add_func('output', 'void', 0)
        self.add_var_param('a', 'int', 1)
        self.table[0]['num'] = 1
        self.table[0]['code_adrr'] = 2  # todo

    def __getitem__(self, item):
        return self.table[item]

    def add_var(self, lexeme, type, scope):
        self.table.append({'lexeme': lexeme, 'type': type, 'scope': scope, 'kind': 'var', 'addr': self.addr})
        self.update_addr(type)

    def add_arr(self, lexeme, type, num, scope):
        self.table.append({'lexeme': lexeme, 'type': type + '*', 'num': num, 'scope': scope, 'kind': 'var',
                           'addr': self.addr})
        self.update_addr(type, int(num) + 1)

    def add_func(self, lexeme, type, scope):
        self.table.append({'lexeme': lexeme, 'type': type, 'scope': scope, 'kind': 'func', 'addr': self.addr,
                           'return_addr': self.return_addr})
        self.return_addr += 4
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

    def get_row_by_addr(self, addr):
        one = True
        for i, row in zip(range(len(self.table) - 1, -1, -1), self.table[::-1]):
            if row['scope'] == 0:
                one = False
                if row['addr'] == addr:
                    return i, row
            elif one:
                if row['addr'] == addr:
                    return i, row


class CodeGenerator:
    def __init__(self):
        self.table = SymbolTable()
        self.stack = []
        self.pb = []
        self.scope = 0
        self.i = 0
        self.arg_counter = 0
        self.declare_func_row = None
        self.func_row = None
        self.func_i = None
        self.temp = 996
        self.repeat_stack = []
        self.add_op('')
        self.add_op('JP', self.i + 3)
        self.add_op('PRINT', 504)
        self.add_op('JP', f'@{self.table.table[0]["return_addr"]}')

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
        elif action == 'push_num':
            self.push(f'#{look_ahead}')
        elif action == 'pop':
            self.pop()
        elif action == 'var_declare':
            self.table.add_var(self.stack[-1], self.stack[-2], self.scope)
            self.pop(2)
        elif action == 'arr_declare':
            # todo: void error
            self.table.add_arr(self.stack[-2], self.stack[-3], self.stack[-1][1:], self.scope)
            arr_row = self.table.table[-1]
            self.add_op('ASSIGN', f'#{arr_row["addr"] + 4}', arr_row["addr"])
            self.pop(3)
        elif action == 'var_param':
            self.table.add_var_param(self.stack[-1], self.stack[-2], self.scope)
            self.arg_counter += 1
            self.pop(2)
        elif action == 'arr_param':
            self.table.add_arr_param(self.stack[-1], self.stack[-2], self.scope)
            self.arg_counter += 1
            self.pop(2)
        elif action == 'func_declare':
            self.table.add_func(self.stack[-1], self.stack[-2], self.scope)
            self.declare_func_row = self.table.table[-1]
            self.arg_counter = 0
            self.pop(2)
            self.scope += 1
            if self.declare_func_row['lexeme'] != 'main':
                self.push(self.i)
                self.add_op('')
        elif action == 'func_end':
            self.scope -= 1
            self.add_op('JP', f'@{self.declare_func_row["return_addr"]}')
            if self.declare_func_row['lexeme'] != 'main':
                self.add_op('JP', self.i, i=self.stack[-1])
                self.pop()
            self.declare_func_row = None
        elif action == 'process_func':
            self.declare_func_row['num'] = self.arg_counter
            self.declare_func_row['code_adrr'] = self.i
            # if self.declare_func_row['lexeme'] == 'main':
            #     self.add_op('JP', self.i, i=1)
            self.arg_counter = 0
        elif action == 'save':
            self.push(self.i)
            self.add_op("")
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
            self.add_op('')
        elif action == 'pid':
            _, row = self.table.get_row(look_ahead)
            self.push(row['addr'])
        elif action == 'assign':
            self.add_op('ASSIGN', self.stack[-1], self.stack[-2])
            self.pop(1) #todo
        elif action == 'get_arr':
            t = self.get_temp()
            self.add_op('MULT', self.stack[-1], '#4', t)
            self.pop()
            t2 = self.get_temp()
            self.add_op('ADD', t, self.stack[-1], t2)
            self.pop()
            self.push(f'@{t2}')
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
            self.add_op('MULT', a, b, t)
            self.pop(2)
            self.push(t)
        elif action == 'repeat':
            self.repeat_stack.append(self.get_temp())
            self.push(self.i)
            self.add_op('')
        elif action == 'until':
            t = self.repeat_stack.pop()
            j = self.stack[-2]
            self.add_op('JPF', self.stack[-1], j + 1)
            self.add_op('ASSIGN', f'#{self.i}', t, i=j)
            self.pop(2)
        elif action == 'break':
            if self.repeat_stack:
                t = self.repeat_stack[-1]
                self.add_op('JP', f'@{t}')
            else:
                pass
        #         todo: break error
        elif action == 'func_id':
            func_addr = self.stack[-1]
            self.func_i, self.func_row = self.table.get_row_by_addr(func_addr)
            self.pop()
        elif action == 'arg':
            # todo: type of arguments
            self.arg_counter += 1
            arg_addr = self.table.table[self.func_i + self.arg_counter]['addr']
            self.add_op('ASSIGN', self.stack[-1], arg_addr)
            self.pop()
        elif action == 'call':
            # todo: error: number of arguments
            self.arg_counter = 0
            self.add_op('ASSIGN', f'#{self.i + 2}', self.func_row['return_addr'])
            self.add_op('JP', self.func_row['code_adrr'])
            t = self.get_temp()
            if self.func_row['type'] != 'void':
                self.add_op('ASSIGN', self.func_row['addr'], t)
            self.push(t)
            self.func_i, self.func_row = None, None
        elif action == 'set_return_value':
            self.add_op('ASSIGN', self.stack[-1], self.declare_func_row['addr'])
            self.pop()
        elif action == 'return':
            self.add_op('JP', f'@{self.declare_func_row["return_addr"]}')
