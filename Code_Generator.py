from Parser import Parser


class SymbolTable:
    def __init__(self):
        self.table = []
        self.addr = 100

    def add_var(self, lexeme, type, scope):
        self.table.append({'lexeme': lexeme, 'type': type, 'scope': scope, 'kind': 'var', 'addr':self.addr})
        self.update_addr(type)

    def add_arr(self, lexeme, type, num, scope):
        self.table.append({'lexeme': lexeme, 'type': type + '*', 'num': num, 'scope': scope, 'kind': 'var', 'addr':self.addr})
        self.update_addr(type, int(num))

    def add_func(self, lexeme, type, scope):
        self.table.append({'lexeme': lexeme, 'type': type, 'scope': scope, 'kind': 'func', 'addr':self.addr})
        self.update_addr(type)

    def add_var_param(self, lexeme, type, scope):
        self.table.append({'lexeme': lexeme, 'type': type, 'scope': scope, 'kind': 'param', 'addr':self.addr})
        self.update_addr(type)

    def add_arr_param(self, lexeme, type, scope):
        self.table.append({'lexeme': lexeme, 'type': type + '*', 'scope': scope, 'kind': 'param', 'addr':self.addr})
        self.update_addr(type)

    def update_addr(self, type, num = 1):
        self.addr += 4 * num

    def get_index(self, id):
        for i in range(len(self.table) - 1, -1, -1):
            if self.table[i]['lexeme'] == id:
                return i

    def get_row(self, id):
        return self.table[self.get_index(id)]

class CodeGenerator:
    def __init__(self, parser):
        self.parser: Parser = parser
        self.table = SymbolTable()
        self.stack = []
        self.scope = 0
        self.i = 0
        self.arg_coutner = 0
        self.declare_func_name = None

    def push(self, val):
        self.stack.append(val)

    def pop(self, n=1):
        for i in range(n):
            self.stack.pop()

    def code_gen(self, action: str):
        if action == 'push':
            self.push(self.parser.look_ahead)
        elif action == 'var_declare':
            self.table.add_var(self.stack[-1], self.stack[-2], self.scope)
            self.pop(2)
        elif action == 'arr_declare':
            # todo: void error
            self.table.add_arr(self.stack[-2], self.stack[-3], self.stack[-1], self.scope)
            self.pop(3)
        elif action == 'scope+':
            self.scope += 1
        elif action == 'scope-':
            self.scope -= 1
        elif action == 'var_param':
            self.table.add_var_param(self.stack[-1], 'int', self.scope)
            self.arg_coutner += 1
            self.pop(1)
        elif action == 'arr_param':
            self.table.add_arr_param(self.stack[-1], 'int', self.scope)
            self.arg_coutner += 1
        elif action == 'func_declare':
            self.table.add_func(self.stack[-1], self.stack[-2], self.scope)
            self.declare_func_name = self.stack[-1]
            self.arg_coutner = 0
        elif action == 'process_func':
            func = self.table.get_row(self.declare_func_name)
            func['num'] = self.arg_coutner
            func['code_adrr'] = self.i
            self.arg_coutner = 0
