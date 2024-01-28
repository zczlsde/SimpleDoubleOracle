from algorithm import double_oracle, double_oracle_with_gambit
import argparse
import numpy as np
import pickle

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--rows', type=int, default=100, help='The rows of the random game matrix')
parser.add_argument('-c', '--cols', type=int, default=100, help='The columns of the random game matrix')
parser.add_argument('-g', '--gambit', type=bool, action=argparse.BooleanOptionalAction, help='If gambit=True, Gambit will be used to solve the LP. Otherwis, Nashpy will be used.')
parser.add_argument('-m', '--games', type=str, default="random", help="Select from 10,3-Blotto, 10,4-Blotto, 10,5-Blotto, 3-move parity game 2, tic_tac_toe...")

args = parser.parse_args()

np.set_printoptions(precision=5)

rng = np.random.default_rng(1)
row_payoff = rng.uniform(-10, 10, (args.rows, args.cols))

if args.games=="random":
    row_payoff = rng.uniform(-10, 10, (args.rows, args.cols))
else:
    with open("games/spinning_top_payoffs.pkl", "rb") as fh:
        payoffs = pickle.load(fh)
    row_payoff = payoffs[args.games]
    
# row_payoff = np.array([[0, -1, 1], [1, 0, -1], [-1, 1, 0]])
if args.gambit:
    double_oracle_with_gambit(row_payoff)
else:
    double_oracle(row_payoff)
