import numpy as np
import nashpy as nash
import pygambit
import matplotlib.pyplot as plt


def randomize_game(payoff):
    # m = payoff.shape[0]
    # n = payoff.shape[1]
    # g = pygambit.Game.new_table([m,n])
    g = pygambit.Game.from_arrays(payoff, -payoff)
    g.players[0].label = "Row"
    g.players[1].label = "Column"
    # for i in range(m):
    #     for j in range(n):
    #         g[i, j][0] = payoff[i,j]
    #         g[i, j][1] = -g[i, j][0]
    # g.add_outcome(list(payoff))
    
    return g

# solve a 2-player zero-sum game with the double-oracle algorithm
# tabular form, matrix A is the payoff of the row player
def double_oracle(A: np.ndarray):
    rows = A.shape[0]
    cols = A.shape[1]
    
    # initialize arrays of row/column flags (if true, then the corresponding strategy is in the population)
    row_flags = [True] + (rows - 1) * [False]
    col_flags = [True] + (cols - 1) * [False]

    # initialize lists of available strategies
    row_strategies = [i for i in range(rows) if row_flags[i]]
    # print(row_strategies)
    
    col_strategies = [i for i in range(cols) if col_flags[i]]
    # print(col_strategies)
    n = 0
    
    regret_row = []
    regret_col = []

    while True:
        n = n + 1

        # solve the game by nashpy
        # Ar here is the matrix under the current strategies
        Ar = A[np.ix_(row_strategies, col_strategies)]
        
        matching_pennies = nash.Game(Ar)
        result = matching_pennies.linear_program()
        xr_row = result[0]
        # print(xr_row)
        xr_col = result[1]
        # print(xr_col)
        
        # x_row is the final row player strategy 
        # assert len(xr_row) == len(row_strategies)
        x_row = np.zeros(A.shape[0])
        for i in range(len(xr_row)):
            x_row[row_strategies[i]] = xr_row[i] 
        
        
        # extend restricted col strategy
        # assert len(xr_col) == len(col_strategies)
        x_col = np.zeros(A.shape[1])
        for i in range(len(xr_col)):
            x_col[col_strategies[i]] = xr_col[i]
        
        print("Current iteration is: ", n)
        print("Row player strategy is: ", x_row)
        print("Column player strategy is: ", x_col)

        # compute response values for the restricted strategies
        # TODO： Check this condition and probably reshape the x_row and x_col
        current_value_row = x_row.T @ (A @ x_col)
        current_value_col = x_col.T @ (-A.T @ x_row)
        
        row_values = A @ x_col
        col_values = -A.T @ x_row

        updated = False

        # add best responses
        
        # TODO: Check the update condition again
        # max val for the row player
        value_row = row_values.max()
        current_regret_row = value_row - current_value_row
        regret_row.append(current_regret_row)
        for i in range(len(row_values)):
            if np.isclose(row_values[i], value_row) and row_flags[i] is False:
                row_strategies.append(i)
                row_flags[i] = True
                updated = True
                break

        # min val for the column player
        value_col = col_values.max()
        current_regret_col = value_col - current_value_col
        regret_col.append(current_regret_col)
        for i in range(len(col_values)):
            if np.isclose(col_values[i], value_col) and col_flags[i] is False:
                col_strategies.append(i)
                col_flags[i] = True
                updated = True
                break
        
        if not updated:
            # print(regret_col)
            # print(regret_row)
            fig, ax = plt.subplots()
         
            x = [x for x in range(len(regret_row))]
            ax.plot(x, regret_row, label='regret_row')
            ax.plot(x, regret_col, label='regret_col')
            ax.set_xlabel('Iteration')
            ax.set_ylabel('Regret') 
            ax.set_title('Regret Plot')
            ax.legend() 

            plt.show() 
            return x_row, x_col
        
def double_oracle_with_gambit(A: np.ndarray):
    rows = A.shape[0]
    cols = A.shape[1]
    
    # initialize arrays of row/column flags (if true, then the corresponding strategy is in the population)
    row_flags = [True] + (rows - 1) * [False]
    col_flags = [True] + (cols - 1) * [False]

    # initialize lists of available strategies
    row_strategies = [i for i in range(rows) if row_flags[i]]
    # print(row_strategies)
    
    col_strategies = [i for i in range(cols) if col_flags[i]]
    # print(col_strategies)
    n = 0
    
    regret_row = []
    regret_col = []
    
    while True:
        n = n + 1

        # solve the game by nashpy
        # Ar here is the matrix under the current strategies
        Ar = A[np.ix_(row_strategies, col_strategies)]
        # print(Ar)
        
        current_game = randomize_game(Ar)
        # strategy = pygambit.gambit.Strategy(game = current_game, player = current_game.players[0])
        # print(strategy)
        nash_row_prob = []
        nash_col_prob = []
        
            
        result = pygambit.nash.lp_solve(current_game, rational=False) # , use_strategic=True
        # eqm = result.equilibria[0]
        # print(eqm.as_behavior())
        
        for strategy in current_game.players[0].strategies:
            # print(strategy)
            prob = result.equilibria[0]._getprob_strategy(strategy)
            nash_row_prob.append(prob)
            # print(prob)
            # print(result.equilibria[0]._regret(strategy))
    
            
        for strategy in current_game.players[1].strategies:
            # print(strategy)
            prob = result.equilibria[0]._getprob_strategy(strategy)
            nash_col_prob.append(prob)
        
        # print(result.equilibria[0]["Row"])
        # matching_pennies = nash.Game(Ar)
        # result = matching_pennies.linear_program()
        
        xr_row = np.array(nash_row_prob)
        # # print(xr_row)
        xr_col = np.array(nash_col_prob)
        # # print(xr_col)
        # x_row is the final row player strategy 
        # assert len(xr_row) == len(row_strategies)
        x_row = np.zeros(A.shape[0])
        for i in range(len(xr_row)):
            x_row[row_strategies[i]] = xr_row[i] 
        
        
        # extend restricted col strategy
        # assert len(xr_col) == len(col_strategies)
        x_col = np.zeros(A.shape[1])
        for i in range(len(xr_col)):
            x_col[col_strategies[i]] = xr_col[i]
        
        
        print("Current iteration is: ", n)
        print("Row player strategy is: ", x_row)
        print("Column player strategy is: ", x_col)

        # compute response values for the restricted strategies
        # TODO： Check this condition and probably reshape the x_row and x_col
        current_value_row = x_row.T @ (A @ x_col)
        current_value_col = x_col.T @ (-A.T @ x_row)
        
        row_values = A @ x_col
        col_values = -A.T @ x_row

        updated = False

        # add best responses
        
        # TODO: Check the update condition again
        # max val for the row player
        value_row = row_values.max()
        current_regret_row = value_row - current_value_row
        regret_row.append(current_regret_row)
        # print(current_regret_row)
        for i in range(len(row_values)):
            if np.isclose(row_values[i], value_row) and row_flags[i] is False:
                row_strategies.append(i)
                row_flags[i] = True
                updated = True
                break

        # min val for the column player
        value_col = col_values.max()
        current_regret_col = value_col - current_value_col
        regret_col.append(current_regret_col)
        # print(current_regret_col)
        for i in range(len(col_values)):
            if np.isclose(col_values[i], value_col) and col_flags[i] is False:
                col_strategies.append(i)
                col_flags[i] = True
                updated = True
                break
        
        if not updated:
            # print(regret_col)
            # print(regret_row)
            fig, ax = plt.subplots()
         
            x = [x for x in range(len(regret_row))]
            ax.plot(x, regret_row, label='regret_row')
            ax.plot(x, regret_col, label='regret_col')
            ax.set_xlabel('Iteration')
            ax.set_ylabel('Regret') 
            ax.set_title('Regret Plot')
            ax.legend() 

            plt.show() 

            return x_row, x_col
    
    