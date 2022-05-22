# Logic for states
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dialogue.states import DialogueState
    from dialogue.manager import DialogueManager


def confirm_handler(self: "DialogueState", confirm_message="Please confirm the following"):
    """ Logic to handle confirmation"""
    missing_details = []
    for e in self.entity_mask:
        if e not in self.state_entities:
            missing_details.append(e)

    if missing_details:
        return_string = "You are missing the following:\n"
        for v in missing_details:
            return_string += f'  - {v.title()}\n'
        return_string += '\n Please try again with the correct options.'
        self.turn = "unknown"

    else:
        return_string = f"{confirm_message}:\n"
        for k, v in self.state_entities.items():
            return_string += f'  - For {k.title()} you entered: {v}\n'
        return_string += '\nYou can say "Yes" or "No" to confirm.'

    return return_string


def init_logic(self: "DialogueState"):
    if self.turn == "confirm":
        return "Confirm but this still shouldnt happen"

    return "Please be clearer with your request"


def check_availability_logic(self: "DialogueState"):
    """Logic for the check availability state"""
    return 'OPTIONS'


def add_to_basket_logic(self: "DialogueState"):
    """Logic for the add to basket state"""
    search_query = self.state_entities['PRODUCT']
    return 'OPTIONS'


def remove_from_basket_logic(self: "DialogueState"):
    """Logic for the remove from basket state"""

    def confirmed_callback(manager: "DialogueManager"):
        search_query = self.state_entities['PRODUCT']
        # TODO: Actually remove the correct item or decrement, make sure it exists
        manager.finalised_values['items'].remove(0)

    if self.turn == "confirm":
        

        return confirm_handler(self, "Please confirm removing the following from the basket")
    elif self.turn == "confirmed":
        return confirmed_callback
    else:
        return f"{self.name}, {self.turn}"


def address_details_logic(self: "DialogueState"):
    """Logic for the address details state"""

    def confirmed_callback(manager: "DialogueManager"):
        manager.finalised_values['address'] = {
            'STREET': self.state_entities['STREET'],
            'CITY': self.state_entities['CITY'],
            'STREET': self.state_entities['POSTCODE'],
        }

    if self.turn == "confirm":
        return confirm_handler(self)
    elif self.turn == "confirmed":
        return confirmed_callback
    else:
        return f"{self.name}, {self.turn}"


def timeslot_details_logic(self: "DialogueState"):
    """Logic for the timeslot request state"""

    def confirmed_callback(manager: "DialogueManager"):
        manager.finalised_values['timeslot'] = self.state_entities['TIME']

    if self.turn == "confirm":
        return confirm_handler(self)
    elif self.turn == "confirmed":
        return confirmed_callback
    else:
        return f"{self.name}, {self.turn}"


def payment_details_logic(self: "DialogueState"):
    """Logic for the payment details state"""

    def confirmed_callback(manager: "DialogueManager"):
        manager.finalised_values['payment'] = {
            'NAME': self.state_entities['NAME'],
            # TODO: Assumes they exist
            'CARD_NUMBER': self.state_entities['CARD_NUMBER'],
            'CARD_CVC': self.state_entities['CARD_CVC'],
            'CARD_EXPIRY': self.state_entities['CARD_EXPIRY'],
        }

    if self.turn == "confirm":
        return confirm_handler(self)
    elif self.turn == "confirmed":
        return confirmed_callback
    else:
        return f"{self.name}, {self.turn}"


def confirm_order_logic(self: "DialogueState"):
    """Logic for the confirm order state"""
    if self.turn == "confirm":
        return "custom confirm"
    else:
        return f"{self.name}, {self.turn}"


def exit_logic(self: "DialogueState"):
    """Logic for the exit state"""

    if self.turn == "confirm":
        return confirm_handler(self)
    else:
        return f"{self.name}, {self.turn}"
