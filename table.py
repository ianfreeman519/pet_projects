import numpy as np
from player import Player
from dealer import Dealer
from utils import create_shoe, hand_values, best_value, Action, Outcome, card_value

class Table:
    """
    An object of a dealer and players these functions should be called to play a sim
    """
    
    #This should be called once ever 
    def __init__(self, dealer, plist, printout=False):
        self.dealer = dealer
        self.plist = plist
        self.printout = printout
        
    #this is how the table deals one card at a time
    def deal_card(self):
        card = self.dealer.deal_cards(1)
        for player in self.plist:
            player.observe_count(card, self.dealer.decks_remaining)
        return card

    def play_shoe(self):
        self.dealer.clear_shoe()
        self.dealer.new_shoe()
        
        for player in self.plist:
            player.new_shoe()
        
        #play rounds until the shoe is done
        while not self.dealer.cut_card_out:
            
            if self.printout:
                print()
                print("NEW ROUND")
                print()
                print(f"player count = {self.plist[0].count} ")
                print(f"player bankroll before {self.plist[0].bankroll}")
            
            # ------------- NEW ROUND -----------------------
            self.dealer.new_round()
            # each player places bet
            for player in self.plist:
                player.new_round()
                player.place_bet()
                
            # dealer takes upcard
            self.dealer.take_cards(self.deal_card())
            dealer_upcard = card_value(self.dealer.hand[0])
            
            # print(f"player hands {self.plist[0].hands}, {len(self.plist[0].hands)}")
            
            # each player gets one card
            for player in self.plist:
                for idx, bet in enumerate(player.bets):
                    player.take_card(self.deal_card(),idx)
                    
            # print(f"player hands {self.plist[0].hands} ,{self.plist[0].hands[0]} ,{self.plist[0].hands[0][0]}")
            
            # dealer takes their downcard
            # CAREFULL THE PLAYER NEEDS TO COUNT THIS LATER
            self.dealer.take_cards(self.dealer.deal_cards(1))
            
            
            #each player gets one card
            for player in self.plist:
                for idx, bet in enumerate(player.bets):
                    player.take_card(self.deal_card(),idx)
              
              
            if self.printout: 
                print(f"player bets{self.plist[0].bets}")     
                print(f"dealer hand {self.dealer.hand}")       
                print(f"player hands {self.plist[0].hands}")
            
            
            # Check for dealer blackjack
            dealer_blackjack = (best_value(self.dealer.hand) == 21)
            
            for player in self.plist:   # loop over player
                for idx, hand in enumerate(player.hands):   # loop over hands of each player
                    is_bj = (best_value(hand) == 21 and len(hand) == 2) # player blackjack bool stored in is_bj
                    
                    # Dealer shows Ace → player can take insurance or even money
                    if dealer_upcard == 11:
                        if is_bj and player.take_even_money(idx):  # You need to define this method
                            # Even money pays 1:1, guaranteed win
                            payout = 2 * player.bets[idx]
                            player.bankroll += payout
                            if self.printout:
                                print(f"[EVEN MONEY] Hand {idx}: Took even money, paid ${payout:.2f}")
                            continue  # Skip rest of blackjack logic

                        elif not is_bj and player.take_insurance(idx):
                            # Insurance bet is half the original bet
                            insurance_bet = 0.5 * player.bets[idx]
                            player.bankroll -= insurance_bet  # Deduct insurance bet
                            if dealer_blackjack:
                                player.bankroll += insurance_bet * 3  # Original insurance + 2:1 payout
                                if self.printout:
                                    print(f"[INSURANCE WIN] Hand {idx}: Insurance bet of ${insurance_bet:.2f} paid out")
                            else:
                                if self.printout:
                                    print(f"[INSURANCE LOSS] Hand {idx}: Lost insurance bet of ${insurance_bet:.2f}")
                                    
                    # Normal blackjack handling
                    if is_bj:
                        if dealer_blackjack:
                            if self.printout:
                                print(f"[BLACKJACK PUSH] Hand {idx}: Player has blackjack {hand}, dealer also has blackjack.")
                            player.settle(idx, Outcome.PUSH, self.printout, BJ_payout=1.5)
                        else:
                            if self.printout:
                                print(f"[BLACKJACK WIN] Hand {idx}: Player has blackjack {hand}, dealer does not.")
                            player.settle(idx, Outcome.BJ, self.printout, BJ_payout=1.5)

                            
            #if dealer has blackjack update count
            if dealer_blackjack:
                for player in self.plist:
                    player.observe_count(self.dealer.hand[1], self.dealer.decks_remaining)
                
                if self.printout:    
                    print(f"player count = {self.plist[0].count} ")
                continue #this gets us to the next round
    
    
            # After checking blackjacks go through and each player plays all their hands
            for player in self.plist:
                hand_idx = 0
                while hand_idx < len(player.hands):
                    while True:
                        decision = player.decide(dealer_upcard, hand_idx)

                        if decision == Action.HIT:
                            player.take_card(self.deal_card(), hand_idx)
                            if self.printout:
                                    print(f"[HIT] Hand {hand_idx} into {player.hands[hand_idx]}")
                                    
                            if best_value(player.hands[hand_idx]) <= 0: # IF 05/03: Changed threshold to handle negative because previous handling returned -1 if busted
                                if self.printout:
                                    print(f"[BUST] Hand {hand_idx} busted, {player.hands[hand_idx]}")
                                break

                        elif decision == Action.DOUBLE:
                            player.take_card(self.deal_card(), hand_idx)
                            player.double(hand_idx)
                            if self.printout:
                                print(f"[DOUBLE] Hand {hand_idx} doubled, {player.hands[hand_idx]}")
                            break
                        
                        # TODO if player splits aces, player isn't allowed to make more decisions afterwards. This logic allows more decisions
                        elif decision == Action.SPLIT:
                            card1 = player.hands[hand_idx][0]   # Take the first card of the original hand
                            card2 = player.hands[hand_idx][1]   # Second card of the original hand
                            new_card_1 = self.deal_card()[0]
                            new_card_2 = self.deal_card()[0]

                            # Update current hand
                            player.hands[hand_idx] = [card1, new_card_1]

                            # Add split hand
                            player.hands.append([card2, new_card_2])
                            player.bets.append(player.bets[hand_idx])
                            
                            player.bankroll -= player.bets[hand_idx]

                            if self.printout:
                                print(f"[SPLIT] Hand {hand_idx} split into {len(player.hands)} hands total")

                            continue  # Exit this hand loop, go back into main hand loop

                        elif decision == Action.STAND:
                            if self.printout:
                                print(f"[STAND] Hand {hand_idx} stands, {player.hands[hand_idx]}")
                            break

                    hand_idx += 1
                    
            # Now that dealer downcard is revealed (non-blackjack case), players observe it
            for player in self.plist:
                player.observe_count([self.dealer.hand[1]], self.dealer.decks_remaining)

            # Check if any player hands are not busted and not blackjack (i.e., still need to be compared)
            any_active_hands = any(
                best_value(hand) > 0 and not (best_value(hand) == 21 and len(hand) == 2)
                for player in self.plist
                for hand in player.hands)


            if not any_active_hands:
                # All player hands are busted → dealer does not draw
                if self.printout:
                    print("[ALL INACTIVE] Dealer does not draw cards.")

                continue  # Move to next round

            # Dealer plays out their hand
            while True:
                action = self.dealer.take_actions()
                if action == Action.HIT:
                    self.dealer.take_cards(self.deal_card())
                    if self.printout:
                        print(f"[DEALER HIT] New dealer hand: {self.dealer.hand}")
                    if best_value(self.dealer.hand) == 0:
                        if self.printout:
                            print(f"[DEALER BUST] Dealer busted with hand: {self.dealer.hand}")
                        break
                elif action == Action.STAND:
                    if self.printout:
                        print(f"[DEALER STAND] Dealer stands with hand: {self.dealer.hand}")
                    break
            
            
            dealer_val = best_value(self.dealer.hand)
            for player in self.plist:
                for idx, hand in enumerate(player.hands):
                    player_val = best_value(hand)
                    is_bj = best_value(hand) == 21 and len(hand) == 2
                    
                    #so we dont double count balckjacks 
                    #We should probably do all accounting right here though
                    if is_bj:
                        continue
                    
                    #This should take care of players busting and then dealer also busting
                    elif player_val > dealer_val:
                        if self.printout:
                            print(f"dealer value {dealer_val}, player value {player_val}")
                        
                        player.settle(idx, Outcome.WIN, self.printout)
                    
                    elif player_val == dealer_val:
                        player.settle(idx, Outcome.PUSH, self.printout)

    
            for player in self.plist:
                player.bankroll_history.append(player.bankroll)
                player.hands_played += len(player.hands)
                if self.printout:
                    print(f"player bankroll after {player.bankroll}")
                    
            # self.dealer.cut_card_out = True
        # Why the hell are we returning 2?
        return 2