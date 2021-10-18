from state import State


class DFA:
    def __init__(self):
        self.states: list[State] = []
        self.describe_dfa()
        self.current_state = self.states[0]

    @property
    def start_state(self):
        return self.states[0]

    def transition(self, input_char: str):
        self.current_state = self.current_state.get_next_state(input_char)
        return self.current_state

    def add_nodes(self):
        for i in range(0, 21):
            self.states.append(State())

        for i in [2, 3, 5, 7, 8, 10, 11, 12, 13, 16, 19, 20]:
            self.states[i].is_final = True

        for i in [2, 8, 11, 16]:
            self.states[i].go_back = True

        for i in [3, 10, 20]:
            self.states[i].has_error = True

        self.states[2].token_type = 'NUM'
        self.states[3].token_type = 'Invalid number'
        self.states[4].token_type = 'ID'
        for i in [7, 8, 11, 12]:
            self.states[i].token_type = 'SYMBOL'

        self.states[10].token_type = 'Unmatched comment'
        self.states[13].token_type = 'WHITESPACE'
        self.states[16].token_type = 'COMMENT'
        self.states[19].token_type = 'COMMENT'
        self.states[20].token_type = 'Unclosed comment'

    def describe_dfa(self):
        self.add_nodes()
        self.add_edges()

    def add_edge(self, i, j, eval_func):
        self.states[i].add_transition(self.states[j], eval_func)

    def add_edges(self):
        self.add_edge(0, 1, digit)
        self.add_edge(1, 1, digit)
        # other for NUM:
        self.add_edge(1, 2, lambda x: symbol(x) or whitespace(x) or slash(x))
        # other than other (errors) for NUM:
        self.add_edge(1, 3, lambda x: True)  # todo: check if this works fine

        self.add_edge(0, 4, letter)
        self.add_edge(4, 4, letter)
        # other for ID:
        self.add_edge(4, 5, lambda x: symbol(x) or whitespace(x) or slash(x))

        self.add_edge(0, 6, lambda x: x == '=')
        self.add_edge(0, 7, lambda x: x == '=')
        # other for =
        self.add_edge(6, 8, lambda x: letter(x) or digit(x) or whitespace(x) or slash(x) or (symbol(x) and x != '='))
        # todo: symbol?

        self.add_edge(0, 9, lambda x: x == '*')
        self.add_edge(9, 10, lambda x: x == '/')
        # other for *
        self.add_edge(9, 11, lambda x: True)  # todo check if this works fine

        self.add_edge(0, 12, lambda x: symbol(x) and x != '=' and x != '*')

        self.add_edge(0, 13, whitespace)

        self.add_edge(0, 14, slash)
        self.add_edge(14, 15, slash)
        self.add_edge(15, 16, lambda x: x == '\n' or x == 'EOF')  # todo: EOF
        self.add_edge(14, 17, lambda x: x == '*')
        self.add_edge(17, 18, lambda x: x == '*')
        self.add_edge(17, 20, lambda x: x == 'EOF')
        self.add_edge(18, 20, lambda x: x == 'EOF')
        self.add_edge(17, 17, lambda x: x != '*' and x != 'EOF')
        self.add_edge(18, 19, slash)
        self.add_edge(18, 17, lambda x: x != '*' and x != '/' and x != 'EOF')


def digit(x: str):
    return x.isdigit()


def letter(x: str):
    return x.isalpha()


def slash(x: str):
    return x == '/'


def whitespace(x: str):
    return x in [' ', '\n', '\r', '\t', '\v', '\f']
    # or maybe x.space?


def symbol(x: str):
    return x in [';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '<']
