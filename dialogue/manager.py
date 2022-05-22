import typing
from collections import deque

from .states import STATE_DEFAULTS, DialogueState

from intent import predict_intent

from ner import ner_spacy


class DialogueManager():
    """ Dialogue Manager that handles state"""

    def __init__(self):
        self.prior_states = deque()
        self.current_state = DialogueState(
            **STATE_DEFAULTS["init"])
        self.finalised_values = {
                                    "items": [],
                                    "address": None,
                                    "timeslot": None,
                                    "payment": None
                                }

    def run_state(self, input=None):
        """ Handle the running of a state"""
        if not self.current_state.confirm:
            current_intent, pass_entities = self.user_turn(input)

            # unless state already known
            if not self.current_state.name == self.current_state.lock_state:
                new_state = DialogueState(
                    **STATE_DEFAULTS[current_intent], 
                    entities = pass_entities)
                self.update_state(new_state)
            else:
                self.current_state.state_entities = pass_entities
                self.current_state.response_intent = current_intent
                self.current_state.lock_state = False
            
            # Change to add_to_basket
            # Do you want to add chicken to basket?
            return self.current_state.state_logic(self.current_state)

        else:
            """
            User: Yes/No
            select new state
            show state message 
            """

            current_intent, pass_entities = self.user_turn(input)

            confirm = False
            lock_state = False
            entities = {}

            if current_intent == "negative":
                next_state_name = self.current_state.name

            elif current_intent == "affirmative":
                next_state_name = self.current_state.default_next_state

            else: # Special case with known next state
                next_state_name = current_intent
                confirm = True
                lock_state = True
                entities = pass_entities
                print("odd case")

            new_state = DialogueState(
                **STATE_DEFAULTS[next_state_name],
                entities=entities,
            )
            new_state.confirm = confirm
            new_state.lock_state = lock_state
            new_state.entities = entities

            # returns state init_message
            self.update_state(new_state)
            return self.current_state.init_message


    def bot_turn(self, start):
        """ Run a bot turn"""

        return self.current_state.state_logic(self.current_state, start=start)


    def user_turn(self, message):
        """ Process a user turn"""

        for p in [",",".","-","?","!"]:
            message = message.replace(p, "")

        turn_intent = self.get_intent(message)
        turn_entities = self.get_entities(message)

        print(f'Message: {message}, Intent {turn_intent}, Entities {turn_entities}')

        self.current_state.state_entities.update(turn_entities)

        return turn_intent, turn_entities

    def get_intent(self, message):
        """ Get intent from an utterance"""

        return predict_intent(message)


    def get_entities(self, message):
        """ Get entities from an utterance"""

        ent_dict = {}
        for ent in ner_spacy(message).ents:
            ent_dict[ent.label_] = ent.text
        return ent_dict


    def update_state(self, new_state):
        """ Save the current dialogue state to history and enter a new state."""
        print(f'State {new_state.name}({new_state.uuid}), confirm={new_state.confirm}')

        self.prior_states.append(self.current_state)
        self.current_state = new_state