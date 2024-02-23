
# Manifold Python Scripts

This repo contains several scripts for interacting with [Manifold Markets](https://manifold.markets/home).

The main thing is the `arbitrage/` folder, which contains an implementation of an arbitrage bot based on `cvxpy`.

## How to use the Arbitrage Bot

1. Clone the repo
2. Get your API Key from <https://manifold.markets/profile>
3. Make a file called `constants.py` in the `arbitrage` folder
4. Add a line to the file that looks like `API_KEY = "00000000-1111-2222-3333-444444444444"`, but using your own key.
5. Run `arb_execution.py`



## TODOs

### Specific Arb Categories to add

- [ ] Things in the other files in this project
- [ ] 2024 POTUS
  - [ ] My blog post on arbing 2024 POTUS
  - [ ] State-by-state outcome arbs
- [ ] Add IMO markets
- [ ] Study existing arbitrage bots
- [ ] Find all pairs of markets that an arbitrage bot has purchased on both in under 10 seconds.
- [ ] Do large scale analysis of back to back trades made by the same user
- [ ] Use large language models to find opportunities in new markets
- [ ] Bitcoin
  - [ ] My preexisting markets
  - [ ] Maybe a new market "resolves as prob to btc price / 100000"

### General Arb capabitilites

- [ ] Write an arbitrageur that, instead of taking in a portfolio which is supposed to be greater than n, takes in a pair or more of portfolios which are supposed to be equivalent, and finds the best arb.
  - [ ] One way to accomplish - take the portfolio which is the sum of the first and the compliment of the second, and then buy the new portfolio.
  - [ ] Function that takes a portfolio and returns some generalized complement - A portfolio which adds with it to produce a constant or 1
  - [ ] Negative shares virtual portfolios
  - [ ] Ability for portfolios to include pure mana alongside shares.
- [ ] When I have a bunch of equivalent markets, rather than just pairing them off and arbing them (and making different prices if I arb two pairs), I should try to arb them all at once.
- [ ] Add support for choose-1 multi-markets
  - [ ] Recomputing the amount of share received for a bet is possible with convex programming, but probably a bit tricky.
  - [ ] Maybe a good 80% solution is just to treat them like choose-many - I think that you alsways get more shares in a choose-1 than you would in a choose-many with the same appearance
    - [ ] This does not allow you to safely bet on multiple outcomes of a choose-1 simultaneously, though.
- [X] Add support for unlinked multimarkets
  - [ ] Now that this is done, Identify arbs in unlinked multis.
- [X] Add support for arbitrage opportunities where shares have different weights in the portfolio
- [ ] Add support for arbitrage of conditional markets (P(A|B), P(A), P(A&B))

### Other trading capabilities

- [ ] CVX-enabled kelly betting.

## General TODOs

- [ ] Track limit orders when computing arbs
- [ ] Move arb execution into portfolio.py
- [ ] Prioritize opportunities by rate of return (risk-free profit / amount spent)^(1/time to resolve)
- [ ] Account for whether existing holdings would be sold when making arb decisions
  - [ ] There may be sufficient mana for a trade where there otherwise would not be
    - [ ] When executing an arb, execute trades in order that sells existing holding first
    - [ ] Report that the mana needed is the minimum
  - [X] An arb may be more rate of return efficient or even infinite-rate-of-return if it sells existing holdings
  - [ ] Account for whether it is good to sell existing arbs to free up mana for new ones, if those new arbs make more profit than is lost by selling the old ones.
  - [X] One might account for risk of bad data entry by putting hard caps on the holdings for a particular share.
- [X] Schedule script to run regularly
- [X] Logging (could be useful if something goes horribly wrong)
- [ ] Testing
  - [ ] Test that the convex optimization is working correctly
  - [ ] Validate market states before executing
  - [ ] Test that the orders are being posted correctly
  - [ ] Validate market states after executing
  - [ ] Figure out why I sometimes get a solver error
    - [X] Or just switch solvers
- [ ] Account for risk of bad data entry
- [ ] [Rate limit better](https://pypi.org/project/ratelimit/)
  - [ ] The thing I don't like about this is that it probably doesn't persist over me terminating and re-executing my bot
- [ ] Access the api via [`manifoldpy`](https://github.com/vluzko/manifoldpy)/[`PyManifold`](https://github.com/bcongdon/PyManifold)
  - [ ] Unfortunately, `manifoldpy` looks a bit unmaintained now, so consider this a dependent issue. Frankly, what should perhaps be done is to fold much of the code here into manifoldpy.
- [X] Make `Share` hashable