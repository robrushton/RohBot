import random
import sqlite3
import html
import UtilityFunctions as UF
from collections import defaultdict

group_drink_pool_dict = defaultdict(set)
active_trivia_dict = defaultdict(bool)
active_trivia_question_dict = defaultdict()


def flip_coin(author):
    side = random.randint(0, 1)
    side = 'heads' if side == 0 else 'tails'
    outcome = '{}\'s coin landed on {}.'.format(UF.nickname_check(author), side)
    print(outcome)
    return outcome


def roll_die(author, message):
    if len(message.content.split()) == 1:
        side = random.randint(1, 6)
        outcome = '{} rolls a {}.'.format(UF.nickname_check(author), side)
        print(outcome)
        return outcome
    elif len(message.content.split()) == 2:
        rolls = []
        die_number = int(message.content.split()[1].split('d')[0])
        die_sides = int(message.content.split()[1].split('d')[1])
        for i in range(die_number):
            rolls.append(random.randint(1, die_sides))
            outcome = '{} rolls {}'.format(UF.nickname_check(author), str(rolls).replace('[', '').replace(']', ''))
        print(outcome)
        return outcome
    else:
        return '{}, you did something wrong.'.format(UF.nickname_check(author))


def in_there_dog(author):
    message = '{} is in there dog!'.format(UF.nickname_check(author))
    print(message)
    return message


def drink(author):
    if random.randint(1, 100) <= 20:
        message = '{} must drink!'.format(UF.nickname_check(author))
        print(message)
        return message
    else:
        message = '{} lucked out this time!'.format(UF.nickname_check(author))
        print(message)
        return message


def three_minutes(author):
    message = '{} has you for three minutes!'.format(UF.nickname_check(author))
    print(message)
    return message


def join_group_drink(author, message):
    channel = str(message.channel.id)
    group_drink_pool_dict[channel].add(author.id)
    message = '{} has joined the drinking pool!'.format(UF.nickname_check(author))
    print(message[:-1] + ' in {}.'.format(channel))
    return message


def leave_group_drink(author, message):
    channel = str(message.channel.id)
    try:
        group_drink_pool_dict[channel].remove(author.id)
        message = '{} has left the drinking pool!'.format(UF.nickname_check(author))
    except Exception:
        message = '{} is not in the drinking pool!'.format(UF.nickname_check(author))
    print(message[:-1] + ' in {}.'.format(channel))
    return message


def clear_group_drink(message):
    channel = str(message.channel.id)
    group_drink_pool_dict[channel].clear()
    message = 'The drinking pool has been cleared!'
    print(message[:-1] + ' in {}.'.format(channel))
    return message


def group_drink(message):
    losers = []
    channel = str(message.channel.id)

    if len(group_drink_pool_dict[channel]) == 0:
        result = "There is no one in the drinking pool!"
        print(result)
        return result

    for i in group_drink_pool_dict[channel]:
        outcome = random.randint(1, 100)
        if outcome <= 20:
            losers.append(i)

    if len(losers) == 2:
        result = '{} and {} are the big losers and have to drink!' \
            .format(UF.nickname_check(message.server.get_member(losers[0])),
                    UF.nickname_check(message.server.get_member(losers[1])))
    elif len(losers) == 1:
        result = '{} is the big loser and has to drink!'.format(UF.nickname_check(message.server.get_member(losers[0])))
    elif len(losers) == 0:
        result = 'You lucky fuckers, sobriety wins again.'
    else:
        names = str()
        for i in range(len(losers)):
            if i < len(losers):
                names += UF.nickname_check(message.server.get_member(losers[i]))
                if len(losers) - 1 == i:
                    names += " "
                else:
                    names += ", "
            else:
                names = names + ", and " + UF.nickname_check(message.server.get_member(losers[0]))
        result = names + "are the big losers and have to drink!"

    print(result[:-1] + ' in {}.'.format(channel))
    return result


def get_rohcoins(author, message):
    author_id = author.id
    server_id = message.server.id
    conn = sqlite3.connect('RohBotDB.db')
    args = (author_id, server_id)

    UF.new_user_setup(author, message)
    cursor = conn.execute('SELECT user_rohcoins FROM tbl_user_coins WHERE user_id = ? AND server_id = ?', args)
    coins = cursor.fetchone()[0]
    conn.close()
    print('{} has {} RohCoins.'.format(author, coins))
    return '{} has {} RohCoins.'.format(UF.nickname_check(author), coins)


def gamble(author, message):
    author_id = author.id
    server_id = message.server.id
    conn = sqlite3.connect('RohBotDB.db')

    UF.new_user_setup(author, message)
    args = (author_id, server_id)
    cursor = conn.execute('SELECT exists(SELECT * FROM tbl_user_coins WHERE user_id = ? AND server_id = ?)', args)
    user_check = cursor.fetchone()[0]
    if user_check == 0:
        conn.close()
        return '{}, use the !coins command to get your starter pack of 10 RohCoins, then try again!' \
            .format(UF.nickname_check(author))
    else:
        try:
            bet = message.content.split()[1]
        except Exception:
            return 'Please put a space between gamble and your bet!'
        try:
            int(bet)
        except Exception:
            return 'You must enter an integer!'
        args = (author_id, server_id, bet)
        cursor = conn.execute(
            'SELECT exists(SELECT * FROM tbl_user_coins WHERE user_id = ? AND server_id = ? AND user_rohcoins >= ?)',
            args)
        coins_check = cursor.fetchone()[0]
        if coins_check == 0:
            conn.close()
            return '{}, you don\'t have enough RohCoins for that bet!'.format(UF.nickname_check(author))
        else:
            mod = UF.get_gamble_modifier()
            payout = int(int(bet) * mod)
            outcome = payout - int(bet)
            if payout == 0:
                args = (bet, author_id, server_id)
                cursor = conn.execute(
                    'UPDATE tbl_user_coins SET user_rohcoins = user_rohcoins - ? WHERE user_id = ? AND server_id = ?',
                    args)
                conn.commit()
                conn.close()
                print('{} lost {} RohCoins.'.format(author, bet))
                return '{} lost {} RohCoins!'.format(UF.nickname_check(author), bet)
            else:
                args = (outcome, author_id, server_id)
                cursor = conn.execute(
                    'UPDATE tbl_user_coins SET user_rohcoins = user_rohcoins + ? WHERE user_id = ? AND server_id = ?',
                    args)
                conn.commit()
                conn.close()
                print('{} gained {} RohCoins.'.format(author, outcome))
                return '{} gained {} RohCoins!'.format(UF.nickname_check(author), outcome)


def add_coins_command(author, message):
    server_id = message.server.id
    conn = sqlite3.connect('RohBotDB.db')
    if UF.check_for_max_permissions(author, message.server):
        content = message.content.split()
        target = message.server.get_member_named(content[1])
        amount = int(content[2])
        args = (amount, target.id, server_id)
        cursor = conn.execute(
            'UPDATE tbl_user_coins SET user_rohcoins = user_rohcoins + ? WHERE user_id = ? AND server_id = ?', args)
        conn.commit()
        conn.close()
        print('{} coins have been added to {}.'.format(amount, target))
        return '{} coins have been added to {}.'.format(amount, UF.nickname_check(target))
    else:
        return 'You do not have the correct permissions for this action.'


def get_trivia_question(author, message):
    ch_id = message.channel.id
    UF.new_user_setup(author, message)
    if not active_trivia_dict[ch_id]:
        trivia_dict = UF.get_json('https://opentdb.com/api.php?amount=1&type=multiple')
        difficulty = trivia_dict['results'][0]['difficulty']
        question = html.unescape(trivia_dict['results'][0]['question'])
        correct_answer = trivia_dict['results'][0]['correct_answer']
        possible_answers = trivia_dict['results'][0]['incorrect_answers']
        insert_at = random.randint(0, 3)
        possible_answers.insert(insert_at, correct_answer)
        result = 'This is a(n) {} difficulty question. \n{} \nAnswer Choices:\n1. {}\n2. {}\n3. {}\n4. {}'\
            .format(difficulty, question, html.unescape(possible_answers[0]), html.unescape(possible_answers[1]),
                    html.unescape(possible_answers[2]), html.unescape(possible_answers[3]))
        ch_id = message.channel.id
        active_trivia_dict[ch_id] = True
        print('Question opened on {}'.format(ch_id))
        active_trivia_question_dict[ch_id] = {'difficulty': difficulty, 'question': question,
                                              'correct_answer': insert_at + 1, 'time': UF.get_seconds_time()}
        return result
    else:
        print('Question already open on {}'.format(ch_id))
        return 'Only one trivia question per channel can be active at a time.'


def answer_question(author, message):
    user_id = author.id
    ch_id = message.channel.id
    server_id = message.server.id
    answer_time = UF.get_seconds_time() - active_trivia_question_dict[ch_id]['time']
    incoming_answer = int(message.content.split()[1])

    if active_trivia_dict[ch_id]:
        if answer_time > 30:
            active_trivia_dict[ch_id] = False
            print('Question answered in {} seconds on {}'.format(answer_time, ch_id))
            print('Question closed on {}'.format(ch_id))
            return 'You answered too late, the correct answer was {}. You only have 30 seconds to answer!'\
                .format(active_trivia_question_dict[ch_id]['correct_answer'])
        else:
            if active_trivia_question_dict[ch_id]['correct_answer'] == incoming_answer:
                if active_trivia_question_dict[ch_id]['difficulty'] == 'hard':
                    reward = 15
                elif active_trivia_question_dict[ch_id]['difficulty'] == 'medium':
                    reward = 10
                else:
                    reward = 5
                UF.add_coins(user_id, server_id, reward)
                print('{} received {} coins.'.format(author, reward))
                active_trivia_dict[ch_id] = False
                print('Question answered in {} seconds on {}'.format(answer_time, ch_id))
                print('Question closed on {}'.format(ch_id))
                return '{}, that\'s correct! You receive {} coins as a reward!'.format(UF.nickname_check(author), reward)
            else:
                active_trivia_dict[ch_id] = False
                print('Question answered in {} seconds on {}'.format(answer_time, ch_id))
                print('Question closed on {}'.format(ch_id))
                return '{}, that answer is incorrect. The correct answer was {}.'\
                    .format(UF.nickname_check(author), active_trivia_question_dict[ch_id]['correct_answer'])
    else:
        return 'There is no active trivia question in this channel.'


def help_command(message):
    result = 'RohBot Commands:\n' \
             'Use !coins command to get your free coins and to be added to the database!\n' \
             '---------------------------------------------------------------------------------------\n' \
             '!flip                     flips a coin\n' \
             '!roll                     rolls a 6-sided die\n' \
             '!roll XdY            rolls X number of Y-sided dice\n' \
             '!inthere              says you\'re in there dog\n' \
             '!3min                  RohBot has you for 3 minutes\n' \
             '!drink                  20% chance you have to drink\n' \
             '!joinpool             adds you to the pool for group drinking\n' \
             '!leavepool          removes you from the group drinking pool\n' \
             '!clearpool           clears everyone out of the group drinking pool\n' \
             '!gdrink                everyone in the group drinking pool has 20% to drink\n' \
             '!nsfw                   links random nsfw reddit thread\n' \
             '!coins                  shows how many RohCoins you have\n' \
             '!gamble X          gamble X of your RohCoins\n' \
             '!addcoins X Y   X is the user Name#0000, Y is the amount, requires admin\n' \
             '!trivia                  a trivia question with 30 seconds to answer\n' \
             '!answer X          answers the trivia question where X is the answer choice'
    print('Printed !help on {}'.format(message.channel.id))
    return result
