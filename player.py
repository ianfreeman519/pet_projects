from utils import Action, Outcome, hard_totals, soft_totals, split_totals, hand_values, best_value

class Player:
    """
    One seat at the table.  Holds its own bankroll, strategy and list of
    current hands (to support splits).
    """
    def __init__(self, bankroll=1_000, bet_unit=10, bet_strategy="conservative"):
        self.bankroll       = bankroll
        self.bet_unit       = bet_unit
        self.bet_strategy   = bet_strategy        # fn(hand, dealer_up)
        self.bets           = []  # Bets populated for each hand (in case splits occur)
        self.hands          = []  # populated each round: [(cards, bet, is_doubled)]
        self.hits_taken     = [] # Hits taken per hand - important to handle for DS cases (A,7) vs 7 or 8
        self.count          = 0
    # --------- Strategy Definition ---------
    def strategy(self, upcard, hand_idx=0):
        hand = self.hands[hand_idx]
        values = hand_values(hand)
        
        # First check blackjack or bust - then don't check the rest
        if best_value(hand) >= 21:
            return Action.STAND
        
        # Now check for splits (to handle case of two aces before hitting soft tottals)
        if len(hand) == 2 and (hand[0] == hand[1]):
            action = split_totals[(min(values), upcard)]
            
        
            
        

        
    # ---------- round‑level hooks ----------
    def new_round(self):
        self.hands.clear()

    def place_bet(self):
        bet = self.bet_unit
        self.bankroll -= bet
        self.hands.append([[], bet, False])   # (cards, wager, doubled?)
        return bet

    # ---------- game‑level hooks -----------
    def new_shoe(self):
        self.hands.clear()
        self.count = 0

    # ---------- gameplay hooks ----------
    def receive_card(self, card, hand_idx=0):
        self.hands[hand_idx].append(card)
        self.cards_taken += 1

    def decide(self, dealer_upcard, hand_idx=0):
        """Return an Action chosen by the strategy function."""
        cards, bet, doubled = self.hands[hand_idx]
        return self.strategy(cards, dealer_upcard,
                             can_double=not doubled and len(cards)==2,
                             can_split = len(cards)==2 and cards[0]==cards[1])

    # ---------- settlement ----------
    def settle(self, hand_idx, outcome, rules):
        cards, bet, doubled = self.hands[hand_idx]
        base = bet * (2 if doubled else 1)
        if outcome == Outcome.WIN:
            self.bankroll += 2*base
        elif outcome == Outcome.BJ:
            self.bankroll += base + base*rules['bj_payout']
        elif outcome == Outcome.PUSH:
            self.bankroll += base
        # loss: do nothing – chips already removed
