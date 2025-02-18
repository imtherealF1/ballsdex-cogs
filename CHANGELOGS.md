# F1 BallsDex Cogs

## Changelogs

### Wednesday, 18th December 2024

1. Updated `HOWTOINSTALL.md`, added `installer.py` for both `gambling` and `battle`.

### Tuesday, 17th December 2024

1. Updated `HOWTOINSTALL.md` for `battle` and `gambling`, improved installing eval to include updating.
2. Adding draws in blackjack, and improving in `/blackjack`.
3. Fixed bug, you now can't gamble with disabled collectibles.
4. Added description to command arguments in `/roulette add`.

### Monday, 16th December 2024

1. Improved `HOWTOINSTALL.md`, made it more detailed and cleaner.

### Sunday, 15th December 2024

1. Added `battle` package:
    - `/battle begin`, to begin a battle with a user.
    - `/battle add`, to add a collectible to the deck.
    - `/battle remove`, to remove a collectible from the deck.
    - `/battle cancel`, to cancel the current battle.
2. Bug fix with `/roulette`.

### Saturday, 14th December 2024

1. Added `gambling` package:
    - `/blackjack`, to start an interactive blackjack game with an AI.
    - `/slots`, to play slots (not interactive).
    - `/roulette start`, to start a game of roulette and the user can choose whether to play alone
    or with other people.
    - `/roulette add`, to add a collectible as a bet when playing alone.
2. Created `LICENSE`, which uses the MIT License.
3. Created `README.md`.
