import random
import math

# TO DO:
# when printing card, make sure to convert 1->A, 11->J, 12->Q, and 13->K

INT_MAX = 100000

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

    owed = betHigh - prevBet
    humanAvail = human.money - owed

    if humanAvail == 0:
        return 0

    bet = input(f"How much do you want to raise (your money: {humanAvail}): ")

    if type(bet) != int:
        try:
            bet = int(bet)
            if bet < 1 or bet > humanAvail:
                print("Wrong amount of money!")
                bet = input(f"How much do you want to raise (your available money: {humanAvail}): ")
        except:
            print("Cannot convert string to int!")
            bet = input(f"How much do you want to raise (your available money: {humanAvail}): ")

    human.money -= owed + bet
    
    return bet

def raiseAI (ai, betHigh, prevBet):
    ai.callout = "raise"
    
    owed = betHigh - prevBet
    aiAvail = ai.money - owed # actually available money to raise
    
    if aiAvail == 0:
        return 0

    betRand = random.randint(1, aiAvail) # random raise

    # logical raise
    if ai.score < 5:
        bet = min(betRand, math.ceil(aiAvail/5)) # raise 1/10 of money
    elif ai.score >= 5 and ai.score < 10:
        bet = min(betRand, math.ceil(aiAvaily/3)) # raise 1/5 of money
    else:
        bet = max(betRand, math.ceil(aiAvail/2)) # raise 1/3 of money

    ai.money -= owed + bet
    
    return bet
    

def callHuman (human, betHigh, prevBet):

    owed = betHigh - prevBet
    print(f"Human owed money {owed}")

    if owed == 0:
        return betHigh

    if owed > 0 and human.money >= owed:
        # if highest bet is greater than what player bet before,
        # player needs to pay extra
        bet = owed
        human.money -= owed
    elif owed > 0 and human.money < owed:
        bet = human.money
        human.money = 0

    # if human.money >= betHigh:
    #     bet = betHigh
    # else:
    #     bet = human.money

    #human.money -= bet

    return bet

def callAI (ai, betHigh, prevBet):
    ai.callout = "call"

    owed = betHigh - prevBet
    print(f"AI owed money {owed}")

    if owed == 0:
        return betHigh
    
    if owed > 0 and ai.money >= owed:
        # if highest bet is greater than what player bet before,
        # player needs to pay extra
        bet = owed
        ai.money -= betHigh - prevBet
    elif owed > 0 and ai.money < oewd:
        bet = ai.money
        ai.money = 0

    # if ai.money >= betHigh:
    #     bet = betHigh
    # else:
    #     bet = ai.money

    #ai.money -= bet
    
    return bet


class Player:
    def __init__(self, money=100) -> None:
        self.type = ""
        self.hand = []
        self.money = money
        self.status = "p"
        self.score = 0
        # status = "p"->play, "f"->fold, "b"->bankrupt
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
                return raiseHuman(self,betHigh, prevBet)
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
    
    def action(self, community, betHigh, prevBet):
        print(f"Current AI money: {self.money}")
        if len(community) >= 3:
            cardRank = think(self, community)
        else:
            cardRank = preflopThink(self)
        myBet = -1

        # random action:
        boolRand = random.choice([1,10])
        if boolRand <= 3:
            print(f"AI rand action: {boolRand}")

            if boolRand == 1:
                myBet = self.up(betHigh, prevBet)
                callout = "raise"
            if boolRand == 2:
                # random action 2, raise only if AI has more money to raise
                if betHigh < self.money:
                    myBet = self.call(betHigh, prevBet)
                    callout = "call"
                else:
                    self.fold()
                    callout = "fold"
            if boolRand == 3:
                self.fold()
                callout = "fold"
            
            if callout == "raise":
                print(f"AI action: {self.callout} by {myBet}")
            else:
                print(f"AI action: {self.callout}")

            return myBet


        # logical action:
        if cardRank[0] <= 6: # straight or better
            myBet = self.up(betHigh, prevBet)
            callout = "raise"
        elif cardRank[0] <= 9: # one pair
            myBet = self.call(betHigh, prevBet)
            callout = "call"
        elif cardRank[0] == 10 and cardRank[1] >= 10: # high card with 10+
            myBet = self.call(betHigh, prevBet)
            callout = "call"
        else: # high card with less than 10
            self.fold()
            callout = "fold"
        
        if callout == "raise":
            print(f"AI action: {callout} by {myBet}")
        else:
            print(f"AI action: {callout}")

        return myBet

    def getScore(self, community):
        rank = 10
        if community.empty():
            rank = preflopThink(self)[0]
        rank = think(self, community)[0]
        self.score = 10 - rank
    
    def call(self, betHigh, prevBet):
        return callAI(self, betHigh, prevBet)
        
    def fold(self):
        self.status = "f"
        
    def up(self, betHigh, prevBet):
        return raiseAI(self, betHigh, prevBet)
        



def preflopThink(player):
    cards = player.hand
    cards.sort()
    if threecard(cards) != (-1, -1, -1):
        return threecard(cards)
    elif onepair(cards) != (-1, -1, -1):
        return onepair(cards)
    elif highcard(cards) != (-1, -1, -1):
        return highcard(cards)
    # at preflop stage, need to make decision based on hand


def think(player, community) -> int | int | int:
        # rank, high card, low card

        cards = player.hand + community
        cards.sort()
        # [('club', 13), ('diamond', 1), ('diamond', 2), ('diamond', 3), ('diamond', 8)]
        if royalflush(cards) != (-1, -1, -1): # (-1, -1, -1) means unable to make it
            return royalflush(cards) # if royalflush is obtained
        elif straight(cards) != (-1, -1, -1):
            return straight(cards)
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
        elif highcard(cards) != (-1, -1, -1):
            return highcard(cards)
        

def royalflush(cards) -> int | int | int:
    # Royal flush:
    symbols = [card[0] for card in cards]
    if symbols.count('club') >= 5:
        values = [card[1] for card in cards if card[0] == 'club' and \
                    (card == 1 or card == 10 or card == 11 or card == 12 or card == 13)]
        if len(values) == 5:
            return 1, -1, -1
    if symbols.count('diamond') >= 5:
        values = [card[1] for card in cards if card[0] == 'diamond' and \
                    (card == 1 or card == 10 or card == 11 or card == 12 or card == 13)]
        if len(values) == 5:
            return 1, -1, -1
    if symbols.count('heart') >= 5:
        values = [card[1] for card in cards if card[0] == 'heart' and \
                    (card == 1 or card == 10 or card == 11 or card == 12 or card == 13)]
        if len(values) == 5:
            return 1, -1, -1
    if symbols.count('spade') >= 5:
        values = [card[1] for card in cards if card[0] == 'spade' and \
                    (card == 1 or card == 10 or card == 11 or card == 12 or card == 13)]
        if len(values) == 5:
            return 1, -1, -1
    return -1, -1, -1

def straightflush(cards) -> int | int | int:
    # Straight flush:
    symbols = [card[0] for card in cards]
    if symbols.count('club') >= 5:
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
            return 2, high, -1
        elif len(values) == 7:
            if values[-1] - values[2] == 4:
                high = values[-1]
            elif values[-2] - values[1] == 4:
                high = max(values[-2], high)
            elif values[-3] - values[0] == 4:
                high = max(values[-3], high)
            return 2, high, -1
    elif symbols.count('diamond') >= 5:
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
            return 2, high, -1
        elif len(values) == 7:
            if values[-1] - values[2] == 4:
                high = values[-1]
            elif values[-2] - values[1] == 4:
                high = max(values[-2], high)
            elif values[-3] - values[0] == 4:
                high = max(values[-3], high)
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
            return 2, high, -1
        elif len(values) == 7:
            if values[-1] - values[2] == 4:
                high = values[-1]
            elif values[-2] - values[1] == 4:
                high = max(values[-2], high)
            elif values[-3] - values[0] == 4:
                high = max(values[-3], high)
            return 2, high, -1
    elif symbols.count('spade') >= 5:
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
            return 2, high, -1
        elif len(values) == 7:
            if values[-1] - values[2] == 4:
                high = values[-1]
            elif values[-2] - values[1] == 4:
                high = max(values[-2], high)
            elif values[-3] - values[0] == 4:
                high = max(values[-3], high)
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
    if symbols.count('club') == 5 or symbols.count('diamond') == 5 \
        or symbols.count('heart') == 5 or symbols.count('spade') == 5:
        return 5, -1, -1
    return -1, -1, -1

def straight(cards) -> int | int | int:
    # Straight
    values = [card[1] for card in cards]
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
    # output: small bet, big bet, pot

    print("This is initial bet for small blind")

    small = INT_MAX

    if small == INT_MAX:
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
        if card[1] == 11:
            print(f"{card[0]} J")
        elif card[1] == 12:
            print(f"{card[0]} Q")
        elif card[1] == 13:
            print(f"{card[0]} K")
        else:
            print(f"{card[0]} {card[1]}")


def showHand(player):
    if player.type == "human":
        print("Player hand:")
    else:
        print("AI hand:")
    for card in player.hand:
        if card[1] == 11:
            print(f"{card[0]} J")
        elif card[1] == 12:
            print(f"{card[0]} Q")
        elif card[1] == 13:
            print(f"{card[0]} K")
        else:
            print(f"{card[0]} {card[1]}")


def emptyHand(player):
    player.hand = []


def callAll(playerList, nAlivePlayer, community, pot):
    # make sure everyone calls
    callCnt = 0
    nAlivePlayer = len(playerList)
    betHigh = 0

    while callCnt != nAlivePlayer:
        prevBet = [0]*playerCnt
        for idx, player in enumerate(playerList):
            if player.status == "f" or callCnt == nAlivePlayer:
                prevBet[idx] = 0
                continue
            
            if player.type == "human":
                tmpBet = player.prompt(betHigh, prevBet[idx])
            else:
                tmpBet = player.action(community, betHigh, prevBet[idx])
            
            prevBet[idx] = tmpBet

            if tmpBet == betHigh:
                callCnt += 1
            else:
                if tmpBet == -1: # if folded, remove player from list
                    nAlivePlayer -= 1
                    betHigh = 0
                else: # if raised,
                    if callCnt == 0: # if raised by first player, then increase callCnt
                        callCnt += 1
                    betHigh += tmpBet
            
            pot += betHigh

    return pot, nAlivePlayer



class Person:
    def __init__(self, name, age):
        self.my_name = name
        self.age = age

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

sb = playerList[0]
bb = playerList[1]

keepPlaying = "y"
# Game start
playerCnt = len(playerList)
while keepPlaying == "y":

    if playerCnt == 1:
        print("Not enough players!\n")
        keepPlaying = "n"
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
    
    nAlivePlayer = len(playerList)
    pot, nAlivePlayer = callAll(playerList, nAlivePlayer, [], pot)

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
    while len(community) <= 5 and nAlivePlayer > 1:
        roundCnt += 1
        print(f"==================== Round {roundCnt} ====================\n")
        
        # make sure everyone called
        pot, nAlivePlayer = callAll(playerList, nAlivePlayer, community, pot)
        # callCnt = 0
        # while callCnt != nAlivePlayer:
        #     humanBet = human.prompt(betHigh)
        #     if humanBet >= betHigh and callCnt == 0:
        #         callCnt += 1
        #         betHigh = humanBet
        #     elif humanBet >= betHigh and callCnt != 0:
        #         betHigh = humanBet
        #         pass
        #     else:
        #         nAlivePlayer -= 1
        #         betHigh = 0
        #     pot += betHigh

        #     for aiPlayer in playerList[1:]:
        #         if aiPlayer.status == "p":
        #             aiBet = aiPlayer.action(community, betHigh) # if player calls or raises increase pot and decrease player.money
        #             if callCnt == 1: # only human player called or raised
        #                 if aiBet > betHigh: # if AI raised, then let human to play action
        #                     pass
        #                 elif aiBet == betHigh: # if AI called, then continue playing
        #                     callCnt += 1
        #                 else: # if AI folded, remove AI from alive player count
        #                     nAlivePlayer -= 1
        #                     betHigh = 0
        #             else:
        #                 if aiBet >= betHigh:
        #                     callCnt += 1
        #                     betHigh = aiBet
        #             betHigh = max(betHigh, aiBet)
        #             pot += betHigh
            
        print(f"Human money: {human.money}")
        for ai in playerList[1:]:
            print(f"AI money: {ai.money}")
        print(f"Pot money = {pot}")

            # for player in playerList:
            #     if player.status == "f" or player.status == "b": # Fold and Bankrupt
            #         nAlivePlayer = nAlivePlayer - 1
                # if player.cont == True:
                #     contCnt = contCnt + 1
                # elif player.cont == False:
                #     contCnt = 0

        community.append(deck.deck[0])
        deck.deck.pop(0)
        # showHand(human)
        # showCard(community)
        print(f"==================== Round {roundCnt} ====================\n")

    showHand(human)
    for aiPlayer in playerList[1:]:
        showHand(aiPlayer)
    showCard(community)

    # Find winner
    playerScore = [] # {score, high card, low card}
    for player in playerList:
        if player.status == 'p':
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
    print(f"player {finalWinnerString} won the game!")
    
    
    # Winner takes money
    playerList[finalWinner].money = playerList[finalWinner].money + pot
    
    # for i, value in enumerate(playerScore):
            

    # Remove bankrupted player
    for player in playerList:
        if player.money == 0:
            player.status = "b"
            playerList.remove(player)
    
    for player in playerList:
        if player.status != "b":
            player.status = "p"

    playerCnt = len(playerList)

    print(f"Human money: {human.money}")
    for ai in playerList[1:]:
        print(f"AI money: {ai.money}")

    keepPlaying = input("Do you want to keep playing? (y/n) ")
    while keepPlaying != "y" and keepPlaying != "n":
        print("Please input y or n")
        keepPlaying = input("Do you want to keep playing? (y/n) ")

# ai1 = AI() 
# sb = player
# bb = ai1

# listPlayer = [player, ai1]


# while True:
#     deal(player,deck)
#     deal(ai1,deck)
#     community = []
#     community = commCard(deck)
#     community = commCard(deck)
#     community = commCard(deck)
#     while len(community) <= 5 or nAlivePlayer > 1:
#         player.prompt()
#         ai1.action()
#         if len(community) != 5:
#             community = commCard(deck)



# val = input("Enter your value: ")
# print(val)
# card.deal()