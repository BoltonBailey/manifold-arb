
# Manifold Python Scripts

This repo contains several scripts for interacting with [Manifold Markets](https://manifold.markets/home).

The main thing is the `arbitrage/` folder, which contains an implementation of an arbitrage bot based on `cvxpy`.

## TODOs

- [ ] Access the api via `manifoldpy`
  - [ ] Unfortunately, this looks a bit unmaintained now, so consider this a dependent issue.
- [ ] Fold the `politics/` folder into `arbitrage/`
- [ ] Make `Market` and `Share` hashable
- [ ] Track limit orders when computing arbs
- [ ] Add support for choose-1 multi-markets
  - [ ] Recomputing the amount of share received for a bet is possible with convex programming, but probably a bit tricky.
  - [ ] Maybe a good 80% solution is just to treat them like choose-many - I think that you alsways get more shares in a choose-1 than you would in a choose-many with the same appearance
    - [ ] This does not allow you to safely bet on multiple outcomes of a choose-1 simultaneously, though.
- [x] Add support for unlinked multimarkets
  - [ ] Now that this is done, Identify arbs in unlinked multis.
- [x] Add support for arbitrage opportunities where shares have different weights in the portfolio
- [ ] Add support for arbitrage of conditional markets (P(A|B), P(A), P(A&B))
- [ ] Prioritize opportunities by rate of return (risk-free profit / amount spent)^(1/time to resolve)
- [ ] Account for whether existing holdings would be sold when making arb decisions
  - [ ] There may be sufficient mana for a trade where there otherwise would not be
  - [ ] An arb may be more rate of return efficient or even infinite-rate-of-return if it sells existing holdings
  - [ ] Account for whether it is good to sell existing arbs to free up mana for new ones, if those new arbs make more profit than is lost by selling the old ones.
  - [ ] One might account for risk of bad data entry by putting hard caps on the holdings for a particular share.
- [ ] Schedule script to run regularly
- [ ] Find more arbitrage opportunities
  - [ ] Study existing arbitrage bots
    - [ ] Find all pairs of markets that an arbitrage bot has purchased on both in under 10 seconds.
  - [ ] Do large scale analysis of back to back trades made by the same user
  - [ ] Use large language models to find opportunities in new markets
- [ ] Logging (could be useful if something goes horribly wrong)
- [ ] Testing
  - [ ] Test that the convex optimization is working correctly
  - [ ] Test that the orders are being posted correctly
- [ ] Account for risk of bad data entry