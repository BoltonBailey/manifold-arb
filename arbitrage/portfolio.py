"""
A module to represent a portfolio of shares.
"""

from shares import Share
import cvxpy as cp


def maniswap_prob_from_pool(pool_yes, pool_no, p):
    """
    Calculate the probability of a maniswap market with the given pool sizes and price.
    """
    return (pool_no * p / (pool_yes * (1-p) + pool_no * p))


class Portfolio():
    """
    A class to represent a portfolio of shares.
    """
    
    def __init__(self, shares):
        # if shares is a list, the weights are all 1
        if isinstance(shares, list):
            for share in shares:
                assert(isinstance(share, Share))
            self.shares = {share: 1 for share in shares}
        # if shares is a dict, the keys are the shares and the values are the weights
        elif isinstance(shares, dict):
            for share in shares.keys():
                assert(isinstance(share, Share))
            self.shares = shares
        else:
            raise ValueError("shares must be a list or a dict")
        
        # Assert that none of the shares are the compliments of others
        for share in self.shares.keys():
            assert(share.compliment not in self.shares)
        
    def get_arb_stats(self, true_value=1, share_purchase_cap=100):
        """
        Returns data about the ROI of an arbing of portfolio assuming that the true value of the portfolio is at least `true_value`.
        """

        # Share weight constant
        share_weights = [cp.Constant(self.shares[share]) for share in self.shares]
        # Make a variable for each share representing how much is to be spent on it
        mana_spent_variables = [cp.Variable(name=f"Mana spent on {share}") for share in self.shares]
        # For each share type, make a variable representing how many shares of it are to be purchased
        share_amount_variables = [cp.Variable(name=f"Share acquired of {share}") for share in self.shares]
        # Make a variable for each share representing how many yes and no shares are to be sent to the pool in the swap
        sent_in_swap = [cp.Variable(shape=(2)) for _ in self.shares]

        pool_before = [cp.Constant(
            [share.market.pool_yes, share.market.pool_no]) for share in self.shares
        ]
        # print(f"Initial pool values: {[pool_before[i].value for i in range(len(shares))]}")
        initial_probs = [maniswap_prob_from_pool(pool_before[i][0].value, pool_before[i][1].value, share.market.p) for i, share in enumerate(self.shares)]
        # print(f"Initial probabilities: {initial_probs}")

        pool_after = [pool_before[i] + sent_in_swap[i] for i in range(len(self.shares))]

        # For each share, introduce a constraint that the amount of mana spent on yields that many shares
        # The constrain says that the constant function y^p n^(1-p) in the pool 
        purchase_constraints = []
        for i, share in enumerate(self.shares):
            p = [share.market.p, 1 - share.market.p]

            purchase_constraints.append(
                cp.geo_mean(pool_after[i], p=p) >= cp.geo_mean(pool_before[i], p=p)
            )
            # we can't spend negative mana
            purchase_constraints.append(
                mana_spent_variables[i] >= 0
            )
            if share.yes:
                # The amount of NO shares we send is equal to the money we exchange for shares
                purchase_constraints.append(
                    mana_spent_variables[i] == sent_in_swap[i][1]
                )
                # The amount of YES shares we receive is equal to the shares we get in the swap, plus those we get in the mana for set of complimentary shares exchange
                purchase_constraints.append(
                    share_amount_variables[i] == -sent_in_swap[i][0] + mana_spent_variables[i]
                )
            else:
                purchase_constraints.append(
                    mana_spent_variables[i] == sent_in_swap[i][0]
                )
                purchase_constraints.append(
                    share_amount_variables[i] == -sent_in_swap[i][1] + mana_spent_variables[i]
                )

            # We can't spend more than the hard cap on any one share
            purchase_constraints.append(
                mana_spent_variables[i] <= share_purchase_cap
            )

        # The risk free profit is 
        # the amount of complete complimentary sets of portfolio copies acquired
        # minus the amount of mana spent
        # Subtract the trading fees as well
        profit = true_value * cp.min(cp.hstack(share_amount_variables) / cp.hstack(share_weights)) - cp.sum(mana_spent_variables) - 0.25 * len(self.shares)

        # Optimize for the risk free profit,
        objective = cp.Maximize(profit)
        problem = cp.Problem(objective, purchase_constraints)
        try:
            problem.solve(solver=cp.CLARABEL)
        except cp.SolverError:
            print("Solver error")
            return None, None, None, None, 0, 0

        profit = profit.value

        share_amounts = [share_amount_variables[i].value for i in range(len(self.shares))]
        mana_spent = [mana_spent_variables[i].value for i in range(len(self.shares))]

        # print(f"Final pool values: {[pool_after[i].value for i in range(len(shares))]}")
        final_probs = [maniswap_prob_from_pool(pool_after[i][0].value, pool_after[i][1].value, share.market.p) for i, share in enumerate(self.shares)]
        # print(f"Final probabilities: {final_probs}")

        roi = profit / sum(mana_spent)

        return mana_spent, share_amounts, initial_probs, final_probs, profit, roi


    # Add portfolios
    def __add__(self, other):
        if isinstance(other, Portfolio):
            raise NotImplementedError("Adding portfolios is not yet implemented")
        else:
            raise ValueError("Can only add two portfolios")