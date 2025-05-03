from player import Player
from player import Player
from dealer import Dealer
from table import Table
from tqdm import tqdm
from utils import card_value
import matplotlib.pyplot as plt
import numpy as np
from mpi4py import MPI    
import sys

# Reading number of shoes to test as a command line input 
if len(sys.argv) > 1:
    try:
        num_shoes = int(sys.argv[1])
    except Exception as e:
        raise "Enter number of shoes to simulate"
else:
    num_shoes = 200

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def simulate_many_shoes(table, num_shoes=200):
    """
    Simulate many shoes and track bankroll history for each player.
    
    Parameters:
        table (Table): Initialized Table instance.
        num_shoes (int): Number of full shoes to simulate.
    """
    for _ in range(num_shoes):
        table.play_shoe()
        for player in table.plist:
            player.bankroll_history.append(player.bankroll)

def analyze_blackjack_strategy_parallel(
    table_factory,
    starting_bankroll=1000,
    num_shoes=100,
    num_trials=1000
):
    local_trials = num_trials // size
    if rank == 0 and num_trials % size != 0:
        print(f"Warning: {num_trials} not evenly divisible by {size}. Truncating to {local_trials * size} total trials.")

    local_final_bankrolls = 0.0
    local_hands_played = 0
    local_ruins = 0

    # Show progress bar only for rank 0
    trial_iterator = tqdm(range(local_trials), desc=f"Rank {rank} Progress") if rank == 0 else range(local_trials)

    for _ in trial_iterator:
        table = table_factory()
        for player in table.plist:
            player.bankroll = starting_bankroll
            player.bankroll_history = [starting_bankroll]
            player.hands_played = 0

        simulate_many_shoes(table, num_shoes)

        player = table.plist[0]  # assume one player
        local_final_bankrolls += player.bankroll
        local_hands_played += player.hands_played
        if any(b < 0 for b in player.bankroll_history):
            local_ruins += 1


    # Reduce across all ranks
    total_final_bankrolls = comm.reduce(local_final_bankrolls, op=MPI.SUM, root=0)
    total_hands_played = comm.reduce(local_hands_played, op=MPI.SUM, root=0)
    total_ruins = comm.reduce(local_ruins, op=MPI.SUM, root=0)

    if rank == 0:
        actual_trials = local_trials * size
        avg_final = total_final_bankrolls / actual_trials
        avg_hands = total_hands_played / actual_trials
        ev_per_hand = (avg_final - starting_bankroll) / avg_hands
        risk_of_ruin = total_ruins / actual_trials

        print(f"\n[Parallel] After {actual_trials} trials of {num_shoes} shoes each:")
        print(f"  → Average final bankroll: ${avg_final:.2f}")
        print(f"  → Average hands played: {avg_hands:.1f}")
        print(f"  → Expected value per hand: ${ev_per_hand:.4f}")
        print(f"  → Risk of ruin (bankroll went negative): {risk_of_ruin:.2%}")



def table_factory():
    dealer = Dealer()
    players = [Player()]
    return Table(dealer, players, printout=False)

analyze_blackjack_strategy_parallel(table_factory, starting_bankroll=1000, num_shoes=num_shoes, num_trials=1000)