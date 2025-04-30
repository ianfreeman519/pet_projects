import numpy as np
import random
from enum import Enum, auto

# Dictionary tables: hard_totals[(3, 7)] returns string action for what a player 3 should do against a dealer 7

# "hit" is a hit
# "sta" is a stand
# "dou" is a double, otherwise hit
# "dst" is a double, otherwise stand
# "yes" is a split
# "nos" is NOT a split, and should be routed to the hard totals table
# The last "response" is "bus" but isn't present here, because that response is handled in the main simulation loop

hard_totals = {
(21,2):'sta',       (21,3):'sta',       (21,4):'sta',       (21,5):'sta', (21,6):'sta',         (21,7): 'sta',      (21,8): 'sta', (21,9): 'sta',       (21,10): 'sta',         (21,11): 'sta',
(20,2):'sta',       (20,3):'sta',       (20,4):'sta',       (20,5):'sta', (20,6):'sta',         (20,7): 'sta',      (20,8): 'sta', (20,9): 'sta',       (20,10): 'sta',         (20,11): 'sta',
(19,2):'sta',       (19,3):'sta',       (19,4):'sta',       (19,5):'sta', (19,6):'sta',         (19,7): 'sta',      (19,8): 'sta', (19,9): 'sta',       (19,10): 'sta',         (19,11): 'sta',
(18,2):'sta',       (18,3):'sta',       (18,4):'sta',       (18,5):'sta', (18,6):'sta',         (18,7): 'sta',      (18,8): 'sta', (18,9): 'sta',       (18,10): 'sta',         (18,11): 'sta',
(17,2):'sta',       (17,3):'sta',       (17,4):'sta',       (17,5):'sta', (17,6):'sta',         (17,7): 'sta',      (17,8): 'sta', (17,9): 'sta',       (17,10): 'sta',         (17,11): 'sta',
(16,2):'sta',       (16,3):'sta',       (16,4):'sta',       (16,5):'sta', (16,6):'sta',         (16,7): 'hit',      (16,8): 'hit', (16,9): 'hit>+4sta', (16,10): 'hit>+0sta',   (16,11): 'hit>+3sta',
(15,2):'sta',       (15,3):'sta',       (15,4):'sta',       (15,5):'sta', (15,6):'sta',         (15,7): 'hit',      (15,8): 'hit', (15,9): 'hit',       (15,10): 'hit>+4sta',   (15,11): 'hit>+5sta',
(14,2):'sta',       (14,3):'sta',       (14,4):'sta',       (14,5):'sta', (14,6):'sta',         (14,7): 'hit',      (14,8): 'hit', (14,9): 'hit',       (14,10): 'hit',         (14,11): 'hit',
(13,2):'sta<-1hit', (13,3):'sta',       (13,4):'sta',       (13,5):'sta', (13,6):'sta',         (13,7): 'hit',      (13,8): 'hit', (13,9): 'hit',       (13,10): 'hit',         (13,11): 'hit',
(12,2):'hit>+3sta', (12,3):'hit>+2sta', (12,4):'sta<+0hit', (12,5):'sta', (12,6):'sta',         (12,7): 'hit',      (12,8): 'hit', (12,9): 'hit',       (12,10): 'hit',         (12,11): 'hit',
(11,2):'dou',       (11,3):'dou',       (11,4):'dou',       (11,5):'dou', (11,6):'dou',         (11,7): 'dou',      (11,8): 'dou', (11,9): 'dou',       (11,10): 'dou',         (11,11): 'dou',
(10,2):'dou',       (10,3):'dou',       (10,4):'dou',       (10,5):'dou', (10,6):'dou',         (10,7): 'dou',      (10,8): 'dou', (10,9): 'dou',       (10,10): 'hit>+4dou',   (10,11): 'hit>+3dou',
(9,2): 'hit>+1dou', (9,3): 'dou',       (9,4): 'dou',       (9,5): 'dou', (9,6): 'dou',         (9,7):  'hit>+3dou',(9,8):  'hit', (9,9):  'hit',       (9,10):  'hit',         (9,11):  'hit',
(8,2): 'hit',       (8,3): 'hit',       (8,4): 'hit',       (8,5): 'hit', (8,6): 'hit>+2dou',   (8,7):  'hit',      (8,8):  'hit', (8,9):  'hit',       (8,10):  'hit',         (8,11):  'hit',

(7,2): 'hit', (7,3): 'hit', (7,4): 'hit', (7,5): 'hit', (7,6): 'hit', (7,7):  'hit', (7,8):  'hit', (7,9):  'hit', (7,10):  'hit', (7,11):  'hit',
(6,2): 'hit', (6,3): 'hit', (6,4): 'hit', (6,5): 'hit', (6,6): 'hit', (6,7):  'hit', (6,8):  'hit', (6,9):  'hit', (6,10):  'hit', (6,11):  'hit',
(5,2): 'hit', (5,3): 'hit', (5,4): 'hit', (5,5): 'hit', (5,6): 'hit', (5,7):  'hit', (5,8):  'hit', (5,9):  'hit', (5,10):  'hit', (5,11):  'hit',
(4,2): 'hit', (4,3): 'hit', (4,4): 'hit', (4,5): 'hit', (4,6): 'hit', (4,7):  'hit', (4,8):  'hit', (4,9):  'hit', (4,10):  'hit', (4,11):  'hit',
(3,2): 'hit', (3,3): 'hit', (3,4): 'hit', (3,5): 'hit', (3,6): 'hit', (3,7):  'hit', (3,8):  'hit', (3,9):  'hit', (3,10):  'hit', (3,11):  'hit'
}

soft_totals = {
(3,2):'hit',        (3,3):'hit', (3,4):'hit',       (3,5):'dou',        (3,6):'dou',        (3,7): 'hit', (3,8): 'hit', (3,9): 'hit', (3,10): 'hit', (3,11): 'hit',
(4,2):'hit',        (4,3):'hit', (4,4):'hit',       (4,5):'dou',        (4,6):'dou',        (4,7): 'hit', (4,8): 'hit', (4,9): 'hit', (4,10): 'hit', (4,11): 'hit',
(5,2):'hit',        (5,3):'hit', (5,4):'dou',       (5,5):'dou',        (5,6):'dou',        (5,7): 'hit', (5,8): 'hit', (5,9): 'hit', (5,10): 'hit', (5,11): 'hit',
(6,2):'hit',        (6,3):'hit', (6,4):'dou',       (6,5):'dou',        (6,6):'dou',        (6,7): 'hit', (6,8): 'hit', (6,9): 'hit', (6,10): 'hit', (6,11): 'hit',
(7,2):'hit>+1dou',  (7,3):'dou', (7,4):'dou',       (7,5):'dou',        (7,6):'dou',        (7,7): 'hit', (7,8): 'hit', (7,9): 'hit', (7,10): 'hit', (7,11): 'hit',
(8,2):'dst',        (8,3):'dst', (8,4):'dst',       (8,5):'dst',        (8,6):'dst',        (8,7): 'sta', (8,8): 'sta', (8,9): 'hit', (8,10): 'hit', (8,11): 'hit',
(9,2):'sta',        (9,3):'sta', (9,4):'sta>+3dst', (9,5):'sta>+1dst',  (9,6):'dst<+0dst',  (9,7): 'sta', (9,8): 'sta', (9,9): 'sta', (9,10): 'sta', (9,11): 'sta',
(10,2):'sta',       (10,3):'sta', (10,4):'sta',     (10,5):'sta',       (10,6):'sta',       (10,7):'sta', (10,8):'sta', (10,9):'sta', (10,10):'sta', (10,11):'sta', 
(11,2):'sta',       (11,3):'sta', (11,4):'sta',     (11,5):'sta',       (11,6):'sta',       (11,7):'sta', (11,8):'sta', (11,9):'sta', (11,10):'sta', (11,11):'sta'
}

split_totals = {
(4,2):  "yes", (4,3): "yes", (4,4):  "yes",         (4,5): "yes",       (4,6): "yes",       (4,7): "yes", (4,8): "nos", (4,9): "nos", (4,10): "nos", (4, 11): "nos",
(6,2):  "yes", (6,3): "yes", (6,4):  "yes",         (6,5): "yes",       (6,6): "yes",       (6,7): "yes", (6,8): "nos", (6,9): "nos", (6,10): "nos", (6, 11): "nos", 
(8,2):  "nos", (8,3):  "nos", (8,4): "nos",         (8,5): "yes",       (8,6): "yes",       (8,7): "nos", (8,8): "nos", (8,9): "nos", (8,10): "nos", (8, 11): "nos",
(10,2): "nos", (10,3): "nos", (10,4):"nos",         (10,5):"nos",       (10,6):"nos",       (10,7):"nos", (10,8):"nos", (10,9):"nos", (10,10):"nos", (10, 11): "nos",
(12,2): "yes", (12,3): "yes", (12,4):"yes",         (12,5): "yes",      (12,6):"yes",       (12,7):"nos", (12,8):"nos", (12,9):"nos", (12,10):"nos", (12, 11): "nos",
(14,2): "yes", (14,3): "yes", (14,4):"yes",         (14,5): "yes",      (14,6): "yes",      (14,7):"yes", (14,8):"nos", (14,9):"nos", (14,10):"nos", (14, 11): "nos",
(16,2): "yes", (16,3): "yes", (16,4):"yes",         (16,5): "yes",      (16,6): "yes",      (16,7):"yes", (16,8):"yes", (16,9):"yes", (16,10):"yes", (16, 11): "yes", 
(18,2): "yes", (18,3): "yes", (18,4):"yes",         (18,5): "yes",      (18,6): "yes",      (18,7):"nos", (18,8):"yes", (18,9):"yes", (18,10):"nos", (18, 11): "nos",
(20,2): "nos", (20,3): "nos", (20,4):"nos>+6yes",   (20,5): "nos>+5yes",(20,6): "nos>+4yes",(20,7):"nos", (20,8):"nos", (20,9):"nos", (20,10):"nos", (20, 11): "nos",
(2,2):  "yes", (2,3): "yes", (2,4):  "yes",         (2,5): "yes",       (2,6): "yes",       (2,7): "yes", (2,8): "yes", (2,9): "yes", (2,10): "yes", (2, 11): "yes"
}

# Basic classes to handle enumerating game states and actions, for readability
class Action(Enum):
    HIT      = auto()
    STAND    = auto()
    DOUBLE   = auto()
    SPLIT    = auto()
    INSURE   = auto()   # “take insurance” –  handled once, not per‑card

class Outcome(Enum):
    WIN = auto()
    PUSH = auto()
    LOSE = auto()
    BJ = auto()       # natural 3:2

# Deck creator (should only be used within create_shoe() defined below)
def create_deck(seed=None):
    """
    Create and shuffle a standard deck of 52 cards.
    Each card is represented as a tuple (rank).
    Ranks: A, 2-10, J, Q, K
    """
    ranks = ['A'] + [str(n) for n in range(2, 11)] + ['J', 'Q', 'K']
    
    deck = 4*ranks
    random.seed(seed)
    random.shuffle(deck)
    return deck

# Shoe creator
def create_shoe(n=8, seed=None):
    shoe = []
    for _ in range(n):
        shoe += create_deck(seed)
    random.shuffle(shoe)
    return shoe

# Determining value of card - Only used in Player.observe_count() and Player.strategy() to make logic easier to read:
def card_value(card):
    if card == 'A':
        return 11
    elif card in ['10', 'J', 'Q', 'K']:
        return 10
    else:
        return int(card)

# Hand values function - returns a list of the possible combinations of hands
# Lists longer than 2 implies a soft total case, and there is an ace somewhere in the hand
def hand_values(hand):
    """
    Given a list of cards (e.g. ['A', '6']),
    return a list of all possible total values.

    Face cards (J, Q, K) count as 10,
    Aces (A) can be 1 or 11,
    Numeric cards count as their integer value.
    
    Examples:
      - A hand of ['A','6'] should return [7, 17].
      - A hand of ['A' 'A'] could return [2, 12, 22].
    """
    # This list will store all possible totals as we process each card.
    possible_totals = [0]
    
    for card in hand:
        rank = card
        next_totals = []
        
        if rank == 'A':
            # An Ace can be 1 or 11.
            for total in possible_totals:
                next_totals.append(total + 1)   # Count Ace as 1
                next_totals.append(total + 11)  # Count Ace as 11
        elif rank in ['J', 'Q', 'K', '10']:
            # Face cards and 10 are all worth 10.
            for total in possible_totals:
                next_totals.append(total + 10)
        else:
            # Numeric cards 2-9, convert rank to int.
            value = int(rank)
            for total in possible_totals:
                next_totals.append(total + value)
        
        # Update possible_totals for next iteration.
        possible_totals = next_totals

    # Remove any duplicates and sort the values.
    unique_totals = sorted(set(possible_totals))
    
    return unique_totals

# Best value for a given hand, which is important for dealers and making decisions given strategies
def best_value(hand):
    # Returns -1 if busted, otherwise returns 
    valid = [x for x in hand_values(hand) if x <= 21]
    return max(valid) if valid else 0