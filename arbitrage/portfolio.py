"""
A module to represent a portfolio of shares.
"""

from shares import Share, InfoState
from api import get_balance
import cvxpy as cp
from collections import Counter
import logging

logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', 
                    filename='bot.log', encoding='utf-8', 
                    level=logging.DEBUG)

DEFAULT_HOLDING_CAP = 317
DEFAULT_SPENDING_CAP = 319
DEFAULT_API_FEE_PER_TRADE = 0.25

def log(msg):
    logging.info(msg)
    print(msg)

class Portfolio():
    """
    A class to represent a portfolio of shares.
    """
    
    def __init__(self, shares):
        # if shares is a list, the weights are all 1
        if isinstance(shares, list):
            for share in shares:
                assert(isinstance(share, Share))
            self.share_counts = Counter()
            for share in shares:
                self.share_counts[share] += 1
        # if shares is a dict, the keys are the shares and the values are the weights
        elif isinstance(shares, dict):
            for share in shares.keys():
                assert(isinstance(share, Share))
            self.share_counts = Counter(shares)
        elif isinstance(shares, Counter):
            for share in shares.keys():
                assert(isinstance(share, Share))
            self.share_counts = shares
        else:
            raise ValueError(f"shares must be a list or a dict, but is {type(shares)}")
        
        # Assert that none of the shares are the compliments of others
        for share in self.share_counts.keys():
            assert(~share not in self.share_counts)

    @property
    def shares(self):
        """
        Return the shares in the portfolio.
        """
        return self.share_counts.keys()
    
    def refresh_all(self):
        """
        Refresh all the shares in the portfolio.
        """
        for share in self.shares:
            share.refresh()
        
    def plan_arbs(self, true_value=1, 
                  holdings=None, api_fee_per_trade=DEFAULT_API_FEE_PER_TRADE,   
                  complimentary_holdings=None, 
                  share_holding_cap=DEFAULT_HOLDING_CAP, 
                  share_spending_cap=DEFAULT_SPENDING_CAP):
        """
        Uses cvxpy to find most profitable arbing of portfolio.

        Given liquidity constraints of various kinds.
         
        Returns a dict of *float* amounts to spend on each share in the portfolio.
        """
        # If we're not given holdings, assume we have none
        if holdings is None:
            holdings = { share : 0 for share in self.shares}
        assert(isinstance(holdings, dict))
        # If we're not given complimentary holdings, assume we have none
        if complimentary_holdings is None:
            complimentary_holdings = { share : 0 for share in self.shares}
        # If the share spending cap is a number, turn it into a dict
        if isinstance(share_holding_cap, (int, float)):
            share_holding_cap = { share : share_holding_cap for share in self.shares}
        # If the share purchase individual cap is a number, turn it into a dict
        if isinstance(share_spending_cap, (int, float)):
            share_spending_cap = { share : share_spending_cap for share in self.shares}
        

        # Get the info states of the markets
        initial_info_states = { share : share.market.current_state() for share in self.shares }

        # Set up variables for the optimization problem        

        # Share weight-in-portfolio constants
        share_weights = { share : cp.Constant(self.share_counts[share]) for share in self.shares }
        # A variable for each share representing how much is to be spent on it
        mana_spent_variables = { share : cp.Variable(name=f"Mana spent on {share}") for share in self.shares }
        # For each share type, a variable representing how many shares of it are to be purchased
        share_amount_variables = { share : cp.Variable(name=f"Share acquired of {share}") for share in self.shares }
        # Make a variable for each share representing how many yes and no shares are to be sent to the pool in the swap
        sent_in_swap = { share : cp.Variable(shape=(2), name=f"Sent in swap of {share}") for share in self.shares }

        pool_before = { share : cp.Constant(
            [initial_info_states[share].pool_yes, initial_info_states[share].pool_no]) for share in self.shares
        }

        pool_after = {share : pool_before[share] + sent_in_swap[share] for share in self.shares}

        # For each share, introduce a constraint that the amount of mana spent on yields that many shares
        # The constrain says that the constant function y^p n^(1-p) in the pool 
        purchase_constraints = []
        for share in self.shares:
            p = [share.market.p, 1 - share.market.p]

            purchase_constraints.append(
                cp.geo_mean(pool_after[share], p=p) >= cp.geo_mean(pool_before[share], p=p)
            )
            # we can't spend negative mana
            purchase_constraints.append(
                mana_spent_variables[share] >= 0
            )
            if share.yes:
                # The amount of NO shares we send is equal to the money we exchange for shares
                purchase_constraints.append(
                    mana_spent_variables[share] == sent_in_swap[share][1]
                )
                # The amount of YES shares we receive is equal to the shares we get in the swap, plus those we get in the mana for set of complimentary shares exchange
                purchase_constraints.append(
                    share_amount_variables[share] == -sent_in_swap[share][0] + mana_spent_variables[share]
                )
            else:
                purchase_constraints.append(
                    mana_spent_variables[share] == sent_in_swap[share][0]
                )
                purchase_constraints.append(
                    share_amount_variables[share] == -sent_in_swap[share][1] + mana_spent_variables[share]
                )
            if share_spending_cap is not None:
                # We can't spend more than the hard cap on any one share
                purchase_constraints.append(
                    mana_spent_variables[share] <= share_spending_cap[share]
                )
            if share_holding_cap is not None:
                # We can't hold more than the hard cap on any one share
                purchase_constraints.append(
                    share_amount_variables[share] - complimentary_holdings[share]
                        + holdings[share] <= share_holding_cap[share]
                )

        # The risk free profit is 
        # the amount of complete complimentary sets of portfolio copies acquired
        # minus the amount of mana spent
        # Subtract the trading fees as well
        feeless_profit = true_value * cp.min(cp.hstack([share_amount_variables[share] for share in self.shares]) / cp.hstack([share_weights[share] for share in self.shares])) - cp.sum([mana_spent_variables[share] for share in self.shares]) 
        profit = feeless_profit - api_fee_per_trade * len(self.shares)

        # Optimize for the risk free profit,
        objective = cp.Maximize(profit)
        problem = cp.Problem(objective, purchase_constraints)
        problem.solve(solver=cp.SCS) # This solver doesn't fail, others do, don't know why

        if problem.status != cp.OPTIMAL:
            for constraint in purchase_constraints:
                print(constraint)
            raise ValueError(f"Problem status is {problem.status}")

        profit = profit.value
        # print(f"PROFIT is {profit} on api fee {api_fee_per_trade} and true value {true_value}")
        
        if profit is None:
            for constraint in purchase_constraints:
                print(constraint)
            raise ValueError(f"Profit is {profit}, which is not a number")

        mana_spent = {share : mana_spent_variables[share].value for share in self.shares}

        for share in self.shares:
            assert(pool_after[share][0].value >= 0)
            assert(pool_after[share][1].value >= 0)

        return mana_spent


    def exec_arbs(self, dry_run=True, true_value=1,
                  api_fee_per_trade=DEFAULT_API_FEE_PER_TRADE,
                  holdings=None, 
                  complimentary_holdings=None, 
                  share_holding_cap=DEFAULT_HOLDING_CAP, 
                  share_spending_cap=DEFAULT_SPENDING_CAP):
        """
        Profitability/liquidity reqs of an arbing of portfolio.
         
        Assuming that the true value of the portfolio is at least `true_value`.
        """

        # Refresh the info on all the markets
        self.refresh_all()

        # If we're not given holdings, assume we have none
        if holdings is None:
            holdings = { share : 0 for share in self.shares}
        assert(isinstance(holdings, dict))
        # If we're not given complimentary holdings, assume we have none
        if complimentary_holdings is None:
            complimentary_holdings = { share : 0 for share in self.shares}

        arb = self.plan_arbs(true_value=true_value, 
                        api_fee_per_trade=api_fee_per_trade,
                       holdings=holdings, complimentary_holdings=complimentary_holdings, 
                      share_holding_cap=share_holding_cap, 
                      share_spending_cap=share_spending_cap)

        # log(f"Arb as floats")
        # for share in self.shares:
        #     log(f"    {share}: {arb[share]}")

        # Convert to ints
        arb = { share : int(arb[share]) for share in self.shares }
        
        # Get the info states of the markets
        initial_info_states = { share : share.market.current_state() for share in self.shares }
        final_info_states = { share : initial_info_states[share].new_state_from_buy(arb[share], share.yes) for share in self.shares }

        initial_probs = { share : initial_info_states[share].prob for share in self.shares }
        final_probs = { share : final_info_states[share].prob for share in self.shares }

        total_mana_spent = sum(arb.values())

        shares_received = { share : initial_info_states[share].shares_received_from_buy(arb[share], share.yes) for share in self.shares }

        portfolio_copies = min(shares_received[share] / self.share_counts[share] for share in self.shares)

        profit = portfolio_copies * true_value - total_mana_spent - 0.25 * len(self.shares)
        
        if profit <= 0:
            log(f"Skipping arb because profit is {profit}")
            log(f"    Portfolio:")
            log(f"{self}")
            log(f"    Arb:")
            for share in self.shares:
                log(f"    {share}: {arb[share]}")
            

            return


        # Check that we have enough mana to execute the arb
        current_balance = get_balance()
        if total_mana_spent > current_balance:
            log(f"Not enough mana to execute arb: {total_mana_spent} mana to be spent, {current_balance} mana in balance")
            return

        shares_recombined = {share : min(shares_received[share], complimentary_holdings[share]) for share in self.shares}
        total_shares_recombined = sum(shares_recombined.values())

        balance_decrease = total_mana_spent - total_shares_recombined

        # if balance_decrease > 0:
        #     log(f"Skipping arb because not enough shares to recombine:")
        #     log(F"    We can recombine {total_shares_recombined} shares, but spend {total_mana_spent} mana on the arb")
        #     log(f"    Portfolio: {self}")
        #     return

        if balance_decrease > 0:
            roi = profit / balance_decrease
        else:
            roi = 1000000

        # If we've already touched any of the markets in this collection, skip it

        log(f"\n----------------------------")

        for share in self.shares:
            log(f"Considering purchase of {share}")
            log(f"    URL: {share.market.url}")
            if holdings[share] > 0:
                log(f"    Bot already owns {holdings[share]:.1f} of this share type")
            elif complimentary_holdings[share] > 0:
                log(f"    Bot already owns {complimentary_holdings[share]:.1f} of the *complimentary* share type")
            else:
                log(f"    No preexisting holdings in this market")
            log(f"    Suggested spend: {arb[share]} mana to get {shares_received[share]:.1f} shares")
            log(f"    From initial prob {initial_probs[share]*100:.1f}% to final prob {final_probs[share]*100:.1f}%")
            if complimentary_holdings[share] > 0:
                log(f"    We can recombine {shares_recombined[share]} shares")

        log("")
        log("Arb summary")
        if balance_decrease > 0:
            log(f"This arb profits {profit} on a starting capital {total_mana_spent}, decreasing balance by {balance_decrease}, for an ROI of {100*roi:.2f}%")
        else:
            log(f"This arb profits {profit} on a starting capital {total_mana_spent}, *increasing* balance by {-balance_decrease}")

        if any(arb[share] < 2 for share in self.shares):
            log("Not enough mana being spent")
            return

        if any(arb[share] > 300 for share in self.shares):
            log("Too much mana being spent")
            quit()



        log(f"Looks good. Executing arb...")
        for share in self.shares:
            log(f"\nOn the market: {share}")
            log(f"   at {share.market.url}")
            log(f"   paying {arb[share]:.0f} mana for {shares_received[share]:.2f} shares")

            if not dry_run:
                success = share.post_order(arb[share], final_probs[share])
                if not success:
                    log("Problem with order")
                    log(f"Aborting")
                    log("Market data from before post")
                    log(f"{share.market.api_data_}")
                    quit()

                # TODO validate shares received is at least what was calculated
                    
        for share in self.shares:
            share.refresh()

        log(f"----------------------------")

    # Add portfolios
    def __add__(self, other):
        if isinstance(other, Portfolio):
            
            return Portfolio(self.share_counts + other.share_counts)
        else:
            raise ValueError("Can only add two portfolios")
        
    def __mul__(self, other):
        if isinstance(other, int):
            return Portfolio({share : self.share_counts[share] * other for share in self.shares})
        else:
            raise ValueError("Can only multiply a portfolio by an int")
        
    # Subtract portfolios
    def __sub__(self, other):
        if isinstance(other, Portfolio):
            return Portfolio(self.share_counts - other.share_counts)
        else:
            raise ValueError("Can only subtract two portfolios")
        
    # Compare portfolios
        
    def __eq__(self, other):
        if isinstance(other, Portfolio):
            return self.share_counts == other.share_counts
        else:
            raise ValueError("Can only compare two portfolios")
        
    def __ne__(self, other):
        if isinstance(other, Portfolio):
            return self.share_counts != other.share_counts
        else:
            raise ValueError("Can only compare two portfolios")
        
        
    def __repr__(self):
        return "\n".join(f"{self.share_counts[share]} shares in {share}" for share in self.shares)
    
    def __str__(self):
        return "\n".join(f"{self.share_counts[share]} shares in {share}" for share in self.shares)
    
    def __hash__(self):
        return hash(self.share_counts)
    
    def __len__(self):
        return len(self.share_counts)
    
    def __neg__(self):
        return Portfolio(-self.share_counts)
    
    def marginal_price(self):
        """
        Return the marginal cost of buying `amount` shares of `share` in this portfolio.
        """
        return sum(share.marginal_price() * self.share_counts[share] for share in self.shares)
    
    def get_complementary_portfolio(self):
        """
        Return the portfolio of shares that are the compliments of the shares in this portfolio.
        """
        return Portfolio({~share : self.share_counts[share] for share in self.shares})