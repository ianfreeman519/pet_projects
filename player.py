from utils import Action, Outcome, hard_totals, soft_totals, split_totals, hand_values, best_value, card_value

# TODO need to handle betting logic, and make sure that bets actually go through when I expect them to - HAVE NOT HANDLED DOUBLING!!!

class Player:
    """
    One seat at the table.  Holds its own bankroll, strategy and list of
    current hands (to support splits).
    """
    def __init__(self, bankroll=0, bet_unit=1, bet_strategy="conservative"):
        self.bankroll       = bankroll
        self.bet_unit       = bet_unit
        self.bet_strategy   = bet_strategy        # fn(hand, dealer_up)
        self.bets           = []  # Bets populated for each hand (in case splits occur)
        self.hands          = []  # populated each round: [(cards, bet, is_doubled)]
        self.hits_taken     = [] # Hits taken per hand - important to handle for DS cases (A,7) vs 7 or 8
        self.count          = 0
        self.true_count     = 0
    
    # Helper for reading off strategy tables:
    def decide_deviation(self, response):
        """
        Basic strategy decisions by default take the form of "dec" with dec representing a decision
        If there is a deviation, they take the form of "dc1>+#dc2" with dc1 by default, or dc2 if the count is >+#
        For example, 10s rarely split, but they do split against upcard 6 at a +4 and above. This decision looks like: 
            "nos>+4yes"
        We have to first check to see if the decision from the table is longer than 3, then read off the default,
            threshold, and deviation decision
        We then compare to the count and decide 
        """
        # First check if there is a deviation
        if len(response) > 3:   # There is a deviation
            # Check the threshold value
            threshold = int(response[4:6])
            # Check for > logic:
            if response[3] == ">" and self.true_count > threshold:
                action = response[6:]   # Take the deviation
            elif response[3] == "<" and self.true_count < threshold:
                action = response[6:]   # Take the deviation
            else:
                action = response[0:3]  # Don't take the deviation
        else:   # No deviation for this decision, don't take one!
            action = response
        return action
    
    # --------- Strategy Definitions ---------
    def bet_deviation(self):
        new_bet = (self.true_count + 1) * self.bet_unit      # Bet function - we can change this later
        return min(new_bet, self.bet_unit)
    
    def strategy(self, upcard, hand_idx=0):
        hand = self.hands[hand_idx]
        values = hand_values(hand)
        # Ensure upcard is actually integer
        upcard = int(upcard)
        
        # First check blackjack or bust - then don't check the rest
        if best_value(hand) >= 21:
            return Action.STAND
        
        # Now check for splits (to handle case of two aces before hitting soft tottals)
        if len(hand) == 2 and (card_value(hand[0]) == card_value(hand[1])):
            response = self.decide_deviation(split_totals[(min(values), upcard)])
            if response == "yes":
                return Action.SPLIT # Splitting requires an immediate return, a "no split" does not
        
        # Now check for soft totals - if statement here in case above split totals sets response to "nos"
        if len(values) > 1:
            response = self.decide_deviation(soft_totals[(min(values), upcard)])
        
        # Finally we see the hard total table:
        else:
            response = self.decide_deviation(hard_totals[(min(values), upcard)])
            
        # We interpret the results and return the decision - Handle the case of "DST" - Double then stand
        if response == "dst" and len(hand) == 2:
            response = "dou"
        else:
            response = "sta"
        
        # Return decision logic
        match response:
            case "sta":
                return Action.STAND
            case "hit":
                return Action.HIT
            case "dou":
                return Action.DOUBLE            
        
    # ---------- round‑level hooks ----------
    def new_round(self):
        self.hands.clear()
        self.bets.clear()

    def place_bet(self, hand_idx):
        bet = self.bet_deviation()
        self.bankroll -= bet
        self.bets[hand_idx] += bet
        return bet
    
    def take_insurance(self):
        if self.true_count >= 3:
            return True
        else:
            return False

    # ---------- game‑level hooks -----------
    def new_shoe(self):
        self.hands.clear()
        self.count = 0

    # ---------- gameplay hooks ----------
    def observe_count(self, cards, n_decks_remaining):
        # TODO right now n_decks_remaining is a float, but we round to nearest half - might change something might not
        for card in cards:
            if card_value(card) >= 10:
                self.count -= 1
            elif card_value(card) <= 6:
                self.count += 1
        self.true_count = self.count / n_decks_remaining
    
    def receive_card(self, cards, hand_idx=0):
        for card in cards:
            self.hands[hand_idx].append(card)
            self.cards_taken += 1

    def decide(self, dealer_upcard, hand_idx=0):
        return self.strategy(dealer_upcard, hand_idx)


    # ---------- settlement ----------
    def settle(self, hand_idx, outcome, BJ_payout=1.5):
        if outcome == Outcome.WIN:
            self.bankroll += 2   * self.bets[hand_idx]
        elif outcome == Outcome.BJ:
            self.bankroll += BJ_payout * self.bets[hand_idx]
        elif outcome == Outcome.PUSH:
            self.bankroll += 1.0 * self.bets[hand_idx]
        # loss: do nothing – chips already removed
