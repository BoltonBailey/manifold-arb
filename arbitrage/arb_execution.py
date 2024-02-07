"""
This script is used to find and execute arbitrage opportunities on Manifold.

It calculates the optimal risk-free profit for a particular arbitrage opportunity via convex optimization on the amount spent on each share, accounting for fees. It then posts orders to the market to execute the arbitrage opportunity.

"""


from shares import *
from arb_listing import complimentary_collections
from api import get_balance, get_position_for_user, request_loan, BOT_USERNAME, BOT_ID
import json
import logging
import schedule

DRY_RUN = False
DRY_RUN = True

# A maximum number of shares to hold of any one type
SHARE_HOLDING_LIMIT = 300
ROI_FLOOR = 0.01

logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s',
                    filename='bot.log', encoding='utf-8',
                    level=logging.DEBUG)


def log(msg):
    logging.info(msg)
    print(msg)


# pos = get_position_for_user("v4uXdQHU0VFksoecHm5C", BOT_ID)

# print(json.dumps(pos, indent=4))
# quit()

# logging.info(request_loan())
# quit()


# s = Share("will-donald-trump-be-the-2024-nomin")
# pos = get_position_for_user(s.market.market_id, BOT_ID)

# logging.info(json.dumps(pos, indent=4))

# quit()


def sort_and_execute_arbs():

    log(f"Assessing arbs...")

    starting_balance = get_balance()

    log(f"Found {len(complimentary_collections)} complimentary collections")
    log("\n")

    for portfolio in complimentary_collections:

        holdings = {}
        complimentary_holdings = {}

        for share in portfolio.shares:
            positions = get_position_for_user(share.market.market_id, BOT_ID)
            if len(positions) == 0:
                holdings[share] = 0
                complimentary_holdings[share] = 0
                continue
            assert len(positions) == 1
            position = positions[0]
            if position["hasYesShares"]:
                yes_shares = position["totalShares"]["YES"]
            else:
                yes_shares = 0

            if position["hasNoShares"]:
                no_shares = position["totalShares"]["NO"]
            else:
                no_shares = 0

            holdings[share] = yes_shares if share.yes else no_shares
            complimentary_holdings[share] = no_shares if share.yes else yes_shares
            # print(position)

        # print(f"holdings: {holdings}")
        # print(f"complimentary_holdings: {complimentary_holdings}")
        portfolio.exec_arbs(dry_run=DRY_RUN, holdings=holdings,
                            complimentary_holdings=complimentary_holdings)

    log(f"starting balance {starting_balance} to ending balance {get_balance()}")


log("Starting scheduled arb execution bot")

log("running loop")
while True:
    log("running sort_and_execute_arbs")
    sort_and_execute_arbs()
    quit()
    time.sleep(1 * 60)
    log("1")
    time.sleep(1 * 60)
    log("2")
    time.sleep(1 * 60)
    log("3")
    time.sleep(1 * 60)
    log("4")
    time.sleep(1 * 60)
    log("5")
    time.sleep(1 * 60)
    log("6")
    time.sleep(1 * 60)
    log("7")
    time.sleep(1 * 60)
    log("8")
    time.sleep(1 * 60)
    log("9")
    time.sleep(1 * 60)
