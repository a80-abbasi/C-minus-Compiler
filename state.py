class State:

    def __init__(self, name: int, is_final: bool = False, go_back: bool = False, has_error: bool = False, token_type: str = None):
        self.name = name
        self.neighbors: dict = {}
        self.is_final = is_final
        self.go_back = go_back
        self.has_error = has_error
        self.token_type = token_type

    def add_transition(self, next_state, eval_func):
        if eval_func not in self.neighbors:
            self.neighbors[eval_func] = next_state

    def get_next_state(self, input_char: str):
        for eval_func, state in self.neighbors.items():
            if eval_func(input_char):
                return state

        raise ValueError('invalid input')
