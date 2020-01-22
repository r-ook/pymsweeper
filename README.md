# `pymsweeper`
> Oh yeah? I'm gonna build my own Minesweeper, with Blackjack, and hookers!  
> In fact, forget the hookers!

It's Minesweeper... with a dash of blackjack... running on native Python `tkinter`  

# Requirements
Just vanilla Python 3.5+ should do (due to type hinting)
(Tested on Python 3.6 and 3.7)

# How to use (3 alternatives)
1. Install `pyms` as a package (`pip install .` on package root) and run (`import pyms; pyms.run()`), or...  
2. Run as module (`python -m pyms`), or...  
3. Run `pymsweeper.pyw` as a script (`python pymsweeper.pyw`)  

# Instruction
(Note: In the GUI, *IEDs* == *Mines*)  

There are two main modes, each comes with three sub levels:
1. Normal modes which mimic typical minesweeper
2. Blackjack modes which assigns a card value (like blackjack) to each mine

## Normal mode
Just like typical minesweeper:

1. Left Click (<kbd>Mouse1</kbd>) to any cell,  
2. Right Click (<kbd>Mouse3</kbd>) (or keyboard <kbd>1</kbd>) to flag cell,  
3. Left + Right Click(<kbd>Mouse1</kbd> + <kbd>Mouse3</kbd>) to reveal adjacent 8 cells if the correct flagged.  

Option:
1. **Use Seed**: If you want to re/play a particular field, use the seed generator under option.  
    - Highscores shows the seed number from your best attempts, so that you may challenge yourself again.  
    - If the current field is generated from a seed, highscore will not be recorded.

## Blackjack mode
Changes from Normal mode:

1. Mid Click mouse wheel (<kbd>Mouse2</kbd>) will allow users to confirm if the flagged value is correct (Read on for more info).  
2. Right click to cycle through flags of `0`-`10`.  
3. Keyboard bindings: The 3x4 area of <kbd>123QWEASDZXC</kbd> are mapped accordingly to the card values, i.e.:

    <kbd>1</kbd> = `1`,  <kbd>2</kbd> = `2`,  <kbd>3</kbd> = `3`  
    <kbd>Q</kbd> = `4`,  <kbd>W</kbd> = `5`,  <kbd>E</kbd> = `6`  
    <kbd>A</kbd> = `7`,  <kbd>S</kbd> = `8`,  <kbd>D</kbd> = `9`  
    <kbd>Z</kbd> = <kbd>X</kbd> = <kbd>C</kbd> = `10`  

Numpads and numbers are mapped as well, with <kbd>4</kbd> = `4`, <kbd>5</kbd> = `5`... and <kbd>0</kbd> = `10`.

4. Each mine is now assigned a value from `1-10`, much like cards in blackjack.  
5. The clues shown are the `sum` of the card values in adjacent cells.

For example, provided `□` represents empty cells, and `#`s represent card values:

    □ a 2
    c b 10
    □ 3 □

- clue `a` will show as `12`  
- clue `b` will show as `15`  
- clue `c` will show as `3`

6. Allow *Hits* (revealing of a valued mine) of up to `21` total points, depending on the *Hits* option selected:  
    - **Disallow hits**: revealing *any* mine will be game over, much like normal mode.  
    - **Allow Hits on guesses only**: use mid-click (<kbd>Mouse2</kbd>) on unopened cells to guess if the flagged value is correct.  
        - If flag value matches, the guess is safe (marked blue)  
        - If flag value doesn't match, but is a mine, it counts as a hit (follows any hits condition, see next section)  
        - If cell is not a mine, immediate game over.  
    - **Allow Hits on any clicks**: revealing any mine will count as a hit.  If mid-click was used, the above logic follows.

The more restrictive the mode (less help), with less guesses and less hits, the better the highscore.

7. Includes two helpful hint system (which can be disabled for higher scores):
    - **Mouseover Hints**: Calculate the flagged values on the hovered cell to show remaining flags required to match total.  
    - **Flags Tracker**: Track how many flags have been used, and which values have been hit or guessed.

# TODOs (in no particular order)
1. Add comments... 
2. Clean up testing artifacts.  
3. Think of an alternative for combining unicode as it doesn't show nicely on Linux and Win7.  Windows 10 is fine.  

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
13. Highscores, finally!
14. Added more symbols for association.  
15. Highscore handling for corrupted loads.  
16. Added save handling for mode and options.  
17. Changed saving file format.  
18. Changed main run script to consoleless mode.    
19. Added basic package structure to support install and running as module.  
20. Added UI hints (change background colour) when # of flags don't match.  

## Wishlist (ranked by preference)
1. Perform more testing on ranking to see if weight assigned is fair.  
2. Add help popup to explain bindings, game modes, etc.  
3. Custom mode to select grid size and rate/amount.  
4. Balancing on number mode (more tests...)  
5. UI tests to see how fonts/etc behave on different systems.  
6. UI enhancements, e.g. image instead of text, alignments, etc.  
7. Polish the package good enough to feel good about publishing on PyPI.  

# Fixes:
1. Fixed a potential issue if first click is flagged it would still trigger a `set_IEDs`.  
2. Fixed an issue with `set_IEDs` being triggered more than once which interferes with seeds.  
3. Fixed highscore ranking as the `sort_key` was sorting it in reverse.  
4. Removed OS dependant colouring name.  
5. Renamed to be unique on PyPI if I finally feel good enough to publish this...  