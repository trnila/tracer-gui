from tracergui import maps
from tracergui.actions.Action import Action


class Signal(Action):
    def __init__(self, sender_pid, receiver_pid, signal, system):
        super().__init__(system)
        self.signal = signal
        self.sender_pid = sender_pid
        self.receiver_pid = receiver_pid

    def apply_filter(self, query):
        return True

    def generate(self, dot_writer):
        dot_writer.write_edge(self.sender_pid, self.receiver_pid, label=maps.signals[self.signal])
