# montecarlo-poker
# Texas Hold'em poker with Monte Carlo simulation-based AI
# Author: Ghanghoon Paik
# License: MIT
# https://github.com/willgpaik/montecarlo-poker

import random
import math
import copy
from collections import Counter

SUITS = {'spade': '♠', 'heart': '♥', 'diamond': '♦', 'club': '♣'}
FACE_CARDS = {1: "A", 11: "J", 12: "Q", 13: "K"}
HAND_RANK = {
    1: "Royal Flush",
    2: "Straight Flush", 
    3: "Four of a Kind",
    4: "Full House",
    5: "Flush",
    6: "Straight",
    7: "Three of a Kind",
    8: "Two Pair",
    9: "One Pair",
    10: "High Card"
}

#random.seed(100)

class Card:
    def __init__(self):
        self.deck = []
        suit = ['spade', 'club', 'diamond', 'heart']
        value = range(1,14)
        for i in suit:
            for j in value:
                self.deck.append((i,j))
        self.shuffle()

    def __str__(self) -> str:
        return f'{self.deck}'

    def shuffle(self):
        random.shuffle(self.deck)

def raiseHuman (human, betHigh, prevBet):
    # function returns how much human player will raise

    owed = betHigh - prevBet
    humanAvail = human.money - owed

    if humanAvail <= 0:
        # if human player has not enough money to raise
        return 0

    try:
        bet = int(input(f"How much do you want to raise (available: {humanAvail}): "))
        if bet < 1 or bet > humanAvail:
            print(f"Wrong amount! input 1-{humanAvail}")
            return raiseHuman(human, betHigh, prevBet)  # retry
    except:
        print("Please enter a number!")
        return raiseHuman(human, betHigh, prevBet)  # retry

    # returns player owed to continue play + amount human player wants to raise
    return owed + bet

def raiseAI (ai, betHigh, prevBet, winRate):
    # function returns how much AI player will raise
    ai.callout = "raise"
    
    owed = betHigh - prevBet
    aiAvail = ai.money - owed # actually available money to raise
    
    if aiAvail <= 0:
        # if AI player has not enough money to raise
        return 0

    # raise based on the winRate
    if winRate > 0.8:
        bet = math.ceil(aiAvail * 0.5) # raise 1/5 of money
    elif winRate > 0.6:
        bet = math.ceil(aiAvail * 0.3) # raise 1/3 of money
    else:
        bet = math.ceil(aiAvail * 0.1) # raise 1/2 of money

    # adding randomness
    bet = max(1, bet + random.randint(-math.ceil(bet*0.2), math.ceil(bet*0.2)))
    bet = min(bet, aiAvail) # make sure not to bet over available money

    # returns AI owed to continue play + amount AI wants to raise
    return owed + bet
    

def callHuman (human, betHigh, prevBet):
    # function returns how much human player owed to continue play

    owed = betHigh - prevBet
    # print(f"Human owed money {owed}") # debug purpose

    if owed == 0:
        # if human player owed nothing
        return 0

    if human.money >= owed:
        # if human player has enough money to call
        return owed
    else:
        # if human player doesn't have enough money to call
        return human.money # all-in

def callAI (ai, betHigh, prevBet):
    # function returns how much AI player owed to continue play
    ai.callout = "call"

    owed = betHigh - prevBet
    # print(f"AI owed money {owed}") # debug purpose

    if owed == 0:
        # if AI player owed nothing
        return 0
    
    if ai.money >= owed:
        # if AI player has enough money to call
        return owed
    else:
        # if AI player doesn't have enough moeny to call
        return ai.money # all-in

class Player:
    def __init__(self, money=100) -> None:
        self.type = ""
        self.hand = []
        self.money = money
        self.status = "p"
        self.score = 0
        # status = "p"->play, "f"->fold, "b"->bankrupt
        # status = "a"->all-in (side pot no implemented)

class Human(Player):
    def __init__(self, money=100) -> None:
        super().__init__(money)
        self.type = "human"

    def prompt(self, betHigh, prevBet):
        print(f"Current human money: {self.money}")
        act = ""
        while (act != "c" and act != 'f' and act != 'r'):
            act = input("What action do you want to play ('c'all, 'f'old, 'r'aise): ")
            if act == "c":
                return callHuman(self, betHigh, prevBet)
            elif act == "f":
                self.status = "f"
                return -1
            elif act == "r":
                return raiseHuman(self, betHigh, prevBet)
            else:
                print("Wrong input")
            
    
    def getScore(self, community):
        rank = think(self, community)[0]
        self.score = 10 - rank
        

class AI(Player):
    def __init__(self, money=100) -> None:
        super().__init__(money)
        self.type = "AI"
    
    def action(self, community, betHigh, prevBet, nAlivePlayer, deck, nSimulation=1000):
        print(f"Current AI money: {self.money}")
        myBet = -1

        # calculate winRate based on Monte Carlo
        winRate = simulate(nAlivePlayer, self, community, deck, nSimulation)
        
        # random action:
        if random.random() < 0.3: # 30% chance to play random action
            boolRand = random.randint(1,10)
            if boolRand <= 3:
                print(f"AI rand action: {boolRand}")

                if random.random() < 0.1: # randomly bluff
                    myBet = self.money
                    self.status = 'a'
                    callout = "all-in"
                elif boolRand == 1:
                    myBet = self.up(betHigh, prevBet, winRate)
                    callout = "raise"
                elif boolRand == 2:
                    # random action 2, raise only if AI has more money to raise
                    if betHigh < self.money:
                        myBet = self.call(betHigh, prevBet)
                        callout = "call"
                    else:
                        self.fold()
                        callout = "fold"
                else: # boolRand == 3
                    self.fold()
                    callout = "fold"

                                
                if callout == "raise" or callout == "all-in":
                    print(f"AI action: {callout} by {myBet}")
                else:
                    print(f"AI action: {callout}")

                return myBet


        # logical action:
        if winRate > 0.9 and random.random() < 0.3: # with high chance to win, all-in with 30% chance
            myBet = self.money
            self.status = 'a'
            callout = "all-in"
        elif winRate < 0.2 and random.random() < 0.1: # if chance to win is really low, bluff
            myBet = self.money
            #self.money = 0
            self.status = 'a'
            callout = "all-in"
        elif winRate > 0.7 + random.uniform(-0.4, 0.4): # more than 70% chance to win
            myBet = self.up(betHigh, prevBet, winRate)
            callout = "raise"
        elif winRate > 0.4 + random.uniform(-0.2, 0.2): # more than 40% chance to win
            myBet = self.call(betHigh, prevBet)
            callout = "call"
        else: # less than 40% chance to win
            self.fold()
            callout = "fold"
        
        if callout == "raise" or callout == "all-in":
            print(f"AI action: {callout} by {myBet}")
        else:
            print(f"AI action: {callout}")

        return myBet

    def getScore(self, community):
        rank = 10
        if not community:
            rank = preflopThink(self)[0]
        else:
            rank = think(self, community)[0]
        self.score = 10 - rank
    
    def call(self, betHigh, prevBet):
        return callAI(self, betHigh, prevBet)
        
    def fold(self):
        self.status = "f"
        
    def up(self, betHigh, prevBet, winRate):
        return raiseAI(self, betHigh, prevBet, winRate)
        



def preflopThink(player):
    return evaluate_hand(player.hand)


def think(player, community):
    return evaluate_hand(player.hand + community)

        
def evaluate_hand(cards):
    """
    Evaluate best hand from up to 7 cards.
    Returns (rank, high, low)  (lower rank is better)
 
    Rank map:
      1=Royal Flush
      2=Straight Flush
      3=Four of a Kind
      4=Full House
      5=Flush
      6=Straight
      7=Three of a Kind
      8=Two Pair
      9=One Pair
      10=High Card
    """
    val_count = Counter(card[1] for card in cards)
    suit_count = Counter(card[0] for card in cards)
    counts = sorted(val_count.values(), reverse=True)
 
    flush_suit = next((s for s, c in suit_count.items() if c >= 5), None)
 
    def find_straight(vals):
        unique = sorted(set(vals))
        best = -1
        for i in range(len(unique) - 4):
            window = unique[i:i+5]
            if window[-1] - window[0] == 4:
                best = max(best, window[-1])
        return best
 
    # Royal flush / Straight flush
    if flush_suit:
        flush_vals = [c[1] for c in cards if c[0] == flush_suit]
        if {1, 10, 11, 12, 13}.issubset(set(flush_vals)):
            return (1, -1, -1)
        sf_high = find_straight(flush_vals)
        if sf_high != -1:
            return (2, sf_high, -1)
 
    # Four of a kind
    if counts[0] == 4:
        quad = max(v for v, c in val_count.items() if c == 4)
        return (3, quad, -1)
 
    # Full house
    if counts[0] == 3 and counts[1] >= 2:
        three = max(v for v, c in val_count.items() if c == 3)
        pair = max(v for v, c in val_count.items() if c >= 2 and v != three)
        return (4, three, pair)
 
    # Flush
    if flush_suit:
        return (5, max(c[1] for c in cards if c[0] == flush_suit), -1)
 
    # Straight
    straight_high = find_straight(val_count.keys())
    if straight_high != -1:
        return (6, straight_high, -1)
 
    # Three of a kind
    if counts[0] == 3:
        three = max(v for v, c in val_count.items() if c == 3)
        return (7, three, -1)
 
    # Two pair
    pairs = sorted([v for v, c in val_count.items() if c >= 2], reverse=True)
    if len(pairs) >= 2:
        return (8, pairs[0], pairs[1])
 
    # One pair
    if len(pairs) == 1:
        return (9, pairs[0], -1)
 
    # High card
    return (10, max(val_count.keys()), -1)


def deal(player, card):
    for i in range(2):
        player.hand.append(card.deck[0])
        card.deck.pop(0)

def initBet(sb, bb, pot) -> int | int | int:
    # output: small blind, big blind, pot

    print("This is initial bet for small blind")

    if sb.type == "human":
        small = input(f"How much do you want to bet (input 1-{sb.money}): ")
    else:
        small = random.randint(1, min(10, sb.money)) # AI player will put random small amount
        print(f"AI small blind: {small}")

    while type(small) != int or small > sb.money:
        try:
            small = int(small)
            if small < 1 or small > sb.money:
                print(f"Wrong value to bet! (input 1-{sb.money})")
                small = input(f"How much do you want to bet (input 1-{sb.money}): ")
        except:
            print("Cannot convert string to int!")
            small = input(f"How much do you want to bet (input 1-{sb.money}): ")
    sb.money = sb.money - small

    if bb.money >= small*2:
        big = small*2
    else:
        big = bb.money
    bb.money = bb.money - big

    pot = small + big

    return small, big, pot

def compareHands(winnerIdx, playerScore):
    highIdx = winnerIdx[0];

    for idx in winnerIdx[1:]:
        if playerScore[idx][1] > playerScore[highIdx][1]:
            highIdx = idx
        elif playerScore[idx][1] == playerScore[highIdx][1]:
            if playerScore[idx][2] > playerScore[highIdx][2]:
                highIdx = idx

    return highIdx


def showCard(community):
    # show all community cards    

    print("Community cards:")
    for card in community:
        suit = SUITS[card[0]]
        value = FACE_CARDS.get(card[1], card[1])
        print(f"{suit}{value}", end=" ")
    print()

def showHand(player):

    if player.type == "human":
        print("Player hand:")
    else:
        print("AI hand:")

    for card in player.hand:
        suit = SUITS[card[0]]
        value = FACE_CARDS.get(card[1], card[1])
        print(f"{suit}{value}", end=" ")
    print()


def emptyHand(player):
    player.hand = []


def callAll(playerList, community, pot, deck, nAlivePlayer, betHigh=0, initBets=None):
    roundBet = [0] * len(playerList) # each player's bet for this round
    hasActed = [False] * len(playerList) # track each player's action
    if initBets:
        for idx, amount in initBets.items():
            roundBet[idx] = amount
            hasActed[idx] = True # player sb/bb already finished action

    while True:
        allCalled = True

        for idx, player in enumerate(playerList):
            if player.status != 'p':
                continue
            if hasActed[idx] and roundBet[idx] == betHigh:
                continue # if player finished action and amount it correct
            
            allCalled = False

            if player.type == "human":
                result = player.prompt(betHigh, roundBet[idx])
            else:
                result = player.action(community, betHigh, roundBet[idx], nAlivePlayer, deck, nSimulation=1000)

            hasActed[idx] = True # finished action

            if result != -1:
                roundBet[idx] += result
                player.money -= result
                if roundBet[idx] > betHigh:
                    betHigh = roundBet[idx]
                    # if a player raised, others need to make an action
                    for i in range(len(playerList)):
                        if i != idx: # except for player who raised
                            hasActed[i] = False

        
            if player.money == 0:
                player.status = 'a' # all-in

        if allCalled:
            break

    initBetsTotal = sum(initBets.values()) if initBets else 0
    pot += sum(roundBet) - initBetsTotal

    nAlivePlayer = sum(1 for p in playerList if (p.status == 'p' or p.status == 'a'))

    return pot, nAlivePlayer


def simulate(nAlivePlayer, player, community, deck, nSimulation=1000):
    # Monte Carlo based prediction of AI's winning rate
    wins = 0
    nOpp = nAlivePlayer-1

    for i in range(nSimulation):
        oppList = []

        # copy remaining deck
        remainingDeck = copy.deepcopy(deck)
        remainingDeck.shuffle()

        # complete community cards (up to 5 cards)
        simCommunity = community.copy()
        while len(simCommunity) < 5:
            card = remainingDeck.deck.pop(0)
            simCommunity.append(card)

        for idx in range(nOpp):
            oppList.append(AI())
            deal(oppList[idx], remainingDeck)

        myRank = think(player, simCommunity)[0]
        oppRank = min(think(opp, simCommunity)[0] for opp in oppList)

        if myRank <= oppRank:
            wins += 1

    return wins / nSimulation
            

def getStartMoney():
    try:
        val = int(input("Starting money per player (default 100, min 10): "))
        if val < 10:
            print("Minimum is 10. Try again.")
            return getStartMoney()
        return val
    except:
        print("Please enter a number.")
        return getStartMoney()




def main():
    deck = Card()
    human = Human()
    nAI = input("Enter number of AI: ")
    while type(nAI) != int:
        try:
            nAI = int(nAI)
            if nAI < 1 or nAI > 5:
                print("Wrong number of AI! (input 1-5)")
                nAI = input("Enter number of AI: ")
        except:
            print("Cannot convert string to int!")
            nAI = input("Enter number of AI: ")

    startMoney = getStartMoney()
    human = Human(startMoney)

    playerList = [human]
    for i in range(0, nAI):
        playerList.append(AI(startMoney))

    sbOrder = 0


    keepPlaying = 'y'

    # Game start
    while keepPlaying == 'y':
        input("\nPress Enter to start next game...")
        print("\n" + "=" * 50)
        print(f"           GAME START")
        print("=" * 50 + "\n")

        # sb/bb order
        playerCnt = len(playerList)
        sb = playerList[sbOrder % playerCnt]
        bb = playerList[(sbOrder+1) % playerCnt]
   
        deck = Card() # new deck for new game

        if playerCnt == 1:
            print("Not enough players!\n")
            keepPlaying = 'n'
            continue

        pot = 0

        small, big, pot = initBet(sb, bb, pot) # first betting sb and bb (2x sb)

        print(f"Human money: {human.money}")
        for ai in playerList[1:]:
            print(f"AI money: {ai.money}")
        print(f"Pot money = {pot}")

        for player in playerList:
            emptyHand(player)
            # deals hands
            deal(player, deck)
        
        showHand(human)
        #showHand(playerList[1]) # debug purpose

        # Pre-flop
        nAlivePlayer = sum(1 for p in playerList if (p.status == 'p' or p.status == 'a'))
        initBets = {
                playerList.index(sb): small,
                playerList.index(bb): big
                }
        pot, nAlivePlayer = callAll(playerList, [], pot, deck, nAlivePlayer, betHigh=big, initBets=initBets)

        # Flop
        community = []
        community.append(deck.deck[0])
        deck.deck.pop(0)
        community.append(deck.deck[0])
        deck.deck.pop(0)
        community.append(deck.deck[0])
        deck.deck.pop(0)

        showCard(community)

        print(f"Human money: {human.money}")
        for ai in playerList[1:]:
            print(f"AI money: {ai.money}")
        print(f"Pot money = {pot}")

        
        # Round
        roundCnt = 0
        while len(community) < 5 and nAlivePlayer > 1:
            roundCnt += 1
            print(f"\n==================== Round {roundCnt} ====================")
            
            community.append(deck.deck.pop(0))
            showCard(community)

            # make sure everyone called
            pot, nAlivePlayer = callAll(playerList, community, pot, deck, nAlivePlayer)
                
            print(f"Human money: {human.money}")
            for ai in playerList[1:]:
                print(f"AI money: {ai.money}")
            print(f"Pot money = {pot}")

            showHand(human)
            print(f"==================== Round {roundCnt} ====================\n")

        showHand(human)
        for aiPlayer in playerList[1:]:
            showHand(aiPlayer)
        showCard(community)

        # Find winner
        playerScore = [] # {score, high card, low card}
        for player in playerList:
            if player.status == 'p' or player.status == 'a':
                playerScore.append(think(player, community))
            else: # if player is not playable
                playerScore.append((100, -1, -1))
        
        winningScore = 100
        winnerCnt = 0
        winnerIdx = []
        for i in playerScore:
            if i[0] == 100:
                continue
            else:
                winningScore = min(winningScore, i[0])

        for idx, value in enumerate(playerScore):
            if value[0] == winningScore:
                winnerCnt = winnerCnt + 1
                winnerIdx.append(idx)

        if winnerCnt == 1:
            finalWinner = winnerIdx[0] # index of winning player from playerList
        else:
            finalWinner = compareHands(winnerIdx, playerScore)
        
        if finalWinner == 0:
            finalWinnerString = "Human player"
        else:
            finalWinnerString = "AI player " + str(finalWinner)
        winningHand = HAND_RANK[winningScore]
        print(f"player {finalWinnerString} won the game with {winningHand}!")
        
        
        # Winner takes money
        playerList[finalWinner].money = playerList[finalWinner].money + pot
        
        # Remove bankrupted player
        for player in playerList:
            if player.money == 0:
                player.status = 'b'
        playerList = [p for p in playerList if p.status != 'b']

        for player in playerList:
            player.status = 'p'

        playerCnt = len(playerList)

        print(f"Human money: {human.money}")
        for ai in playerList[1:]:
            print(f"AI money: {ai.money}")

        keepPlaying = input("Do you want to keep playing? (y/n) ")
        while keepPlaying != 'y' and keepPlaying != 'n':
            print("Please input y or n")
            keepPlaying = input("Do you want to keep playing? (y/n) ")

        # if human player is removed, end the game
        if human not in playerList:
            print("You are bankrupt! Game over.")
            break
    
        sbOrder = (sbOrder+1) % playerCnt



if __name__ == "__main__":
    main()
