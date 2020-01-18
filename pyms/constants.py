from collections import namedtuple

# Mouse state constants
MOUSE_LEFT = 2 ** 8
MOUSE_MID = 2 ** 9
MOUSE_RIGHT = 2 ** 10

# Status constants
STATUS = namedtuple('STATUS', 'icon fg bg font')
STATUS_OKAY = STATUS('☺', 'black', 'gold', ('tkDefaultFont', 18, 'bold'))
STATUS_WOAH = STATUS('☹', 'black', 'orange', ('tkDefaultFont', 24, 'bold'))
STATUS_BOOM = STATUS('☠', 'white', 'red3', ('tkDefaultFont', 18, 'bold'))
STATUS_YEAH = STATUS('✌', 'white', 'limegreen', ('tkDefaultFont', 18, 'bold'))

# Mode constants
MODE_CONFIG = namedtuple('MODE_CONFIG', 'name x y rate amount special')
MODES = {
    0: MODE_CONFIG('Fresh', 8, 8, None, 10, False),
    1: MODE_CONFIG('Skilled', 16, 16, None, 40, False),
    2: MODE_CONFIG('Pro', 30, 16, None, 99, False),
    3: MODE_CONFIG('Half Deck', 12, 12, None, 52 // 2, True),
    4: MODE_CONFIG('Full Deck', 16, 16, None, 52, True),
    5: MODE_CONFIG('Double Deck', 28, 16, None, 52 * 2, True)
}

# Circled Number constants

# CIRCLED_NUMBERS = {i + 1: chr(0x2780 + i) for i in range(10)}
CIRCLED_NUMBERS = {i + 1: chr(0x2460 + i) for i in range(10)}

# NEG_CIRCLED_NUMBERS = {i + 1: chr(0x2776 + i) for i in range(10)}
NEG_CIRCLED_NUMBERS = {i + 1: chr(0x278A + i) for i in range(10)}

# Numbered clues helper config
TRACKER_CONFIG = namedtuple('TRACKER_CONFIG', 'max_check over_state tracked_num flag_state')

# Mouse over hint config
HINT = namedtuple('HINT', 'frame label counter')

# GUI Options
OPTIONS = namedtuple('OPTIONS', 'mode sound mouseover tracker allow_hits')

# Record data to support record class (follows order to be shown in highscore)
RECORD = namedtuple('RECORD',
            '''
            time_val
            seed
            time_str
            IED_guesses
            IED_hits
            IED_blew
            opt_mouseover
            opt_tracker
            opt_allow_hits
            '''
        )