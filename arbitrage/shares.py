from api import get_data_from_slug, get_data_from_marketID, post_order_binary, post_order_independent_multi
import cvxpy as cp
from constants import API_KEY
import json
import time

# Example json 
# {
# "id": "7saOUy7MabAtKEBq5rvg",
# "creatorId": "uyzAXSRdCCUWs4KstCLq2GfzAip2",
# "creatorUsername": "BoltonBailey",
# "creatorName": "Bolton Bailey",
# "createdTime": 1681579690313,
# "creatorAvatarUrl": "https://firebasestorage.googleapis.com/v0/b/mantic-markets.appspot.com/o/user-images%2FBoltonBailey%2Fsandpile.gif?alt=media&token=0ee5d4ad-984f-439d-a636-412c606f9103",
# "closeTime": 2258427540000,
# "question": "Will Bitcoin hit $100k before it next hits $10k?",
# "slug": "will-bitcoin-hit-100k-before-it-nex",
# "url": "https://manifold.markets/BoltonBailey/will-bitcoin-hit-100k-before-it-nex",
# "pool": {
# "NO": 793.1264716510092,
# "YES": 437.8014737450576
# },
# "probability": 0.65,
# "p": 0.5062051978411725,
# "totalLiquidity": 590,
# "outcomeType": "BINARY",
# "mechanism": "cpmm-1",
# "volume": 5075.228579312481,
# "volume24Hours": 20,
# "isResolved": false,
# "uniqueBettorCount": 33,
# "lastUpdatedTime": 1704501647450,
# "lastBetTime": 1704501647294,
# "lastCommentTime": 1687384580490,
# "description": {
# "type": "doc",
# "content": [
# {
# "type": "paragraph"
# }
# ]
# },
# "coverImageUrl": "https://firebasestorage.googleapis.com/v0/b/mantic-markets.appspot.com/o/dream%2FE_OSwypAVZ.png?alt=media&token=85e5cdb9-c322-434a-9de1-ed42eb912d1c",
# "groupSlugs": [
# "crypto-prices",
# "bitcoin"
# ],
# "textDescription": ""
# }

def maniswap_prob_from_pool(pool_yes, pool_no, p):
    """
    Calculate the probability of a maniswap market with the given pool sizes and price.
    """
    return (pool_no * p / (pool_yes * (1-p) + pool_no * p))


class InfoState:
    """
    A class to represent the state of a market/multimarket answer on Manifold.

    Includes the following properties:
    Amount of mana in the YES pool
    Amount of mana in the NO pool
    p (amm weight parameter)
    """

    def __init__(self, pool_yes, pool_no, p):
        self.pool_yes = pool_yes
        self.pool_no = pool_no
        self.p = p

    def __str__(self):
        return f"InfoState(pool_yes={self.pool_yes}, pool_no={self.pool_no}, p={self.p})"
    
    def __repr__(self):
        return str(self)
    
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, InfoState):
            return False
        return self.pool_yes == __value.pool_yes and self.pool_no == __value.pool_no and self.p == __value.p
    
    def __hash__(self) -> int:
        return hash((self.pool_yes, self.pool_no, self.p))
    
    @property
    def invariant(self):
        return self.pool_yes ** self.p * self.pool_no ** (1 - self.p)
    
    @property
    def prob(self):
        return maniswap_prob_from_pool(self.pool_yes, self.pool_no, self.p)
    
    def new_state_from_buy(self, amount, yes):
        """
        Simulates spending amount mana to buy yes (or no) shares.

        Returns new InfoState.
        """
        if yes:
            pool_no = self.pool_no + amount
            pool_yes = (self.invariant / pool_no ** (1 - self.p)) ** (1/self.p)
        else:
            pool_yes = self.pool_yes + amount
            pool_no = (self.invariant / pool_yes ** self.p) ** (1/(1-self.p))
        
        return InfoState(pool_yes, pool_no, self.p)
    
    def shares_received_from_buy(self, amount, yes):
        """
        Simulates spending amount mana to buy yes (or no) shares.

        Returns new InfoState.
        """
        
        new_state = self.new_state_from_buy(amount, yes)
        if yes:
            return self.pool_yes - new_state.pool_yes + amount
        else:
            return self.pool_no - new_state.pool_no + amount


class Market:
    """
    A class to represent a market on Manifold.
    """

    def __init__(self, slug=None, marketId=None):
        self.slug = slug
        self.marketId = marketId
        # Data to be obtained lazily
        # self.api_data_ = preloaded_data

    @property
    def data(self):
        """Get the API data for this Market lazily."""

        if self.slug is not None:
            self.api_data_ = get_data_from_slug(self.slug)
        elif self.marketId is not None:
            self.api_data_ = get_data_from_marketID(self.marketId)
        else:
            raise ValueError("Must specify either marketId or slug")
        
        if self.api_data_ == []:
            print(json.dumps(self.api_data_, indent=4))
            raise ValueError("API data empty")
        
        self.slug = self.api_data_["slug"]
        self.marketId = self.api_data_["id"]
        return self.api_data_

    @property
    def id(self):
        return self.data["id"]
    
    @property
    def market_id(self):
        return self.id

    def refresh(self):
        """ Re-request the market state from the API."""
        # TODO clear data from the cache in api.py
        self.api_data_ = None
        pass
    
    @property
    def creatorId(self):
        return self.data["creatorId"]
    
    @property
    def creatorUsername(self):
        return self.data["creatorUsername"]
    
    @property
    def creatorName(self):
        return self.data["creatorName"]
    
    @property
    def createdTime(self):
        return self.data["createdTime"]

    @property
    def price(self):
        return self.data["probability"]
        
    @property
    def question(self):
        return self.data["question"]
    
    @property
    def url(self):
        return self.data["url"]

    @property
    def p(self):
        return self.data["p"]
    
    @property
    def pool_yes(self):
        return self.data["pool"]["YES"]
    
    @property
    def pool_no(self):
        return self.data["pool"]["NO"]
    
    @property
    def probability(self):
        return self.data["probability"]
    
    @property
    def outcomeType(self):
        return self.data["outcomeType"]
    
    @property
    def closeTime(self):
        return self.data["closeTime"]
    
    @property
    def isResolved(self):
        return self.data["isResolved"]
    
    @property
    def isClosed(self):
        return self.isResolved or self.closeTime < time.time() * 1000
    
    def current_state(self):
        return InfoState(self.pool_yes, self.pool_no, self.p)

    def __str__(self):
        return self.question

    def __repr__(self):
        return str(self)
    
    def post_order(self, mana_amount, outcome, limit_prob, expiration_delta=60*1000):
        """
        Post an order to the market with the given id.
        """
        # TODO do more validation on the state of the market before and  after the trade, making sure that the api call outpus are consistent with each other and that you get the expected result
        return post_order_binary(self.market_id, mana_amount, outcome, limit_prob, expiration_delta=expiration_delta)


class MultiMarketAnswer:
    """
    A class to represent an answer to a multi market on Manifold.
    """

    def __init__(self, slug, answer_text):
        self.slug = slug
        self.market = Market(slug=slug)
        self.answer_text = answer_text



    def refresh(self):
        """ Re-request the market state from the API."""
        self.market.refresh()

    @property
    def answer_data(self):
        # Get the first answer from self.market.data["answers"] that matches answer_text
        answers_texts = [answer["text"] for answer in self.market.data["answers"]]
        answers_with_text = [answer["text"] for answer in self.market.data["answers"] if answer["text"] == self.answer_text]
        if len(answers_with_text) == 0:
            print("Found answers", answers_texts)
            raise ValueError(f"No answer with text {self.answer_text} found in market {self.slug}")
        return next(answer for answer in self.market.data["answers"] if answer["text"] == self.answer_text)

    @property
    def market_id(self):
        return self.market.id
    
    @property
    def answer_id(self):
        return self.answer_data["id"]
    
    @property
    def question(self):
        return f"{self.market.question} ({self.answer_text})"
    
    @property
    def url(self):
        return self.market.url
    
    @property
    def probability(self):
        return self.answer_data["probability"]

    @property
    def p(self):
        return 0.5

    @property
    def pool_no(self):
        return self.answer_data["pool"]["NO"]
    
    @property
    def pool_yes(self):
        return self.answer_data["pool"]["YES"]
    
    @property
    def isClosed(self):
        return self.market.isClosed
    
    def current_state(self):
        return InfoState(self.pool_yes, self.pool_no, self.p)

    def __str__(self):
        return f"{self.market.question} ({self.answer_text})"

    def __repr__(self):
        return str(self)
    
    def post_order(self, mana_amount, outcome, limit_prob, expiration_delta=60*1000):
        """p
        Post an order to the market with the given id.
        """
        return post_order_independent_multi(self.market_id, self.answer_id, mana_amount, outcome, limit_prob, expiration_delta=expiration_delta)
    


class Share:
    """
    A class to represent a share of a market on Manifold.
    """

    def __init__(self, slug, answer_text=None, yes=True):
        self.yes = yes
        self.slug = slug
        if answer_text is None:
            self.market = Market(slug=slug)
        else:
            self.market = MultiMarketAnswer(slug=slug, answer_text=answer_text)
        self.answer_text = answer_text


    def refresh(self):
        """ Re-request the market state from the API."""
        self.market.refresh()

    def __str__(self):
        if self.yes:
            return f"{self.market.question} (YES)"
        else:
            return f"{self.market.question} (NO)"

    def __repr__(self):
        return str(self)
    
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Share):
            return False
        return self.market.market_id == __value.market.market_id and self.answer_text == __value.answer_text and self.yes == __value.yes
    
    def __hash__(self) -> int:
        return hash((self.slug, self.answer_text, self.yes))
    
    def __invert__(self):
        return Share(self.slug, answer_text=self.answer_text, yes=not self.yes)
    
    def marginal_price(self):
        """
        Calculate the marginal price of buying a share.
        """
        return self.market.probability if self.yes else 1 - self.market.probability

    def post_order(self, mana_amount, limit_prob, expiration_delta=60*1000):

        assert(self.market.isClosed == False)

        return self.market.post_order(mana_amount, "YES" if self.yes else "NO", limit_prob, expiration_delta=expiration_delta)