from state import State

states: dict[int, State] = {}


def add_nodes():
    for i in range(0, 21):
        states[i] = State()

    for i in [2, 3, 5, 7, 8, 10, 11, 12, 13, 16, 19, 20]:
        states[i].is_final = True

    for i in [2, 8, 11, 16]:
        states[i].go_back = True

    for i in [3, 10, 20]:
        states[i].has_error = True

    states[2].token_type = 'NUM'
    states[3].token_type = 'Invalid number'
    states[4].token_type = 'ID'
    for i in [7, 8, 11, 12]:
        states[i].token_type = 'SYMBOL'

    states[10].token_type = 'Unmatched comment'
    states[13].token_type = 'WHITESPACE'
    states[16].token_type = 'COMMENT'
    states[19].token_type = 'COMMENT'
    states[20].token_type = 'Unclosed comment'


def describe_dfa():
    add_nodes()
    #add_edges()


def add_edge(i, j, eval_func):
    states[i].add_transition(states[j], eval_func)




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
