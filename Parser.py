# A:  0---B--->1
# 0 and 1: State
# B: NTT (NonTerminal or Terminal! change it if you want)

class TransitionDiagram:
    def __init__(self):
        start_symbol = self.create_transition_diagram()
        self.state = start_symbol

    def create_transition_diagram(self):  # todo
        return None

    # def do_transition(self, look_ahead):
    #     for ntt, neighbor in self.state.neighbors.items():
    #         if self.should_do_with_first(self, ntt, look_ahead)
    #             self.state = neighbor
    #             return
    #     if
    #
    # def should_do_with_first(self, cur_state, ntt, look_ahead):
    #     if look_ahead in ntt.first:
    #         return True
    #     if 'epsilon' in ntt.first:  # todo: epsilon
    #         for t, neigh in cur_state.neighbors[ntt].items():
    #             if self.should_do_with_first(cur_state.neighbors[ntt], t, look_ahead):
    #                 return True
    #     return False


class State:
    def __init__(self, number, is_final=False, neighbors=None):
        self.number = number
        self.is_final = is_final
        self.neighbors = neighbors

    def add_neighbor(self, neighbor, input):  # input is an NTT
        self.neighbors = input, neighbor


class StartState(State):

    def __init__(self, number, start_terminal, is_final=False, neighbors=None):
        super().__init__(number, is_final, neighbors)
        self.start_terminal = start_terminal
        self.neighbors = neighbors if neighbors is not None else []

    def add_neighbor(self, neighbor, input):
        self.neighbors.append((input, neighbor))


class NTT:
    count = 0

    def __init__(self, first, follow=None, is_terminal=False, name=None, number=count):
        self.first = first
        self.follow = follow if follow is not None else []
        self.is_terminal = is_terminal
        self.name = name
        self.number = number
        NTT.count += 1

    def set_first(self, first):
        self.first = first

    def set_follow(self, follow):
        self.follow = follow
