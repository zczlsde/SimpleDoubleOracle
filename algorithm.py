import numpy as np
import nashpy as nash


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
        print("Current iteration is: ", n)
        print("Row player strategy is: ", xr_row)
        print("Column player strategy is: ", xr_col)
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

        # compute response values for the restricted strategies
        # TODO： Check this condition and probably reshape the x_row and x_col
        row_values = A @ x_col
        col_values = -A.T @ x_row

        updated = False

        # add best responses
        
        # TODO: Check the update condition again
        # max val for the row player
        value_row = row_values.max()
        for i in range(len(row_values)):
            if np.isclose(row_values[i], value_row) and row_flags[i] is False:
                row_strategies.append(i)
                row_flags[i] = True
                updated = True
                break

        # min val for the column player
        value_col = col_values.max()
        for i in range(len(col_values)):
            if np.isclose(col_values[i], value_col) and col_flags[i] is False:
                col_strategies.append(i)
                col_flags[i] = True
                updated = True
                break
        
        if not updated:
            return x_row, x_col