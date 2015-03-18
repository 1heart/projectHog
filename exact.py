"""Returns the exact win rate for a given final_strategy.

Expects the following files in the current directory:

hog.py

Because the state space for this game is relatively small, it 
can be computed to a large recursive depth, giving exact win rates.

Questions/comments: kvchen@berkeley.edu
"""

__version__ = '1.1'

# Just copied straight from the grader, no need for rewrites :)
try:
    import hog     # Student submission
except (SyntaxError, IndentationError) as e:
    import traceback
    print('Unfortunately, the exact win rate cannot be computed' +
          'because your program contains a syntax error:')
    traceback.print_exc(limit=1)
    exit(1)

import urllib.request, urllib.error
import re
from math import factorial, floor
from datetime import datetime


# CHANGE PLAYER STRATEGIES
p1_strategy = hog.final_strategy
p2_strategy = hog.always_roll(5)


def check_for_updates():
    print('You are running hog_contest_exact.py version', __version__)
    print('=================================================')
    index = 'https://raw.github.com/kvchen/hog_tools/master/'
    try:
        remote_hog_exact = urllib.request.urlopen(index + 'hog_contest_exact.py').read().decode('utf-8')
    except urllib.error.URLError:
        print("Couldn't read from GitHub, check your network settings.")
        return
    remote_version = re.search("__version__ = '(.*)'", remote_hog_exact)
    if remote_version and remote_version.group(1) != __version__:
        print('There is a new version available for download (v%s)' % remote_version.group(1))
        prompt = input('Do you want to automatically download these files? [y/n]: ')
        if 'y' in prompt.lower():
            with open('hog_contest_exact.py', 'w') as new:
                new.write(remote_hog_exact)
                print('hog_contest_exact.py updated, please rerun the script.')
            exit(0)
        else:
            print('You can download the new win rate calculator from the following link:')
            print('\t' + index + 'hog_contest_exact.py')
            print()

def nCr(n,r):
    """Returns the mathematical value of the combination n choose r,
    expanded to minimize rounding error.
    """
    assert n >= 0
    assert 0 <= r <= n

    return factorial(n) // factorial(r) // factorial(n - r)

def generate_dice_table():
    """Creates a look-up table of all possible sums and their respective
    probabilities.

    Returns a list of values that can be accessed by:
    generated_table[dice_type][num_rolls][total]
    """
    dice_table = {}
    for dice_type in ('four_sided', 'six_sided'):
        dice_table[dice_type] = {}
        sides = (4, 6)[dice_type == 'six_sided']

        for num_rolls in range(-1, 11):
            dice_table[dice_type][num_rolls] = {}
            n = num_rolls
            if n == -1:
                dice_table[dice_type][11] = {1: float(1)}
            elif n == 0:
                dice_table[dice_type][num_rolls] = {0: float(1)}

            # Calculates probabilities for sums of each number of rolls
            for possible_sum in range(1, sides*n+1):
                # Probability of getting a 1 on any one of n rolls
                if possible_sum==1:
                    prb = 1 - float((sides - 1) / sides)**n

                # Probability of getting a non-one total
                else:
                    combination = []
                    s, k = sides - 1, possible_sum - num_rolls
                    for i in range(0, floor((k-n)/s)+1):
                        combination.append(((-1)**i) * 
                            nCr(n, i) * nCr(k - s*i - 1, n - 1))
                    prb = sum(combination) / (sides**n)
                    #prb = sum(combination) * ((float(sides - 1) / sides)**n) * float((1 / (s**n)))
                dice_table[dice_type][num_rolls][possible_sum] = prb
    return dice_table

def calculate_win_rate(p1_strategy, p2_strategy, swap = False):
    """Calculates the true win rate for p1 in a scenario where p1_strategy
    takes precedence over p2_strategy in making the first move unless swap 
    is True, in which case p2 begins the game.
    """
    SCORE_SEQUENCE_MAP = {}
    dice_table = generate_dice_table()

    def calculate_roll_nodes(p1 = 0, p2 = 0, who = swap, hijinked = False):
        """A recursive search for which branches result in a p1 win.
        Calculates the true win rate.
        """
        nonlocal SCORE_SEQUENCE_MAP
        if (p1, p2, who) not in SCORE_SEQUENCE_MAP:
            if p1 >= hog.GOAL_SCORE:
                node_value = 1
            elif p2 >= hog.GOAL_SCORE:
                node_value = 0
            else:
                num_rolls = (p1_strategy, p2_strategy)[who]((p1, p2)[who], 
                    (p2, p1)[who])
                if num_rolls == (-1):
                    num_rolls = 11

                # Checks for hog wild rule and hog hijink
                dice = ('four_sided', 'six_sided')[(((p1 + p2) % 7 != 0) + hijinked) % 2]
                
                # Loops through all possible number of rolls
                branches = []
                for possible_sum in dice_table[dice][num_rolls]:
                    branch_prb = dice_table[dice][num_rolls][possible_sum]

                    home, away = (p1, p2)[who], (p2, p1)[who]

                    # Checks for free bacon
                    if not(num_rolls):
                        home += max([int(digit) for digit in str(away)]) + 1
                    else:
                        home += possible_sum

                    # Checks for swine swap
                    if (home * 2 == away) or (away * 2 == home):
                        home, away = away, home

                    # Checks for hog hijink
                    if num_rolls == 11:
                        hijinked = 1 - hijinked

                    branches.append(branch_prb * calculate_roll_nodes((home, away)[who], 
                        (away, home)[who], 1 - who, hijinked))
                node_value = sum(branches)
            SCORE_SEQUENCE_MAP[(p1, p2, who)] = node_value
        return SCORE_SEQUENCE_MAP[(p1, p2, who)]
    calculate_roll_nodes()
    return SCORE_SEQUENCE_MAP[(0, 0, swap)]

if __name__ == '__main__':
    check_for_updates()
    startTime = datetime.now()
    print("Calculating exact win rate...")
    true_win_rate = (calculate_win_rate(p1_strategy, p2_strategy) + 
        calculate_win_rate(p1_strategy, p2_strategy, swap = True)) / 2
    print("True average win rate of final_strategy is %s" % true_win_rate)
    print("Script finished in %s" % str(datetime.now() - startTime))

a = calculate_win_rate