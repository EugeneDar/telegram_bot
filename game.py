from enum import Enum
import random


class State(Enum):
    BET_ENTERING = 0
    PLAYING = 1
    NOTHING = 2


class Game:
    def __init__(self):
        self.state = State.NOTHING
        self.bet = 0

        self.deck = Game.generate_deck()
        self.user_cards = list()
        self.dealer_cards = list()

        self.user_cards.append(self.deck.pop(0))
        self.user_cards.append(self.deck.pop(0))

        self.dealer_cards.append(self.deck.pop(0))
        self.dealer_cards.append(self.deck.pop(0))

    @staticmethod
    def generate_deck():
        deck = list()
        for sigh in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']:
            for color in ['♠', '♥', '♣', '♦']:
                deck.append(sigh + color)
        random.shuffle(deck)
        return deck

    @staticmethod
    def cards_to_string(cards):
        text = ''
        for card in cards:
            text += card + ' '
        return text

    @staticmethod
    def evaluate_hand(cards):
        score = 0
        aces = 0

        for card in cards:
            if '2' <= card[0] <= '9':
                score += int(card[0])
            elif card[0] == 'A':
                score += 1
                aces += 1
            else:
                score += 10

        while score + 10 <= 21 and aces > 0:
            score += 10
            aces -= 1

        return score
