"""
This script is used to find and execute arbitrage opportunities on Manifold.

It calculates the optimal risk-free profit for a particular arbitrage opportunity via convex optimization on the amount spent on each share, accounting for fees. It then posts orders to the market to execute the arbitrage opportunity.

"""


from shares import *
from arb_listing import complimentary_collections
from api import get_balance

DRY_RUN = False




total_mana_spent = 0
starting_balance = get_balance()

# Sort complimentary collections by decreasing ROI
complimentary_collections.sort(key=lambda portfolio: portfolio.get_arb_stats()[-1], reverse=True)
touched_markets = set()

for portfolio in complimentary_collections:

    # If we've already touched any of the markets in this collection, skip it
    if any(share.market.market_id in touched_markets for share in portfolio.shares):
        continue

    # Add all the markets in this collection to the touched markets
    for share in portfolio.shares:
        touched_markets.add(share.market.market_id)


    print(f"\n-----")
    mana_spent, share_amounts, initial_probs, final_probs, profit, roi = portfolio.get_arb_stats()

    if profit is None or profit <= 0 or roi <= 0.01:
        continue

    for i, share in enumerate(portfolio.shares):
        print(f"   {share} at {share.market.url}")
        print(f"       suggested spend {int(mana_spent[i])} mana to get {share_amounts[i]:.1f} shares")
        print(f"       From initial prob {initial_probs[i]:.2f} to final prob {final_probs[i]:.2f}")
    about_to_spend = sum(mana_spent)
    print(f"This arb profits {profit} on a total mana investment of {about_to_spend}, for an ROI of {100*roi:.2f}%")

    if about_to_spend + total_mana_spent > starting_balance:
        print("Not enough mana")
        continue


    for i, share in enumerate(portfolio.shares):
        print(f"\nOn the market: {share}")
        print(f"   at {share.market.url}")
        print(f"   pay {mana_spent[i]:.0f} mana for {share_amounts[i]:.2f} shares")

        if not DRY_RUN:
            success = share.market.post_order(mana_spent[i], "YES" if share.yes else "NO", final_probs[i])
            if not success:
                print("Failed to post order")
                quit()
        total_mana_spent += mana_spent[i]


print(f"Total mana spent {total_mana_spent} from starting balance {starting_balance} to ending balance {get_balance()}")

