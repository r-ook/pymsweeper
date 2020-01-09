# pysweeper
Minesweeper... on native Python (using `tkinter`)

# Requirements
Just native Python 3 should do.
Tested on Python 3.6+, but should work on lower versions as well.

# TODOs (in no particular order)
1.) Custom mode to select grid size and rate/amount  
2.) UI hints when # of flags don't match  
3.) UI tests to see how fonts/etc behave on different systems  
4.) UI enhancements, e.g. image instead of text, alignments, etc.  
5.) ... add comments... (in progress)  
6.) Highscores  
7.) Balancing on number mode (more tests...)  
8.) Add help popup to explain bindings, game modes, etc.

# Cleared TODOs:
1.) Identify false flags  
2.) First click no longer explodes  
3.) Some UI enhancement to update the visual  
4.) Blackjack-ish mode!  
5.) Added number hints with mouse over  
6.) Added number hints for flags  
7.) Options to disable hints  
8.) Confirm numbered flags to lock (will fail if flagged value not match)  
9.) Added handling for updating hinter with locked/hit numbers as well  
10.) Changed f-strings to `format` to support lower versions.

# Fixes:
1.) Fixed a potential issue if first click is flagged it would still trigger a `set_IEDs`

# Other features to consider
1.) Blackjack (Somewhat different from original intent, but it's there!)  
2.) And hookers
