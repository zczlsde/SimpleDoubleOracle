from algorithm import double_oracle
import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--rows', type=int, default=10, help='The rows of the random game matrix')
parser.add_argument('-c', '--cols', type=int, default=10, help='The columns of the random game matrix')

args = parser.parse_args()

np.set_printoptions(precision=5)

rng = np.random.default_rng(1)
row_payoff = rng.uniform(-10, 10, (args.rows, args.cols))
double_oracle(row_payoff)