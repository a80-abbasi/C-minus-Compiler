class State:

    def __init__(self, neighbors: dict = None, is_final=False, token_type: str = None, other: list = None):
        self.neighbors = neighbors
        self.is_final = is_final
        self.token_type = token_type
        self.other = other if other else []

    def add_transition(self, next_state, input_char: str):
        if input_char not in self.neighbors:
            self.neighbors[input_char] = next_state

    def get_next_state(self, input_char: str):
        if input_char.isdigit():
            input_char = 'digit'
        elif input_char.isalpha():
            input_char = 'letter'
        elif input_char in self.other:
            input_char = 'other'

        return self.neighbors[input_char]
