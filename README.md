# montecarlo-poker

Text-based Texas Hold'em poker in Python with a Monte Carlo simulation-based AI.

## Features

- Texas Hold'em rules: pre-flop, flop, turn, river
- SB/BB rotation across rounds
- Up to 5 AI opponents
- All-in support (side pot not implemented)
- Hand evaluation: Royal Flush through High Card
- AI decision-making via Monte Carlo simulation (1000 iterations per decision)
- AI bluffing behavior with randomized action component

## How to run

```bash
python poker.py
```

Requires Python 3.10+. No external dependencies.

## How the AI works

Each AI turn, the AI runs a Monte Carlo simulation to estimate its win probability:

1. Deep copy the remaining deck and shuffle
2. Randomly complete the community cards (up to 5)
3. Randomly assign hole cards to each opponent
4. Evaluate all hands and check if the AI wins
5. Repeat 1000 times and compute win rate

The AI then uses the win rate to decide whether to raise, call, or fold:

```
win rate > 0.9  →  all-in (30% chance)
win rate > 0.7  →  raise
win rate > 0.4  →  call
win rate < 0.2  →  bluff all-in (10% chance)
otherwise       →  fold
```

A 30% random action component is layered on top to make behavior less predictable.

## Known limitations

- Side pot not implemented (all-in winner takes entire pot)
- No opponent modeling (AI does not adapt to player behavior)
- Text-based interface only

## Planned features

- [ ] Opponent modeling (track player raise/fold/call frequency)
- [ ] Web version
