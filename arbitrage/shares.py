from api import get_data_from_slug, get_data_from_marketID, post_order_binary, post_order_independent_multi
import cvxpy as cp
import functools
from constants import API_KEY


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

class Market:
    """
    A class to represent a market on Manifold.
    """

    def __init__(self, slug=None, marketId=None, preloaded_data=None):
        self.slug = slug
        self.marketId = marketId
        # Data to be obtained lazily
        self.api_data_ = preloaded_data

    @property
    def data(self):
        """Get the API data for this Market lazily."""
        if self.api_data_ is None:
            # if self.id is not None:
            #     self.api_data_ = get_data_from_id(self.id)
            if self.slug is not None:
                self.api_data_ = get_data_from_slug(self.slug)
            elif self.marketId is not None:
                self.api_data_ = get_data_from_marketID(self.marketId)
            else:
                raise ValueError("Must specify either marketId or slug")
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

    def __str__(self):
        return self.question

    def __repr__(self):
        return str(self)
    
    def post_order(self, mana_amount, outcome, limit_prob, expiration_delta=60*1000):
        """
        Post an order to the market with the given id.
        """
        return post_order_binary(self.market_id, mana_amount, outcome, limit_prob, expiration_delta=expiration_delta)


class MultiMarketAnswer:
    """
    A class to represent an answer to a multi market on Manifold.
    """

    def __init__(self, slug, answer_text):
        self.slug = slug
        self.market = Market(slug=slug)
        self.answer_text = answer_text
        # Get the first answer from self.market.data["answers"] that matches answer_text
        self.answer_data = next(answer for answer in self.market.data["answers"] if answer["text"] == answer_text)

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
    def p(self):
        return 0.5

    @property
    def pool_no(self):
        return self.answer_data["pool"]["NO"]
    
    @property
    def pool_yes(self):
        return self.answer_data["pool"]["YES"]

    def __str__(self):
        return f"{self.market.question} ({self.answer_text})"

    def __repr__(self):
        return str(self)
    
    def post_order(self, mana_amount, outcome, limit_prob, expiration_delta=60*1000):
        """
        Post an order to the market with the given id.
        """
        return post_order_independent_multi(self.market_id, self.answer_id, mana_amount, outcome, limit_prob, expiration_delta=expiration_delta)
    


class Share:
    """
    A class to represent a share of a market on Manifold.
    """

    def __init__(self, slug, answer_text=None, yes=True):
        self.yes = yes
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
    
    def __invert__(self):
        return Share(self.market.slug, answer_text=self.answer_text, yes=not self.yes)
