from DFA import DFA


class Scanner:

    def __init__(self, input_file):
        self.keywords = ['if', 'else', 'void', 'int', 'repeat', 'break', 'until', 'return', 'endif']
        self.symbol_table = list(self.keywords)
        self.dfa = DFA()
        self.buffer = list()
        self.input_file = input_file
        self.errors_file = open('lexical_errors.txt', 'w')
        self.file_ended = False
        self.lexical_error_find = False
        self.last_error_line = 0
        self.pointer_last_position = input_file.tell()
        self.line_number = 1

    def get_next_token(self):
        status: str = None
        message: str = None

        if self.file_ended:
            return None, None

        while status is None:
            self.pointer_last_position = self.input_file.tell()
            input_char = self.input_file.read(1)
            self.buffer.append(input_char)

            # Condition for EOF
            if input_char == '':
                self.file_ended = True

            status, message = self.dfa.do_transition(input_char)

        if 'GO_BACK' in status:
            self.buffer.pop()
            self.input_file.seek(self.pointer_last_position)

        if status.startswith('ERROR'):

            error_string = "".join(self.buffer)
            if message == 'Unclosed comment':
                error_string = error_string[0:7] + '...'
            if not self.lexical_error_find:
                self.lexical_error_find = True
                self.errors_file.write(f'{self.line_number}.\t')
            elif self.line_number != self.last_error_line:
                self.errors_file.write(f'\n{self.line_number}.\t')
            self.last_error_line = self.line_number
            self.errors_file.write(f'({error_string}, {message}) ')
            self.buffer.clear()
            self.line_number += error_string.count('\n')
            return self.get_next_token()

        elif status.startswith('TOKEN'):

            if message == 'EOF':
                return None, None

            # Handle * in DFA
           # if 'GO_BACK' in status:
            #    self.buffer.pop()
             #   self.input_file.seek(self.pointer_last_position)

            token_string = "".join(self.buffer)
            self.buffer.clear()

            self.line_number = self.line_number + token_string.count('\n')

            # Handle ID , Keyword add new ID to symbol table
            if message == 'ID':
                if token_string in self.keywords:
                    message = 'KEYWORD'
                if token_string not in self.symbol_table:
                    self.symbol_table.append(token_string)

            return [message, token_string]

    def close_files(self):
        if not self.lexical_error_find:
            self.errors_file.write('There is no lexical error.')
        self.errors_file.close()
    #    with open('symbol_table.txt', 'w') as file:
    #        for i, id in enumerate(self.symbol_table):
    #            file.write(f'{i + 1}.\t{id}\n')
