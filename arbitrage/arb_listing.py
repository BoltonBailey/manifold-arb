"""
Create a list of combinations of shares that are fungible with each other, and combinations of shares that sum to at least 1.
"""

from portfolio import *

# Bitcoin highs


bitcoin_50k_2024 = { # Bitcoin hits 60k
    Share("will-bitcoin-be-at-over-50k-by-eoy"),
}
bitcoin_60k_2024 = { # Bitcoin hits 60k
    Share("will-bitcoin-reach-60000-in-2024-bf0412b0af0b"),
    Share("will-bitcoin-reach-60000-in-2024"),
    Share("will-the-price-of-bitcoin-exceed-60"),
    Share("2024-will-bitcoin-reach-60000"),
}
bitcoin_ath_2024 = { # Bitcoin hits new ATH
    Share("will-bitcoins-price-reach-alltime-h"),
    Share("will-bitcoin-reach-a-new-all-time-h"),
    Share("will-bitcoin-hit-all-time-high-in-2"),
}
bitcoin_70k_2024 = {
    Share("2024-will-bitcoin-reach-70000"),
    Share("will-bitcoin-reach-70000-in-2024"),
}
bitcoin_80k_2024 = {
    Share("2024-will-bitcoin-reach-80000"),
    Share("will-bitcoin-reach-80k-in-2024"),
    Share("will-bitcoin-price-surpass-80000-be"),
}
bitcoin_90k_2024 = {
    Share("2024-will-bitcoin-reach-90000"),
    Share("will-bitcoin-price-surpass-90000-be")
}
bitcoin_100k_2024 = {
    Share("2024-will-bitcoin-reach-100000"),
    Share("will-bitcoin-reach-100k-in-2024"),
    Share("will-bitcoin-reach-100000"),
    Share("will-bitcoin-reach-107k-in-2024"), # slug is fucked but title says 100k
    Share("will-bitcoin-reach-100000-by-the-en"),
    Share("will-bitcoin-hit-100k-before-jan-1s"),
    Share("what-will-happen-by-eoy-2024-add-re", answer_text="Bitcoin hits $100k USD")
}
bitcoin_120k_2024 = {
    Share("2024-will-bitcoin-reach-120000"),
    Share("will-bitcoin-price-hit-usd120000-be"),
}

ascending_bitcoin_high_collections = [
    bitcoin_50k_2024,
    bitcoin_60k_2024,
    bitcoin_ath_2024,
    bitcoin_70k_2024,
    bitcoin_80k_2024,
    bitcoin_90k_2024,
    bitcoin_100k_2024,
    bitcoin_120k_2024,
]

# Collections of shares that are fungible with each other
fungible_collections = [
    { # Weed rescheduled
        Share("acx-2024-will-cannabis-be-removed-f"),
        Share("will-weed-be-rescheduled-by-the-end"),
        Share("will-marijuana-be-rescheduled-by-th")
    },
    { # Biden nominated
        Share("will-biden-be-the-2024-democratic-n"),
        Share("will-biden-be-the-democratic-nomine"),
        Share("will-biden-be-the-2024-democratic-n-cccae55809bb"),
        Share("2024-predictions-matthew-yglesias-v-cdeb78933127"),
        Share("will-joe-biden-be-the-2024-democrat"),
        Share("if-joe-biden-runs-for-the-2024-demo"), # Now the same as the above
        ~Share("will-biden-still-be-the-likely-cand"),
    },
    { # Biden wins
        Share("will-joe-biden-win-the-2024-us-pres"),
        Share("will-joe-biden-be-reelected-in-2024"),
        Share("will-joe-biden-win-the-2024-us-pres-8952413770dd"),
        Share("will-joe-biden-be-reelected-in-2024-332847ff192c"),
    },
    { # Trump nominated
        Share("will-donald-trump-be-the-2024-nomin"),
        Share("will-donald-trump-be-the-2024-repub"),
        Share("will-donald-trump-be-the-republican-1120636b600a"),
        Share("will-the-gop-candidate-for-the-2024"),
        Share("will-donald-trump-be-the-gop-nomine"),
        Share("will-donald-trump-be-the-republican-d8de4615e308"),
        Share("will-donald-trump-be-the-republican")
    },
    { # Haley nominated
        Share("will-nikki-haley-be-the-2024-republ"),
        Share("will-nikki-haley-be-the-republican"),
    },
    { # Haley 2nd in iowa
        Share("will-nikki-haley-get-more-votes-tha"),
        Share("will-nikki-haley-beat-ron-desantis"),
    },
    { # Doors of Stone released
        Share("will-there-kingkiller-chronicles-be"),
        Share("will-patrick-rothfuss-release-doors"),
    },
    { # Ethereum has lowest volatility year 2024
        ~Share("will-ethusd-be-more-volatile-over-2-203743eb419d"),
        Share("will-2024-be-ethereums-lowestvolati"),
    },
    { # Bitcoin dominance reaches 60%
        Share("will-bitcoin-dominance-reach-60-or"),
        Share("2024-will-bitcoin-dominance-reach-6"),
    },
    { # GPT5 by 2025
        Share("gpt5-by-2025"),
        Share("will-gpt5-be-released-before-2025"),
        Share("will-gpt5-launch-before-1-january-2"),
    },
    { # NH wins POTUS
        Share("will-the-candidate-who-wins-new-ham"),
        Share("will-the-winner-of-the-2024-preside-445a123e528c"),
    },
    { # Bitcoin ATH before halving
        Share("will-bitcoin-btc-reach-a-new-all-ti"),
        Share("new-bitcoin-alltimehigh-ath-before"),
    }
]

fungible_collections.extend(ascending_bitcoin_high_collections)


# Collections of markets that sum to at least 1
complimentary_collections = [
    [
        Share("will-bitcoin-hit-100k-before-it-nex"),
        Share("will-bitcoin-reach-10k-before-it-re")
    ],
    [
        Share("will-an-ai-get-gold-on-any-internat"),
        Share("will-ai-first-get-imo-gold-in-2026"),
        Share("will-an-ai-win-a-gold-medal-on-the", yes=False)
    ],
    [
        ~Share("will-either-joe-biden-or-donald-tru"),
        Share("will-joe-biden-win-the-2024-us-pres"),
        Share("will-donald-trump-win-the-2024-pres")
    ]
]

for c1, c2 in zip(ascending_bitcoin_high_collections, ascending_bitcoin_high_collections[1:]):
    for s1 in c1:
        for s2 in c2:
            complimentary_collections.append([s1, ~s2])

# For every pair of distinct elements in any fungible collection, add a complimentary collection between them
for collection in fungible_collections:
    for share1 in collection:
        for share2 in collection:
            if share1 == share2:
                continue
            complimentary_collections.append([share1, ~share2])


complimentary_collections = [Portfolio(collection) for collection in complimentary_collections]