import numpy as np
from utils import create_shoe, hand_values, best_value, Action

class Dealer:
    """
    Dealer of the house - handles the shoe, the remaining cards
    """
    def __init__(self, shoe_length=8):
        self.shoe           = create_shoe(shoe_length)
        self.hand           = self.deal_cards(2)  # populated each round: [(cards, bet, is_doubled)]
        
    def deal_cards(self, n):
        hand = []
        for _ in range(n):
            card = self.shoe.pop()
            hand.append(card)
        return hand
    
    def take_actions(self):
        # Calculate the possible hand values
        vals = hand_values(self.hand)
        best = best_value(self.hand)
        
        # If the dealer has a soft total (an Ace valued as 11) and the hand value is 17, they will hit
        if best == 17:
            # Check if the dealer has a soft 17 (Ace + 6) and needs to hit
            if len(vals) >= 2:      # TODO Implement stand 17 games
                print(f"Dealer's soft 17: {self.hand}, hitting.")
                return  Action.HIT # After hitting, we return to recheck the hand
            else:
                print(f"Dealer stands with {self.hand}")
                return  Action.STAND # Stand

        # Dealer hits if the best value is less than 17
        if best < 17:
            print(f"Dealer's hand value: {best}, hitting.")
            return  Action.HIT

        # Dealer stands if the best value is 17 or more
        print(f"Dealer's hand value: {best}, standing.")
        return  Action.STAND

    def new_round(self):
        self.hand.clear()
        
    def clear_shoe(self):
        self.shoe.clear()