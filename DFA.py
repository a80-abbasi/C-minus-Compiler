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
    add_edges()


def add_edge(i, j, eval_func):
    states[i].add_transition(states[j], eval_func)


def add_edges():
    add_edge(0, 1, digit)
    add_edge(1, 1, digit)
    # other for NUM:
    add_edge(1, 2, lambda x: symbol(x) or whitespace(x) or slash(x))
    # other than other (errors) for NUM:
    add_edge(1, 3, lambda x: True)  # todo: check if this works fine

    add_edge(0, 4, letter)
    add_edge(4, 4, letter)
    # other for ID:
    add_edge(4, 5, lambda x: symbol(x) or whitespace(x) or slash(x))

    add_edge(0, 6, lambda x: x == '=')
    add_edge(0, 7, lambda x: x == '=')
    # other for =
    add_edge(6, 8, lambda x: letter(x) or digit(x) or whitespace(x) or slash(x) or (symbol(x) and x != '='))
    # todo: symbol?

    add_edge(0, 9, lambda x: x == '*')
    add_edge(9, 10, lambda x: x == '/')
    # other for *
    add_edge(9, 11, lambda x: True)  # todo

    add_edge(0, 12, lambda x: symbol(x) and x != '=' and x != '*')

    add_edge(0, 13, whitespace)

    add_edge(0, 14, slash)
    add_edge(14, 15, slash)
    add_edge(15, 16, lambda x: x == '\n' or x == 'EOF')  # todo: EOF
    add_edge(14, 17, lambda x: x == '*')
    add_edge(17, 18, lambda x: x == '*')
    add_edge(17, 20, lambda x: x == 'EOF')
    add_edge(18, 20, lambda x: x == 'EOF')
    add_edge(17, 17, lambda x: x != '*' and x != 'EOF')
    add_edge(18, 19, slash)
    add_edge(18, 17, lambda x: x != '*' and x != '/' and x != 'EOF')


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
