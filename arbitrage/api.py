"""
Functions for access to the manifold API.
"""
import time
import requests
import functools
from constants import API_KEY


READ_REQUEST_RATE_LIMIT = 0.01  # seconds
BET_RATE_LIMIT = 6  # seconds
BOT_USERNAME = "JointBot"
BOT_ID = "dTaXWSfwgkSAJDDlzmIGrEQIl2X2"


def get_balance():
    """
    Get the balance of the bot's account.
    """

    url_query = f"https://api.manifold.markets/v0/user/{BOT_USERNAME}"
    # Sleep for a time per request of API
    time.sleep(READ_REQUEST_RATE_LIMIT)
    response = requests.get(url_query)

    if response.status_code != 200:
        print("Error fetching user data")
        print(response.text)
        return []

    return response.json()["balance"]


def get_data_from_slug(slug):

    print(f"Getting market data for {slug}")
    # TODO see https://docs.manifold.markets/api#get-v0bets for docs on getting open limit orders

    url_query = f"https://api.manifold.markets/v0/slug/{slug}"
    # Sleep for a time per request of API
    time.sleep(READ_REQUEST_RATE_LIMIT)
    response = requests.get(url_query)

    if response.status_code != 200:
        print(f"Error fetching for market {slug}")
        print(response.text)
        return []

    return response.json()


def get_data_from_marketID(marketId):

    print(f"Getting market data for {marketId}")
    # TODO see https://docs.manifold.markets/api#get-v0bets for docs on getting open limit orders

    url_query = f"https://api.manifold.markets/v0/market/{marketId}"
    # Sleep for a time per request of API
    time.sleep(READ_REQUEST_RATE_LIMIT)
    response = requests.get(url_query)

    if response.status_code != 200:
        print(f"Error fetching for market {marketId}")
        print(response.text)
        return []

    return response.json()


def get_markets():
    """
    Get all the markets.
    """
    # TODO see https://docs.manifold.markets/api#get-v0bets for docs on getting open limit orders

    url_query = "https://api.manifold.markets/v0/markets"
    # Sleep for a time per request of API
    time.sleep(READ_REQUEST_RATE_LIMIT)
    response = requests.get(url_query)

    if response.status_code != 200:
        print("Error fetching for markets")
        print(response.text)
        return []

    return response.json()


def post_order_binary(market_id, mana_amount, outcome, end_prob, expiration_delta=60*1000):
    """
    Post an order to the market with the given id.
    """
    # TODO see https://docs.manifold.markets/api#post-v0bets for docs on posting orders

    print(
        f"Posting order for market {market_id}, for {mana_amount} mana to outcome {outcome}, with end prob {end_prob}")

    # From mqp "yeah you need to specify also an answerId"

    assert (outcome in ["YES", "NO"])

    expiration_time = time.time() + expiration_delta

    # url_query = f"https://api.manifold.markets/v0/bet?amount={amount}&contractId={market_id}&outcome={outcome}&limitProb={end_prob}&expiresAt={expiration_time}"
    # Sleep for a time per request of API
    time.sleep(BET_RATE_LIMIT)
    response = requests.post(
        "https://api.manifold.markets/v0/bet",
        json={
            # This can't be a float, even though the backend supports floats
            "amount": int(mana_amount),
            "outcome": outcome,
            "contractId": market_id
        },
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Key {API_KEY}"
        }
    )

    if response.status_code != 200:
        print(f"Error posting order for market {market_id}")
        print(response.text)
        return False

    if abs(response.json()["probAfter"] - end_prob) > 0.001:
        print(f"Weird order for market {market_id}")
        print(
            f"Expected final prob {end_prob} but got {response.json()['probAfter']}")
        print(response.text)
        return True

    print("Success")

    return True


def post_order_independent_multi(market_id, answer_id, mana_amount, outcome, limit_prob, expiration_delta=60*1000):
    """
    Post an order to the multimarket market with the given id.
    """
    # TODO see https://docs.manifold.markets/api#post-v0bets for docs on posting orders

    print(
        f"Posting order for market {market_id} {answer_id}, for {mana_amount} mana to outcome {outcome}, with limit prob {limit_prob}")

    assert (outcome in ["YES", "NO"])

    expiration_time = time.time() + expiration_delta

    # url_query = f"https://api.manifold.markets/v0/bet?amount={amount}&contractId={market_id}&outcome={outcome}&limitProb={limit_prob}&expiresAt={expiration_time}"
    # Sleep for a time per request of API
    time.sleep(BET_RATE_LIMIT)
    response = requests.post(
        "https://api.manifold.markets/v0/bet",
        json={
            # I think this can be a float if desired
            "amount": int(mana_amount),
            "outcome": outcome,
            "contractId": market_id,
            "answerId": answer_id
        },
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Key {API_KEY}"
        }
    )

    if response.status_code != 200:
        print(f"Error posting order for market {market_id}")
        print(response.text)
        return False

    print("Success")
    # print(response.text)
    return True


def get_bets_of_user(username):

    url_query = f"https://api.manifold.markets/v0/bets?username={username}"
    # Sleep for a time per request of API
    time.sleep(READ_REQUEST_RATE_LIMIT)
    response = requests.get(url_query)

    if response.status_code != 200:
        print(f"Error fetching bets of user {username}")
        print(response.text)
        return []

    return response.json()


def get_positions(marketId):
    """
    Get all the positions of everyone in some market
    """

    url_query = f"https://api.manifold.markets/v0/market/{marketId}/positions"
    # Sleep for a time per request of API
    time.sleep(READ_REQUEST_RATE_LIMIT)
    response = requests.get(url_query)

    if response.status_code != 200:
        print("Error fetching positions")
        print(response.text)
        return []

    return response.json()


def get_position_for_user(marketId, userId):
    """
    Get all the positions of someone in some market
    """

    url_query = f"https://api.manifold.markets/v0/market/{marketId}/positions?userId={userId}"
    # Sleep for a time per request of API
    time.sleep(READ_REQUEST_RATE_LIMIT)
    response = requests.get(url_query)

    if response.status_code != 200:
        print("Error fetching positions")
        print(response.text)
        return []

    return response.json()


def request_loan():

    url_query = "https://api.manifold.markets/request-loan"
    # Sleep for a time per request of API
    time.sleep(BET_RATE_LIMIT)
    response = requests.get(
        url_query,
        headers={
            "Authorization": f"Key {API_KEY}"
        }
    )

    if response.status_code != 200:
        print("Error requesting loan")
        print(response.text)
        return []

    return response.json()


response = request_loan()
print(response)
