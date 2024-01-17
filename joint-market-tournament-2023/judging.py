import time
import requests
import json
import matplotlib.pyplot as plt

import scipy.stats
import numpy as np

middle_east_slug = "israelhezbollah-conflict-killing-40"
middle_east_yes_yes_answer_id = "f1039ffb0f5f"
middle_east_yes_no_answer_id = "7325ea920cf5"
middle_east_no_yes_answer_id = "7ca945fd1ee3"
middle_east_no_no_answer_id = "47c86690899c"
space_slug = "will-starship-reach-space-in-2023-x"
space_yes_yes_answer_id = "fc1517a5880c"
space_yes_no_answer_id = "5043463d7799"
space_no_yes_answer_id = "99bd4c6bd697"
space_no_no_answer_id = "37d463fc541a"
bitcoin_slug = "bitcoin-etf-2023-x-new-alltime-high"
bitcoin_yes_yes_answer_id = "00f461756ed7"
bitcoin_yes_no_answer_id = "0cf64173ce93"
bitcoin_no_yes_answer_id = "a3be4d5f78d6"
bitcoin_no_no_answer_id = "f1c758bd1e06"
llms_slug = "will-gemini-be-released-before-2024"
llms_yes_yes_answer_id = "9e2d4e952a6a"
llms_yes_no_answer_id = "6ed3ae9a23a1"
llms_no_yes_answer_id = "bdef2145d60c"
llms_no_no_answer_id = "37eb93c9aeeb"

def mutual_information(matrix):
    # Takes a 2 by 2 by n matrix and computes the mutual information of the matrix along the first two axes

    # Compute the mutual information of the matrix
    matrix = np.array(matrix)
    matrix /= matrix.sum()

    # Compute the marginal probabilities
    row_probabilities = matrix.sum(axis=1)
    column_probabilities = matrix.sum(axis=0)

    # Compute the entropy of the rows and columns
    row_entropy = scipy.stats.entropy(row_probabilities, axis=0)
    column_entropy = scipy.stats.entropy(column_probabilities, axis=0)

    # print("row_entropy", row_entropy)
    # print("column_entropy", column_entropy)

    # Compute the entropy of the matrix
    matrix_entropy = scipy.stats.entropy(np.reshape(matrix, (4, -1)), axis=0)

    # print("matrix_entropy", matrix_entropy)

    # Compute the mutual information
    mutual_information = row_entropy + column_entropy - matrix_entropy

    return mutual_information

def get_bets(contract_slug):

    url_query = f"https://api.manifold.markets/v0/bets?contractSlug={contract_slug}"
    # Sleep for 1 second to avoid rate limiting
    time.sleep(1)
    response = requests.get(url_query)

    if response.status_code != 200:
        print(f"Error fetching bets for market {contract_slug}")
        print(response.text)
        return []
    
    return response.json()


def get_price_at_time(t, answer_id, price_times):
    # Get the price at a given time
    # price_times is a list of tuples (answer_id, price, time)
    # Return the price at the first time greater than time
    l = list(filter(lambda x: x[2] >= t and x[0] == answer_id, price_times))
    if len(l) == 0:
        return 0.5
    return l[0][1]



def get_price_times(contract_slug):

    bets = get_bets(contract_slug)
    answer_ids = list(set([bet["answerId"] for bet in bets]))

    print(f"Investigating market: {contract_slug}")
    print(f"Found answer ids: {answer_ids}")
    
    price_times = []

    for bet in bets:
        price_times.append((bet["answerId"], bet["probAfter"], bet["createdTime"]))
    

    # Sort by created time
    price_times.sort(key=lambda x: x[2])
    times = list(set([price_time[2] for price_time in price_times]))
    times.sort()
    print("b", times)
    times_ = list(filter(lambda x: 1698796801000 < x and x < 1704067201000, times))
    print("c", times_)
    times = [1698796801000] + times_ + [1704067201000]
    print("d", times)
    # For each answer id and each time, get the price for that answer id at the first time greater than that time
    probs_at_times = {
        answer_id : [get_price_at_time(t, answer_id, price_times) for t in times] 
            for answer_id in answer_ids
    }

    return times, probs_at_times




def analyze(contract_slug, answer_ids_ordered):

    print(f"Analyzing {contract_slug}")
    times, probs_at_times = get_price_times(contract_slug=contract_slug)

    probs_at_times = [probs_at_times[answer_id] for answer_id in answer_ids_ordered]
    probs_at_times = np.array(probs_at_times)
    probs_at_times = probs_at_times.reshape((2, 2, -1))

    # Compute the mutual information of the matrix
    mi = mutual_information(probs_at_times)

    # take the weighted average of the mutual information
    mi_average = np.average(mi[:-1], weights=np.diff(times))

    # Pyplot make two adjacent figures
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 10))

    fig.suptitle(f"Data for {contract_slug}")

    # Plot the probabilities over time on the top 
    
    # Title and labels
    ax1.set_title(f"Probabilities")
    # ax1.set_xlabel("Time")
    ax1.set_ylabel("Probability")
    # Let the x_lim

    print(times, probs_at_times)

    # Plot the probabilities over time
    ax1.step(times, probs_at_times[0, 0, :], label="Yes, Yes", where="post")
    ax1.step(times, probs_at_times[0, 1, :], label="Yes, No", where="post")
    ax1.step(times, probs_at_times[1, 0, :], label="No, Yes", where="post")
    ax1.step(times, probs_at_times[1, 1, :], label="No, No", where="post")

    # Plot the mutual information over time on the bottom, with scale factor 20
    ax2.set_title(f"Mutual Information")
    ax2.set_xlabel("Time")
    # Set the x axis to be dates
    ax2.set_xticks([1698796801000, 1704067201000], labels=["2023-11-01", "2024-01-01"])
    ax2.set_ylabel("Mutual Information")
    ax2.set_ylim(0, 0.15)
    ax2.step(times, mi, label="Mutual Information", where="post")
    #  make a dashed horizontal line at mi_average
    ax2.axhline(mi_average, color='grey', label="Avg MI", linestyle='--')
    # label the horizontal line with the average mutual information value
    # ax2.text(times[0], mi_average, f"Average mutual information: {mi_average}")
    plt.legend()
    plt.savefig(f"img/{contract_slug}_mi.png")
    plt.clf()


    print(f"{contract_slug} {mi}")

    return mi



analyze(contract_slug=middle_east_slug, answer_ids_ordered=[middle_east_yes_yes_answer_id, middle_east_yes_no_answer_id, middle_east_no_yes_answer_id, middle_east_no_no_answer_id])

analyze(contract_slug=space_slug, answer_ids_ordered=[space_yes_yes_answer_id, space_yes_no_answer_id, space_no_yes_answer_id, space_no_no_answer_id])

analyze(contract_slug=bitcoin_slug, answer_ids_ordered=[bitcoin_yes_yes_answer_id, bitcoin_yes_no_answer_id, bitcoin_no_yes_answer_id, bitcoin_no_no_answer_id])

analyze(contract_slug=llms_slug, answer_ids_ordered=[llms_yes_yes_answer_id, llms_yes_no_answer_id, llms_no_yes_answer_id, llms_no_no_answer_id])








quit()

middle_east_bets = api.get_bets(marketSlug=middle_east_slug)
# sleep for 1 second to avoid rate limiting
time.sleep(1)
space_bets = api.get_bets(marketSlug=space_slug)
# sleep for 1 second to avoid rate limiting
time.sleep(1)
bitcoin_bets = api.get_bets(marketSlug=bitcoin_slug)
# sleep for 1 second to avoid rate limiting
time.sleep(1)
llms_bets = api.get_bets(marketSlug=llms_slug)
# sleep for 1 second to avoid rate limiting
time.sleep(1)

print(len(middle_east_bets))
print(len(space_bets))
print(len(bitcoin_bets))
print(len(llms_bets))

for bet in middle_east_bets:
    print(f"Created time: {bet['createdTime']} to price {bet['probAfter']}")
    print(bet)