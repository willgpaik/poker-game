import random
import math
import copy

# TO DO:

INT_MAX = 100000

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
        # value = range(2,11)
        value = range(1,14)
        for i in suit:
            # self.deck.append({{i}, A})
            for j in value:
                self.deck.append((i,j))
            # self.deck.append({{i}, 'J'})
            # self.deck.append({{i}, 'Q'})
            # self.deck.append({{i}, 'K'})
        self.shuffle()

    def __str__(self) -> str:
        return f'{self.deck}'

    def shuffle(self):
        random.shuffle(self.deck)

# card = Card()
# print(card)

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

    betRand = random.randint(1, aiAvail) # random raise

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
    print(f"Human owed money {owed}")

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
    print(f"AI owed money {owed}")

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
        #self.cont = False # if call or fold or bankrupt -> True

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
        callout = ""
    
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
                    #self.money = 0
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
            #self.money = 0
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
    cards = player.hand
    cards.sort()
    if threecard(cards) != (-1, -1, -1):
        return threecard(cards)
    elif onepair(cards) != (-1, -1, -1):
        return onepair(cards)
    else:
        return highcard(cards)
    # at preflop stage, need to make decision based on hand


def think(player, community) -> int | int | int:
        # rank, high card, low card

        cards = player.hand + community
        cards.sort()
        # [('club', 13), ('diamond', 1), ('diamond', 2), ('diamond', 3), ('diamond', 8)]
        if royalflush(cards) != (-1, -1, -1): # (-1, -1, -1) means unable to make it
            return royalflush(cards) # if royalflush is obtained
        elif straightflush(cards) != (-1, -1, -1):
            return straightflush(cards)
        elif fourcard(cards) != (-1, -1, -1):
            return fourcard(cards)
        elif fullhouse(cards) != (-1, -1, -1):
            return fullhouse(cards)
        elif flush(cards) != (-1, -1, -1):
            return flush(cards)
        elif straight(cards) != (-1, -1, -1):
            return straight(cards)
        elif threecard(cards) != (-1, -1, -1):
            return threecard(cards)
        elif twopair(cards) != (-1, -1, -1):
            return twopair(cards)
        elif onepair(cards) != (-1, -1, -1):
            return onepair(cards)
        #elif highcard(cards) != (-1, -1, -1):
        else:
            return highcard(cards)
        

def royalflush(cards) -> int | int | int:
    # Royal flush:
    symbols = [card[0] for card in cards]
    if symbols.count('club') >= 5:
        values = [card[1] for card in cards if card[0] == 'club' and \
                    (card[1] == 1 or card[1] == 10 or card[1] == 11 or card[1] == 12 or card[1] == 13)]
        if len(values) == 5:
            return 1, -1, -1
    if symbols.count('diamond') >= 5:
        values = [card[1] for card in cards if card[0] == 'diamond' and \
                    (card[1] == 1 or card[1] == 10 or card[1] == 11 or card[1] == 12 or card[1] == 13)]
        if len(values) == 5:
            return 1, -1, -1
    if symbols.count('heart') >= 5:
        values = [card[1] for card in cards if card[0] == 'heart' and \
                    (card[1] == 1 or card[1] == 10 or card[1] == 11 or card[1] == 12 or card[1] == 13)]
        if len(values) == 5:
            return 1, -1, -1
    if symbols.count('spade') >= 5:
        values = [card[1] for card in cards if card[0] == 'spade' and \
                    (card[1] == 1 or card[1] == 10 or card[1] == 11 or card[1] == 12 or card[1] == 13)]
        if len(values) == 5:
            return 1, -1, -1
    return -1, -1, -1

def straightflush(cards) -> int | int | int:
    # Straight flush:
    symbols = [card[0] for card in cards]
    if symbols.count('club') >= 5:
        values = [card[1] for card in cards if card[0] == 'club']
        high = -1 # highest card value
        if len(values) == 5:
            if values[-1] - values[0] == 4:
                return 2, values[-1], -1
        elif len(values) == 6:
            if values[-1] - values[1] == 4:
                high = values[-1]
            elif values[-2] - values[0] == 4:
                high = max(values[-2], high)
            if high != -1:
                return 2, high, -1
        elif len(values) == 7:
            if values[-1] - values[2] == 4:
                high = values[-1]
            elif values[-2] - values[1] == 4:
                high = max(values[-2], high)
            elif values[-3] - values[0] == 4:
                high = max(values[-3], high)
            if high != -1:
                return 2, high, -1
    elif symbols.count('diamond') >= 5:
        values = [card[1] for card in cards if card[0] == 'diamond']
        high = -1 # highest card value
        if len(values) == 5:
            if values[-1] - values[0] == 4:
                return 2, values[-1], -1
        elif len(values) == 6:
            if values[-1] - values[1] == 4:
                high = values[-1]
            elif values[-2] - values[0] == 4:
                high = max(values[-2], high)
            if high != -1:
                return 2, high, -1
        elif len(values) == 7:
            if values[-1] - values[2] == 4:
                high = values[-1]
            elif values[-2] - values[1] == 4:
                high = max(values[-2], high)
            elif values[-3] - values[0] == 4:
                high = max(values[-3], high)
            if high != -1:
                return 2, high, -1
    elif symbols.count('heart') >= 5:
        values = [card[1] for card in cards if card[0] == 'heart']
        high = -1 # highest card value
        if len(values) == 5:
            if values[-1] - values[0] == 4:
                return 2, values[-1], -1
        elif len(values) == 6:
            if values[-1] - values[1] == 4:
                high = values[-1]
            elif values[-2] - values[0] == 4:
                high = max(values[-2], high)
            if high != -1:
                return 2, high, -1
        elif len(values) == 7:
            if values[-1] - values[2] == 4:
                high = values[-1]
            elif values[-2] - values[1] == 4:
                high = max(values[-2], high)
            elif values[-3] - values[0] == 4:
                high = max(values[-3], high)
            if high != -1:
                return 2, high, -1
    elif symbols.count('spade') >= 5:
        values = [card[1] for card in cards if card[0] == 'spade']
        high = -1 # highest card value
        if len(values) == 5:
            if values[-1] - values[0] == 4:
                return 2, values[-1], -1
        elif len(values) == 6:
            if values[-1] - values[1] == 4:
                high = values[-1]
            elif values[-2] - values[0] == 4:
                high = max(values[-2], high)
            if high != -1:
                return 2, high, -1
        elif len(values) == 7:
            if values[-1] - values[2] == 4:
                high = values[-1]
            elif values[-2] - values[1] == 4:
                high = max(values[-2], high)
            elif values[-3] - values[0] == 4:
                high = max(values[-3], high)
            if high != -1:
                return 2, high, -1
    return -1, -1, -1
                
def fourcard(cards) -> int | int | int:
    # Four cards:
    values = [card[1] for card in cards]
    for value in values:
        if values.count(value) == 4:
            return 3, value, -1
    return -1,-1, -1

def fullhouse(cards) -> int | int | int:
    # Full house
    two = 0
    three = 0
    values = [card[1] for card in cards]
    for value in values:
        if values.count(value) == 3:
            three = value
            if value > three:
                two = three
                three = value
        if values.count(value) == 2:
            two = value
    if three != 0 and two != 0:
        return 4, three, -1
    return -1, -1, -1

def flush(cards) -> int | int | int:
    # Flush
    symbols = [card[0] for card in cards]
    if symbols.count('club') >= 5 or symbols.count('diamond') >= 5 \
        or symbols.count('heart') >= 5 or symbols.count('spade') >= 5:
        return 5, -1, -1
    return -1, -1, -1

def straight(cards) -> int | int | int:
    # Straight
    values = sorted(set(card[1] for card in cards))
    prev = values[0]
    cnt = 1
    for value in values[1:]:
        if value == prev + 1:
            cnt = cnt + 1
        else:
            cnt = 1
        if cnt == 5:
            return 6, value, -1
        prev = value
    return -1, -1, -1

def threecard(cards) -> int | int | int:
    # Three cards
    values = [card[1] for card in cards]
    three = 0
    for value in values:
        if values.count(value) == 3:
            three = max(three, value)
    if three != 0:
        return 7, three, -1
    return -1, -1, -1

def twopair(cards) -> int | int | int:
    # Two pair
    values = [card[1] for card in cards]
    pairs = []
    for value in values:
        if values.count(value) == 2:
            if value not in pairs:
                pairs.append(value)
    
    if len(pairs) >= 2:
        pairs.sort()
        high = pairs[-1]
        low = pairs[-2]
        return 8, high, low # if players have same high cards, compare low cards
    return -1, -1, -1
            
def onepair(cards) -> int | int | int:
    # One pair
    values = [card[1] for card in cards]
    for value in values:
        if values.count(value) == 2:
            return 9, value, -1
    return -1, -1, -1

def highcard(cards) -> int | int | int:
        # High card
        values = [card[1] for card in cards]
        high = max(values)
        return 10, high, -1
            




# [2] 3 5 8 10

# cnt = 1
# prev = value



# [c3 d3 h3] [c5 d5] [h10 s10]
# [c3 d3 h3] [c5 d5 h5] s2


# heart: [[3, 4, 5, 6, 8], 1, 2] -> [1 2 3 4 5 6 8] -> 2-6
# spade: [[3, 4, 5, 6, 8], 7, 9] -> [3 4 5 6 7 8 9] -> 5-9


def deal(player, card):
    for i in range(2):
        player.hand.append(card.deck[0])
        card.deck.pop(0)

def initBet(sb, bb, pot) -> int | int | int:
    # output: small blind, big blind, pot

    print("This is initial bet for small blind")

    small = input(f"How much do you want to bet (input 1-{sb.money}): ")

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

def compareHands(playerList, winnerIdx):
    
    highIdx = 0
    highScore = 0
    
    for idx in winnerIdx:
        score = playerList[idx].score
        if score > highScore:
            highScore = score
            highIdx = idx

    return highIdx



def showCard(community):
    # show all community cards    

    print("Community cards:")
    for card in community:
        suit = SUITS[card[0]]
        value = FACE_CARDS.get(card[1], card[1])
        #print(f"{card[0]} {value}")
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
        #print(f"{card[0]} {value}")
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
            





def main():
    # MAIN
    #     class Card
    #     class Player
    #     class AI
    #     sb, bb
    #     loop:
    #         set Player.hand
    #     3 CC    
    #     loop:
    #         action
    #         CC (if loop cnt < 3)

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


    playerList = [human]
    for i in range(0, nAI):
        playerList.append(AI())

    sbOrder = 0


    keepPlaying = 'y'
    # Game start
#    playerCnt = len(playerList)
    while keepPlaying == 'y':
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
        showHand(playerList[1])

        # Pre-flop
        for player in playerList[2:]:
            pass # if player calls or raises increase pot and decrease player.money
        
        nAlivePlayer = sum(1 for p in playerList if (p.status == 'p' or p.status == 'a'))
        initBets = {
                playerList.index(sb): small,
                playerList.index(bb): big
                }
        pot, nAlivePlayer = callAll(playerList, [], pot, deck, nAlivePlayer, betHigh=big, initBets=initBets)

        # playerList[0].prompt(big)

        # if len(playerList) == 2 and playerList[0].status == "f":
        #     print(f"player AI player1 won the game!")
        #     # Winner takes money
        #     playerList[1].money = playerList[1].money + pot
        #     for player in playerList:
        #         if player.status != "b":
        #             player.status = "p"
        #     continue
        # playerList[1].action([], big)

        # Flop
        community = []
        community.append(deck.deck[0])
        deck.deck.pop(0)
        community.append(deck.deck[0])
        deck.deck.pop(0)
        community.append(deck.deck[0])
        deck.deck.pop(0)

        showCard(community)

        # nAlivePlayer = 0
        # for player in playerList:
        #     if player.status == "p":
        #         nAlivePlayer = nAlivePlayer + 1

        print(f"Human money: {human.money}")
        for ai in playerList[1:]:
            print(f"AI money: {ai.money}")
        print(f"Pot money = {pot}")

        
        # Round
        roundCnt = 0
        while len(community) < 5 and nAlivePlayer > 1:
            roundCnt += 1
            print(f"==================== Round {roundCnt} ====================\n")
            
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
            finalWinner = compareHands(playerList, winnerIdx)
        
        if finalWinner == 0:
            finalWinnerString = "Human player"
        else:
            finalWinnerString = "AI player " + str(finalWinner)
        winningHand = HAND_RANK[winningScore]
        print(f"player {finalWinnerString} won the game with {winningHand}!")
        
        
        # Winner takes money
        playerList[finalWinner].money = playerList[finalWinner].money + pot
        
        # for i, value in enumerate(playerScore):
                

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
