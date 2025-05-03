import numpy as np
from utils import create_shoe, hand_values, best_value, Action

class Dealer:
    """
    Dealer of the house - handles the shoe, the remaining cards
    """
    
    #This should be called once ever 
    def __init__(self, num_decks_in_shoe=8, decks_to_cut=1, printout=False):
        #need to know so we can make new shoes
        self.num_decks_in_shoe = num_decks_in_shoe 
        #the dealer needs to know when to stop dealing the shoe
        self.decks_to_cut = decks_to_cut
        self.decks_remaining = num_decks_in_shoe
        self.shoe = []
        self.hand = []
        self.printout = printout
        
        
    #This shold be to only way the shoe gives out cards
    def deal_cards(self, n):
        hand = []
        for _ in range(n):
            card = self.shoe.pop()
            hand.append(card)
        
        # round to the nearest half
        # TODO check if we want to round down always???
        self.decks_remaining = round(len(self.shoe) / 52 * 2) / 2

        #let the table know that the shoe is over after this round
        if len(self.shoe) < self.decks_to_cut * 52:
            self.cut_card_out = True
        
        return hand
    
    #to give the dealer their own cards
    def take_cards(self, cards):
        self.hand.extend(cards)
    
    #logic to tell the dealer to draw or stand their own hand
    def take_actions(self):
        # Calculate the possible hand values
        vals = hand_values(self.hand)
        best = best_value(self.hand)
        
        # If the dealer has a soft total (an Ace valued as 11) and the hand value is 17, they will hit
        if best == 17:
            # Check if the dealer has a soft 17 (Ace + 6) and needs to hit
            if len(vals) >= 2:      # TODO Implement stand 17 games
                if self.printout:
                    print(f"Dealer's soft 17: {self.hand}, hitting.")
                
                return  Action.HIT # After hitting, we return to recheck the hand
            else:
                if self.printout:
                    print(f"Dealer stands with {self.hand}")
                
                return  Action.STAND # Stand

        # Dealer hits if the best value is less than 17
        if best < 17:
            if self.printout:
                print(f"Dealer's hand value: {best}, hitting.")
            
            return  Action.HIT

        # Dealer stands if the best value is 17 or more
        if self.printout:
            print(f"Dealer's hand value: {best}, standing.")
        return  Action.STAND

    def new_round(self):
        self.hand.clear()
        
    def new_shoe(self):
        self.shoe = create_shoe(self.num_decks_in_shoe)
        self.cut_card_out = False
        
    def clear_shoe(self):
        self.shoe.clear()