# pysweeper
Minesweeper... on native Python (using `tkinter`)  
Note: IEDs = Mines

# Requirements
Just native Python 3.5+ should do (due to type hinting)
(Tested on Python 3.6 and 3.7)

# How to use
1. Exec run.py from root (`python run.py`), or...  
2. Run main.py as module (`python -m pyms.main`)

# Instruction
There are two main modes, each comes with three sub levels:
1. Normal modes which mimic typical minesweeper
2. Blackjack modes which assigns a card value (like blackjack) to each mine

## Normal mode
Just like typical minesweeper:

1. Left click to any cell,  
2. Right click (or keyboard `1`) to flag cell,  
3. Both click to reveal adjacent 8 cells if the correct flagged.  

## Blackjack mode
Changes from Normal mode:

1. Mid clicking mouse wheel (`Mouse2`) will allow users to confirm if the flagged value is correct.  
    - Read on for more info

2. Right click to cycle through flags of 0-10.  
3. Keyboard bindings: The 3x4 area of 123qweasdzxc are mapped accordingly to the card values, i.e.:

    1 = 1, 2 = 2, 3 = 3
    q = 4, w = 5, e = 6
    a = 7, s = 8, d = 9
    z, x, c = 10

Numpads and numbers are mapped as well, with 1 = 1, 2 = 2... and 0 = 10.

4. Each mine is now assigned a value from 1-10, much like cards in blackjack.  
5. The clues shown are the `sum` of the card values in adjacent cells.

For example, provided `□` represents empty cells, and `#`s represent card values:

    □ a 2
    c b 10
    □ 3 □

- clue `a` will show as `12`  
- clue `b` will show as `15`  
- clue `c` will show as `3`

6. Allow `hits` (revealing of a valued mine) of up to `21` total points, depending on the `Hits` option selected:  
    - **Disallow hits**: revealing *any* mine will be game over, much like normal mode.  
    - **Allow Hits on guesses only**: use mid-click on unopened cells to guess if the flagged value is correct.  
        - if flag value matches, the guess is safe (marked blue)  
        - if flag value doesn't match, but is a mine, it counts as a hit (follows any hits condition, see next section)  
        - if cell is not a mine, immediate game over.  
    - **Allow Hits on any clicks**: left clicks on mine will count as a hit.  If a mid-click is employed, the above logic follows.

The more restrictive the mode, with less gueses and less hits, the better the highscore.

7. Includes two helpful hint system (which can be disabled for higher scores):
    - **Mouseover Hints**: Calculate the flagged values on the hovered cell to show remaining flags required to match total.  
    - **Flags Tracker**: Track how many flags have been used, and which values have been hit or guessed.

# TODOs (in no particular order)
1. Custom mode to select grid size and rate/amount  
2. UI hints when # of flags don't match  
3. UI tests to see how fonts/etc behave on different systems  
4. UI enhancements, e.g. image instead of text, alignments, etc.  
5. ... add comments... (in progress)  
6. Highscores  
7. Balancing on number mode (more tests...)  
8. Add help popup to explain bindings, game modes, etc.

## Cleared TODOs:
1. Identify false flags  
2. First click no longer explodes  
3. Some UI enhancement to update the visual  
4. Blackjack-ish mode!  
5. Added number hints with mouse over  
6. Added number hints for flags  
7. Options to disable hints  
8. Confirm numbered flags to lock (will fail if flagged value not match)  
9. Added handling for updating hinter with locked/hit numbers as well  
10. Changed f-strings to `format` to support lower versions.  
11. Added seeding - possibility to use seed to generate field.  
12. Separated "hits" option to three - Disallow hits, allow hits on guesses, allow any hits.  

## Fixes:
1. Fixed a potential issue if first click is flagged it would still trigger a `set_IEDs`.  
2. Fixed an issue with `set_IEDs` being triggered more than once which interferes with seeds.  

# Other features to consider
1. Blackjack (Somewhat different from original intent, but it's there!)  
2. And hookers (I have no idea)
