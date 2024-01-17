
import spacy
from api import get_data_from_marketID, get_bets_of_user
import json
import time

BOT_USERNAMES = [
  'TenShino',
  'pos',
  'v',
  'acc',
  'jerk',
  'snap',
  'ArbitrageBot',
  'MarketManagerBot',
  'Botlab',
  'JuniorBot',
  'ManifoldDream',
  'ManifoldBugs',
  'ACXBot',
  'JamesBot',
  'RyanBot',
  'trainbot',
  'runebot',
  'LiquidityBonusBot',
  '538',
  'FairlyRandom',
  'Anatolii',
  'JeremyK',
  'Botmageddon',
  'SmartBot',
  'ShifraGazsi',
  'NiciusBot',
  'Bot',
  'Mason',
  'VersusBot',
  'GPT4',
  'EntropyBot',
  'veat',
  'ms_test',
  'arb',
  'Turbot',
  'MiraBot',
  'MetaculusBot',
  'burkebot',
  'Botflux',
  '7',
  'hyperkaehler',
  'NcyBot',
  'ithaca',
  'GigaGaussian',
  'BottieMcBotface',
  'Seldon',
  'OnePercentBot',
  'arrbit',
  'ManaMaximizer',
  'rita',
  'uhh',
  'ArkPoint',
  'EliBot',
  'manifestussy',
  'mirrorbot',
  'JakeBot',
  'loopsbot',
  'breezybot',
  'echo',
  'Sayaka',
  'cc7',
  'Yuna',
  'ManifoldLove',
  'chooterb0t',
  'bonkbot',
  'NermitBundaloy',
  'FirstBot',
  'bawt',
  'FireTheCEO',
  'JointBot',
]

nlp = spacy.load("en_core_web_md")

output = []

for username in BOT_USERNAMES:

    print(f"Getting bets for {username}")
    user_bets = get_bets_of_user(username)

    sorted_bets = sorted(user_bets, key=lambda bet: bet["createdTime"])

    for bet1, bet2 in zip(sorted_bets, sorted_bets[1:]):
        if abs(bet1["createdTime"] - bet2["createdTime"]) < 10000 and bet1["contractId"] != bet2["contractId"]:
            # Get the markets
            id1 = bet1["contractId"]
            id2 = bet2["contractId"]
            market1 = get_data_from_marketID(id1)
            market2 = get_data_from_marketID(id2)
            if market1["closeTime"] < time.time() * 1000:
                continue
            if market2["closeTime"] < time.time() * 1000:
                continue
            question1 = market1["question"]
            question2 = market2["question"]
            
            doc1 = nlp(question1)
            doc2 = nlp(question2)
            if doc1.similarity(doc2) > 0.90:
                print(f"\nMarket 1: {question1}")
                print(f"Market 2: {question2}")
                print(f"Similarity: {doc1.similarity(doc2)}")
                output.append([
                    question1,
                    question2,
                    market1["slug"],
                    market2["slug"],
                ])
                print(f"\n")
            
# Dump output to json file  
with open("arbs.json", "w") as f:
    json.dump(output, f, indent=4)

