from DFA import DFA


class Scanner:

    def __init__(self, input_file):
        self.keywords = ['if', 'else', 'void', 'int', 'repeat', 'break', 'until', 'return']
        self.symbol_table = list(self.keywords)
        self.dfa = DFA()
        self.buffer = list()
        self.input_file = input_file
        self.errors_file = open('lexical_errors.txt', 'w')
        self.file_ended = False
        self.line_number = 1

    def get_next_token(self):
        status: str = None
        message: str = None

        if self.file_ended:
            return None, None

        while status is None:
            input_char = self.input_file.read(1)
            self.buffer.append(input_char)

            # Condition for EOF
            if input_char == '':
                input_char = 'EOF'
                self.file_ended = True

            status, message = self.dfa.do_transition(input_char)
        if status.startswith('ERROR'):
            self.errors_file.write(f'{self.line_number} ({"".join(self.buffer)}, {message})\n')
            self.buffer.clear()
            return self.get_next_token()

        elif status.startswith('TOKEN'):

            token_string = "".join(self.buffer)

            # Handle ID , Keyword add new ID to symbol table
            if message == 'ID':
                if token_string in self.keywords:
                    message = 'KEYWORD'
                if token_string not in self.symbol_table:
                    self.symbol_table.append(token_string)

            # Handle * in DFA
            if 'GO_BACK' in status:
                token_string = token_string[0:-1]
                del self.buffer[0:-1]
            else:
                self.buffer.clear()
            return [message, token_string]

    def close_files(self):
        self.errors_file.close()

