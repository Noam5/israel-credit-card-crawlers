from abc import ABC, abstractmethod

class Transaction:
    pass

class CreditCard:
    def __init__(self, card_id, last4digits, innerdata):
        self.card_id = card_id
        self.last4digits = last4digits
        self.innerdata = innerdata # Data that is specific for each company

class CardProvider(ABC):
    @abstractmethod
    def login(self, username, password, cardsixdigits=None):
        pass

    @abstractmethod
    def get_credit_cards(self):
        pass

    @abstractmethod
    def get_card_transactions(self, card_id, month, year):
        pass
