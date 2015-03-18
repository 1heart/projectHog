"""The Game of Hog."""

from dice import four_sided, six_sided, make_test_dice
from ucb import main, trace, log_current_line, interact

GOAL_SCORE = 100 # The goal of Hog is to score 100 points.

######################
# Phase 1: Simulator #
######################

# Taking turns

def roll_dice(num_rolls, dice=six_sided):
    """Roll DICE for NUM_ROLLS times.  Return either the sum of the outcomes,
    or 1 if a 1 is rolled (Pig out). This calls DICE exactly NUM_ROLLS times.

    num_rolls:  The number of dice rolls that will be made; at least 1.
    dice:       A zero-argument function that returns an integer outcome.
    """
    # These assert statements ensure that num_rolls is a positive integer.
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls > 0, 'Must roll at least once.'
    total = 0
    pigOut = 0
    for i in range(0,num_rolls):
        currentRoll = dice()
        if currentRoll == 1: #if any dice = 1, pigOut is applied
            pigOut = 1
        else:
            total += currentRoll #otherwise, increase the total
    if pigOut == 1:
        return 1
    else:
        return total

def take_turn(num_rolls, opponent_score, dice=six_sided):
    """Simulate a turn rolling NUM_ROLLS dice, which may be 0 (Free bacon).

    num_rolls:       The number of dice rolls that will be made.
    opponent_score:  The total score of the opponent.
    dice:            A function of no args that returns an integer outcome.
    """
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls >= 0, 'Cannot roll a negative number of dice.'
    assert num_rolls <= 10, 'Cannot roll more than 10 dice.'
    assert opponent_score < 100, 'The game should be over.'
    if num_rolls == 0:
        dig10 = int(opponent_score/10)
        dig1 = opponent_score - (dig10 * 10)
        return (max(dig10,dig1) + 1)
    else:
        return roll_dice(num_rolls,dice)

# Playing a game

def select_dice(score, opponent_score):
    """Select six-sided dice unless the sum of SCORE and OPPONENT_SCORE is a
    multiple of 7, in which case select four-sided dice (Hog wild).
    """
    if (score + opponent_score)%7 == 0:
        return four_sided
    else:
        return six_sided

def other(who):
    """Return the other player, for a player WHO numbered 0 or 1.

    >>> other(0)
    1
    >>> other(1)
    0
    """
    return 1 - who

def play(strategy0, strategy1, goal=GOAL_SCORE):
    """Simulate a game and return the final scores of both players, with
    Player 0's score first, and Player 1's score second.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    strategy0:  The strategy function for Player 0, who plays first.
    strategy1:  The strategy function for Player 1, who plays second.
    """
    who = 0  # Which player is about to take a turn, 0 (first) or 1 (second)
    score0, score1 = 0, 0
    def swineSwap(score0,score1):
        if (score0 == 2 * score1) or (score1 == 2* score0):
            return (score1,score0)
        else:
            return (score0,score1)

    while score0 < goal and score1 < goal: #while players haven't won yet
        print ('0=',score0,' 1=',score1)
        if who == 0: #player 0 taking turn
            score0 += take_turn(strategy0(score0,score1),score1,select_dice(score0,score1))
            who = 1
            score0,score1 = swineSwap(score0,score1)
        else: #player 1 taking turn
            score1 += take_turn(strategy1(score1,score0),score0,select_dice(score1,score0))
            who = 0
            score0,score1 = swineSwap(score0,score1)
    print ('Game ended. Score of player 0 is ',score0,' and score of player 1 is ',score1)
    return score0,score1

#######################
# Phase 2: Strategies #
#######################

# Basic Strategy


def always_roll(n):
    """Return a strategy that always rolls N dice.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    >>> strategy = always_roll(5)
    >>> strategy(0, 0)
    5
    >>> strategy(99, 99)
    5
    """
    def strategy(score, opponent_score):
        return n
    return strategy

# Experiments


def make_averaged(fn, num_samples=100):
    """Return a function that returns the average_value of FN when called.

    To implement this function, you will have to use *args syntax, a new Python
    feature introduced in this project.  See the project description.

    >>> dice = make_test_dice(3, 1, 5, 6)
    >>> averaged_dice = make_averaged(dice, 1000)
    >>> averaged_dice()
    3.75
    >>> make_averaged(roll_dice, 1000)(2, dice)
    6.0

    In this last example, two different turn scenarios are averaged.
    - In the first, the player rolls a 3 then a 1, receiving a score of 1.
    - In the other, the player rolls a 5 and 6, scoring 11.
    Thus, the average value is 6.0.
    """
    def new(*args):
        total = 0
        for i in range(0,num_samples):
            total += fn(*args)
        avg = total/num_samples
        return avg
    return new




def max_scoring_num_rolls(dice=six_sided):
    """Return the number of dice (1 to 10) that gives the highest average turn
    score by calling roll_dice with the provided DICE.  Print all averages as in
    the doctest below.  Assume that dice always returns positive outcomes.

    >>> dice = make_test_dice(3)
    >>> max_scoring_num_rolls(dice)
    1 dice scores 3.0 on average
    2 dice scores 6.0 on average
    3 dice scores 9.0 on average
    4 dice scores 12.0 on average
    5 dice scores 15.0 on average
    6 dice scores 18.0 on average
    7 dice scores 21.0 on average
    8 dice scores 24.0 on average
    9 dice scores 27.0 on average
    10 dice scores 30.0 on average
    10
    """
    highest_i, highestScore = 0, 0
    for i in range(1,11):
        currentScore = make_averaged(roll_dice)(i,dice)
        if currentScore > highestScore:
            highestScore = currentScore
            highest_i = i
        print(i,'dice scores',currentScore,'on average')
    return highest_i


def winner(strategy0, strategy1):
    """Return 0 if strategy0 wins against strategy1, and 1 otherwise."""
    score0, score1 = play(strategy0, strategy1)
    if score0 > score1:
        return 0
    else:
        return 1

def average_win_rate(strategy, baseline=always_roll(5)):
    """Return the average win rate (0 to 1) of STRATEGY against BASELINE."""
    win_rate_as_player_0 = 1 - make_averaged(winner)(strategy, baseline)
    win_rate_as_player_1 = make_averaged(winner)(baseline, strategy)
    return (win_rate_as_player_0 + win_rate_as_player_1) / 2 # Average results


def run_experiments():
    """Run a series of strategy experiments and report results."""
    if False: # Change to False when done finding max_scoring_num_rolls
        six_sided_max = max_scoring_num_rolls(six_sided)
        print('Max scoring num rolls for six-sided dice:', six_sided_max)
        four_sided_max = max_scoring_num_rolls(four_sided)
        print('Max scoring num rolls for four-sided dice:', four_sided_max)

    if False: # Change to True to test always_roll(8)
        print('always_roll(8) win rate:', average_win_rate(always_roll(8)))

    if False: # Change to True to test bacon_strategy
        print('bacon_strategy win rate:', average_win_rate(bacon_strategy))

    if False: # Change to True to test swap_strategy
        print('swap_strategy win rate:', average_win_rate(swap_strategy))

    if True: # Change to True to test final_strategy
        print('final_strategy win rate:', average_win_rate(final_strategy))

    "*** You may add additional experiments as you wish ***"


def largestDigit(x): # give you the largest digit of a 2 digit number
    assert x >= 0 and x <100
    tensDig = x // 10
    onesDig = x - tensDig * 10
    return max(tensDig,onesDig)


# Strategies

def bacon_strategy(score, opponent_score, margin=8, num_rolls=5):
    """This strategy rolls 0 dice if that gives at least MARGIN points,
    and rolls NUM_ROLLS otherwise.
    """
    if (largestDigit(opponent_score) + 1) >= margin:
        return 0
    else:
        return num_rolls


def swap_strategy(score, opponent_score, margin=8, num_rolls=5):
    """This strategy rolls 0 dice when it would result in a beneficial swap and
    rolls NUM_ROLLS if it would result in a harmful swap. It also rolls
    0 dice if that gives at least MARGIN points and rolls
    NUM_ROLLS otherwise.
    """
    potentialYou = score + (1 + largestDigit (opponent_score)) #potential score for rolling 0
    if  potentialYou == opponent_score/2 or opponent_score == potentialYou/2:
        if potentialYou < opponent_score:
            return 0
        else:
            return num_rolls
    else:
        return bacon_strategy(score, opponent_score, margin, num_rolls)
     



def correctEV(score,opponent_score): #implements the correct # rolls for maximum value, depending on dice
    if (score+opponent_score)%7 == 0: #if you're rolling 4sided, return 4
        return 4
    else: #if you're rolling 6sided, return 6
        return 6

def final_strategy(score, opponent_score):
    """Write a brief description of your final strategy.
        Execute in order (if possible):
        1. favorable swine swap
        2. give other person 4 dice
        3. bacon strategy
        The correct numRoll for 4-sided dice is 4, while the correct\
        numRoll for 6-sided dice is 6; therefore, use the correctEV \
        function to choose the right roll.
    """
    potentialYou = score + (1 + largestDigit (opponent_score)) # potential future score if rolling 0

    if potentialYou == opponent_score/2 or opponent_score == potentialYou/2: ##if favorable swine swap, return 0
        if opponent_score - potentialYou > 0:
            return 0
        else:
            return correctEV(score,opponent_score)
    if (potentialYou + opponent_score)%7 == 0 and potentialYou != 0: ##try to give other person 4 dice
        return 0
    if (score+opponent_score)%7 == 0: #rolling 4sided bacon strat
        if (largestDigit(opponent_score) + 1) >= 4: ##if favorable free bacon, return 0 (margin = 4)
            return 0
        else:
            return correctEV(score,opponent_score)
    if (score+opponent_score)%7 != 0: #rolling 6sided bacon strat
        if (largestDigit(opponent_score) + 1) >= 8: ##if favorable free bacon, return 0 (margin = 8)
            return 0
        else:
            return correctEV(score,opponent_score)

from exact import *
#a = calculate_win_rate

##########################
# Command Line Interface #
##########################

# Note: Functions in this section do not need to be changed.  They use features
#       of Python not yet covered in the course.


@main
def run(*args):
    """Read in the command-line argument and calls corresponding functions.

    This function uses Python syntax/techniques not yet covered in this course.
    """
    import argparse
    parser = argparse.ArgumentParser(description="Play Hog")
    parser.add_argument('--run_experiments', '-r', action='store_true',
                        help='Runs strategy experiments')
    args = parser.parse_args()

    if args.run_experiments:
        run_experiments()
