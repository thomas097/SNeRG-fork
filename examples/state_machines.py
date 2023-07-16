import json
from pprint import pformat
from typing import Hashable


class FiniteStateMachine:
    def __init__(self, start_state: Hashable = "start", path: str = None) -> None:
        """FSM constructor. If a path to a configuration file is provided,
        the FSM is loaded from file; otherwise, a blank FSM is created.

        Args:
            start_state (Hashable, optional): State at which traversal starts. Defaults to "start".
            path (str, optional): Path to configuration file describing FSM. Defaults to None.
        """
        # Load FSM from file if path provided.
        if path is not None:
            self._start_state, self._state_dict, self._global_transitions = self.__load_state_dict(path)
        else:
            self._start_state = start_state
            self._state_dict = {self._start_state: []} # Start state with no transitions
            self._global_transitions = []

        self._current_state = self._start_state

    def __str__(self) -> str:
        return pformat(self._state_dict)

    def __eval(self, condition: str, memory: dict) -> bool:
        """Evaluates a Boolean condition using variable:value pairs in memory. If a
        variable in the condition is not stored in memory, __eval() evaluates to False.

        Args:
            condition (str): A Python-syntax Boolean condition with optional variables.
            memory (dict): Mapping from variable names to values.

        Returns:
            bool: True when the condition is met; False otherwise.
        """
        try:
            return eval(condition, {}, memory)
        except NameError:
            return False
        
    def __load_state_dict(self, path: str) -> None:
        """Loads state dict from JSON-encoded file.

        Args:
            path (str): Path to previously saved state dict.
        """
        with open(path, 'r', encoding='utf-8') as infile:
            return json.load(fp=infile)
        
    def save_state_dict(self, path: str, indent: int = 4) -> None:
        """Saves state dict to JSON-encoded file.

        Args:
            path (str): Desired path to state dict file.
            indent (int): Number of spaces to use for indentation.
        """
        data = [self._start_state, self._state_dict, self._global_transitions]
        with open(path, 'w', encoding='utf-8') as outfile:
            json.dump(data, fp=outfile, indent=indent)


    def add_transition(self, src: Hashable, dst: Hashable, condition: str = "True") -> None:
        """Adds a new state transition from state designated by `src` to state designated by `dst`.
        If `src = None`, the source state is considered a wildcard, thus any state can transition 
        to the `dst` state upon satisfying the condition (local transitions do take priority).

        Args:
            src (Hashable): Identifier of source, or starting, state.
            dst (Hashable): Identifier of destination state.
            condition (str, optional): Condition which triggers state transition. Defaults to "True".
        """
        if src not in self._state_dict and src is not None:
            self._state_dict[src] = []
            
        if dst not in self._state_dict:
            self._state_dict[dst] = []

        # If frm == None, allow any state to transition to state designated by `dst` (i.e. global transition)
        if src is None:
            self._global_transitions.append((dst, condition))
            return

        self._state_dict[src].append((dst, condition))

    def tick(self, memory: dict) -> Hashable:
        """Returns the next state given current state of FSM and variables in memory.

        Args:
            memory (dict): Memory buffer with variable:values pairs.

        Returns:
            Hashable: Identifier of current state.
        """
        for next_state, condition in self._state_dict[self._current_state] + self._global_transitions:
            if self.__eval(condition, memory=memory):
                self._current_state = next_state
                break

        return self._current_state



if __name__ == '__main__':
    memory = {
        'power': 'on',
        'battery_level': .95,
        'altitude': 0.0,
        'in_flight': False
    }

    fsm = FiniteStateMachine(start_state="waiting")

    # Local transitions
    fsm.add_transition(src="waiting", dst="systems_active", condition="power == 'on' and battery_level >= .9")
    fsm.add_transition(src="systems_active", dst="take-off")
    fsm.add_transition(src="take-off", dst="at_altitude", condition="altitude > 1.0")

    # Global transition
    fsm.add_transition(src=None, dst="goto_gcs", condition="in_flight and battery_level < .2")
    
    print(fsm.tick(memory))
    print(fsm.tick(memory))
    print(fsm.tick(memory))