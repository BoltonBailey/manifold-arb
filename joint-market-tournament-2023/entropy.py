import scipy.stats
import numpy as np


middle_east = [[0.07, 0.38], [0.014, 0.54]]
space = [[0.19, 0.33], [0.11, 0.37]]
llms = [[0.29, 0.27], [0.20, 0.23]]
bitcoin = [[0.24, 0.26], [0.21, 0.29]]

def mutual_information(matrix):
    # Compute the mutual information of the matrix
    matrix = np.array(matrix)
    matrix /= matrix.sum()

    # Compute the marginal probabilities
    row_probabilities = matrix.sum(axis=1)
    column_probabilities = matrix.sum(axis=0)

    # Compute the entropy of the rows and columns
    row_entropy = scipy.stats.entropy(row_probabilities)
    column_entropy = scipy.stats.entropy(column_probabilities)


    # Compute the entropy of the matrix
    matrix_entropy = scipy.stats.entropy(matrix.flatten())

    # Compute the mutual information
    mutual_information = row_entropy + column_entropy - matrix_entropy

    return mutual_information



# Compute the mutual information of the matrix
middle_east_mi = mutual_information(middle_east)
space_mi = mutual_information(space)
llms_mi = mutual_information(llms)
bitcoin_mi = mutual_information(bitcoin)

print(f"Middle east {middle_east_mi}")
print(f"Space {space_mi}")
print(f"LLMS {llms_mi}")
print(f"Bitcoin {bitcoin_mi}")
