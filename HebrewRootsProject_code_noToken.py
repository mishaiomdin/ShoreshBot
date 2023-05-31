import csv
import sqlite3
import telebot
from telebot import types

#Connecting the database
connection = sqlite3.connect('database.db', check_same_thread=False)
cursor = connection.cursor()

csv_file_words = "HebrewTableWords.csv"
csv_file_roots = "HebrewTableRoots.csv"
csv_file_patterns = "HebrewTablePatterns.csv"
about_text_file = 'AboutThisBot.txt'

admins = [839506170] #Misha Iomdin

#Setting up the bot
bot = telebot.TeleBot("your_token_here")

#OPERATIONS WITH TABLES IN DATABASE

#Creates table "words" in database
def create_table_words():
	cursor.execute(
		'''
		CREATE TABLE words (
		id INTEGER PRIMARY KEY,
		word VARCHAR(30),
		root VARCHAR(30),
		part_of_speech VARCHAR(30),
		pattern VARCHAR(30),
		translation TEXT)
		'''
	)

#Creates table "roots" in database
def create_table_roots():
	cursor.execute(
		'''
		CREATE TABLE roots (
		id INTEGER PRIMARY KEY,
		root VARCHAR(30),
		first_consonant VARCHAR(5),
		second_consonant VARCHAR(5),
		third_consonant VARCHAR(5),
		meaning TEXT,
		gizra TEXT)
		'''
		)

#Creates table "patterns" in database (binyan + miskal)
def create_table_patterns():
	cursor.execute(
		'''
		CREATE TABLE patterns (
		id INTEGER PRIMARY KEY,
		pattern VARCHAR(30),
		pattern_heb VARHCAR(30),
		description TEXT,
		of_binyan VARCHAR(30),
		is_binyan BIT)
		'''
		)

#Clears table "words" in database
def clear_table_words():
	cursor.execute(
		'''
		DELETE FROM words;
		''')
	connection.commit()

#Clears table "roots" in database
def clear_table_roots():
	cursor.execute(
		'''
		DELETE FROM roots;
		''')
	connection.commit()

#Clears table "patterns" in database
def clear_table_patterns():
	cursor.execute(
		'''
		DELETE FROM patterns;
		''')
	connection.commit()

#Updates table "words" in database according to csv_file_words
def update_table_words_from_csv():
	with open(csv_file_words, "r") as file:
		csv_reader = csv.reader(file)
		next(csv_reader)  # Skip the header row
		update_query = '''
		INSERT INTO words(word, root, part_of_speech, pattern, translation)
		VALUES
		'''
		for row in csv_reader:
			update_query += f"('{row[0]}', '{row[1]}', '{row[2]}', '{row[3]}', '{row[4]}'),\n"
		update_query = update_query[:-2] + ";"
		cursor.execute(update_query)
		connection.commit()

#Updates table "roots" in database according to csv_file_roots
def update_table_roots_from_csv():
	with open(csv_file_roots, "r") as file:
		csv_reader = csv.reader(file)
		next(csv_reader)  # Skip the header row
		update_query = '''
		INSERT INTO roots(root, first_consonant, second_consonant, third_consonant, meaning)
		VALUES
		'''
		for row in csv_reader:
			update_query += f"('{row[0]}', '{row[1]}', '{row[2]}', '{row[3]}', '{row[4][:16]}'),\n"
		update_query = update_query[:-2] + ";"
		cursor.execute(update_query)
		connection.commit()

#Updates table "patterns" in database according to csv_file_patterns
def update_table_patterns_from_csv():
	with open(csv_file_patterns, "r") as file:
		csv_reader = csv.reader(file)
		next(csv_reader)  # Skip the header row
		update_query = '''
		INSERT INTO patterns(pattern, description, is_binyan, of_binyan)
		VALUES
		'''
		for row in csv_reader:
			update_query += f"('{row[0]}', '{row[1][:16]}', {row[2]}, '{row[3]}'),\n"
		update_query = update_query[:-2] + ";"
		cursor.execute(update_query)
		connection.commit()

#Prints all of the table "words" to console
def print_table_words():
	cursor.execute(
		'''
		SELECT * FROM words;
		''')
	results = cursor.fetchall()
	for row in results:
		print(row)

#Deletes table "words", creates it again and updates it according to csv_file_words
def recreate_table_words():
	cursor.execute("DROP TABLE words;")
	connection.commit()
	create_table_words()
	update_table_words_from_csv()

#Deletes table "roots", creates it again and updates it according to csv_file_roots
def recreate_table_roots():
	cursor.execute("DROP TABLE roots;")
	connection.commit()
	create_table_roots()
	update_table_roots_from_csv()

#Deletes table "patterns", creates it again and updates it according to csv_file_patterns
def recreate_table_patterns():
	cursor.execute("DROP TABLE patterns;")
	connection.commit()
	create_table_patterns()
	update_table_patterns_from_csv()

#Deletes, recreates and updates from csv all three tables
def recreate_tables():
	recreate_table_words()
	print("Table words recreated.")
	recreate_table_roots()
	print("Table roots recreated.")
	recreate_table_patterns()
	print("Table patterns recreated.")

#Clears and updates all tables
def update_tables():
	clear_table_words()
	update_table_words_from_csv()
	print("Table words updated.")
	clear_table_roots()
	update_table_roots_from_csv()
	print("Table roots updated.")
	clear_table_patterns()
	update_table_patterns_from_csv()
	print("Table patterns updated.")

#SELECTIONS FROM TABLES IN DATABASE

#Selects all words in table "words" by requested_root, returns InlineKeyboardMarkup:
#| 1. word | translation | part_of_speech | pattern |
def select_by_root_as_keyboard(requested_root):
	cursor.execute(
		f'''
		SELECT word, root, translation, part_of_speech, pattern
		FROM words
		WHERE root LIKE '%{requested_root}%';
		''')
	results = cursor.fetchall() #get all of the results
	keyboard = types.InlineKeyboardMarkup()
	i = 1
	for row in results:
		cur_word_row = [
		types.InlineKeyboardButton(f"{row[0]} .{i}", callback_data = f"word: {row[0]}"), #word
		#types.InlineKeyboardButton(row[1], callback_data = f"root: {row[1]}"), #root
		types.InlineKeyboardButton(row[2], callback_data = f"translation: {row[2][:16]}"), #translation
		#types.InlineKeyboardButton(row[3], callback_data = f"part_of_speech: {row[3]}"), #part_of_speech
		types.InlineKeyboardButton(row[4], callback_data = f"pattern: {row[4]}") #pattern
		]
		keyboard.row(*cur_word_row)
		i += 1
	return keyboard

#Selects all words in table "words" by requested_pattern, returns InlineKeyboardMarkup:
#| 1. word | root | translation | part_of_speech |
def select_by_pattern_as_keyboard(requested_pattern):
	cursor.execute(
		f'''
		SELECT word, root, translation, part_of_speech, pattern
		FROM words
		WHERE pattern LIKE '%{requested_pattern}%';
		''')
	results = cursor.fetchall() #get all of the results
	keyboard = types.InlineKeyboardMarkup()
	i = 1
	for row in results:
		cur_word_row = [
		types.InlineKeyboardButton(f"{row[0]} .{i}", callback_data = f"word: {row[0]}"), #word
		types.InlineKeyboardButton(row[2], callback_data = f"translation: {row[2][:16]}"), #translation
		types.InlineKeyboardButton(row[1], callback_data = f"root: {row[1]}"), #root
		#types.InlineKeyboardButton(row[3], callback_data = f"part_of_speech: {row[3]}"), #part_of_speech
		#types.InlineKeyboardButton(row[4], callback_data = f"pattern: {row[4]}") #pattern
		]
		keyboard.row(*cur_word_row)
		i += 1
	return keyboard

#Selects everything from all words, returns list of rows
def select_all():
	cursor.execute(
		f'''
		SELECT *
		FROM words;
		''')
	results = cursor.fetchall()
	return results

#Selects all from "roots", returns InlineKeyboardMarkup:
#| root | meaning |
def select_all_roots_as_keyboard():
	keyboard = types.InlineKeyboardMarkup()
	cursor.execute(
		f'''
		SELECT root, meaning
		FROM roots;
		''')
	results = cursor.fetchall()
	for cur_root in results:
		cur_row = [
		types.InlineKeyboardButton(text = cur_root[0], callback_data = f"root: {cur_root[0]}"),
		types.InlineKeyboardButton(text = cur_root[1], callback_data = f"root_meaning: {cur_root[1]}")
		]
		keyboard.row(*cur_row)
	return keyboard

#Selects all from "patterns", returns InlineKeyboardMarkup:
#| pattern | description |
def select_all_patterns_as_keyboard():
	keyboard = types.InlineKeyboardMarkup()
	cursor.execute(
		f'''
		SELECT pattern, description, of_binyan
		FROM patterns;
		''')
	results = cursor.fetchall()
	for cur_pattern in results:
		of_binyan = f"от {cur_pattern[2]}"
		if len(cur_pattern[2]) == 0:
			of_binyan = " "
		cur_row = [
		types.InlineKeyboardButton(text = cur_pattern[0], callback_data = f"pattern: {cur_pattern[0]}"),
		types.InlineKeyboardButton(text = cur_pattern[1], callback_data = f"pattern_description: {cur_pattern[1]}"),
		types.InlineKeyboardButton(text = of_binyan, callback_data = f"pattern_of_binyan: {cur_pattern[2]}")
		]
		keyboard.row(*cur_row)
	return keyboard

#REQUESTS FROM USER IN BOT –> ANSWERS TO USER

#Searches all words by requested_root, replies to user with text (if any):
#1. word (part_of_speech): translation
def find_by_root(chat_id, requested_root):
	bot.send_message(chat_id, f"Searching for root {requested_root}...")
	output = select_by_root(requested_root)
	if output == "":
		bot.send_message(chat_id, "The search returned no results.")
	else:
		bot.send_message(chat_id, f"<b>Found results:</b>\n{output}", parse_mode="HTML")

#Selects all words by requested_root, replies to user with InlineKeyboardMarkup (if any):
#| 1. word | translation | part_of_speech | pattern |
def find_by_root_as_keyboard(chat_id, requested_root):
	bot.send_message(chat_id, f"Searching for root {requested_root}...")
	keyboard = select_by_root_as_keyboard(requested_root)
	if len(keyboard.keyboard) == 0:
		bot.send_message(chat_id, "The search returned no results.")
	else:
		bot.send_message(chat_id, f"<b>Found results:</b>", parse_mode="HTML", reply_markup = keyboard)

#Selects all words by requested_pattern, replies to user with InlineKeyboardMarkup (if any):
#| 1. word | root | translation | part_of_speech |
def find_by_pattern_as_keyboard(chat_id, requested_pattern):
	bot.send_message(chat_id, f"Searching for pattern {requested_pattern}...")
	keyboard = select_by_pattern_as_keyboard(requested_pattern)
	if len(keyboard.keyboard) == 0:
		bot.send_message(chat_id, "The search returned no results.")
	else:
		bot.send_message(chat_id, f"<b>Found results:</b>", parse_mode="HTML", reply_markup = keyboard)

#REQUESTS NOT USING DATABASE

#Replies to user with link to pealim for word
def find_word(chat_id, requested_word):
	link_to_pealim = f"https://www.pealim.com/search/?q={requested_word}"
	bot.send_message(chat_id, f'''Here's a link to pealim: <a href="{link_to_pealim}">{requested_word}</a>''', parse_mode="HTML")

#REACTS TO COMMANDS

#/start: Welcomes user, offers list of commands
@bot.message_handler(commands=['start'])
def start_bot(message):
	bot.send_message(message.chat.id, "Hi! I'm shoresh_bot. My task is analyzing hebrew roots and helping users.")
	commands_description = "Here's a list of my commands:\n"
	commands_description += "/about — learn more about the bot\n"
	commands_description += "/root — find words by root\n"
	commands_description += "/pattern — find words by pattern\n"
	commands_description += "more coming soon!\n"
	bot.send_message(message.chat.id, commands_description)

#/root: Offers clickable list of roots
@bot.message_handler(commands=['root'])
def offer_roots_new(message):
	keyboard = select_all_roots_as_keyboard()
	bot.send_message(message.chat.id, "Select a root to learn its words:", reply_markup = keyboard)

#/pattern: Offers clickable list of patterns
@bot.message_handler(commands=['pattern'])
def offer_patterns_new(message):
	keyboard = select_all_patterns_as_keyboard()
	bot.send_message(message.chat.id, "Select a pattern to learn its words:", reply_markup = keyboard)

#/about: Tells user about bot
@bot.message_handler(commands=['about'])
def about_bot(message):
	with open(about_text_file) as file:
		about_text = file.read()
		bot.send_message(message.chat.id, about_text, parse_mode="HTML")

#/update: Clears all tables and updates according to csv: ONLY FOR ADMIN (MISHA)
@bot.message_handler(commands=['update'])
def initiate_update(message):
	if message.from_user.id in a:
		update_tables()
		bot.send_message(message.chat.id, "Tables updated succesfully")
	else:
		bot.send_message(message.chat.id, "You aren't an admin.")

#/recreate: Deletes all tables, creates and updates according to csv: ONLY FOR ADMIN (MISHA)
@bot.message_handler(commands=['update'])
def initiate_update(message):
	if message.from_user.id in admins:
		recreate_tables()
		bot.send_message(message.chat.id, "Tables recreated & updated succesfully")
	else:
		bot.send_message(message.chat.id, "You aren't an admin.")

#REACTS TO SENT TEXT MESSAGES
#for now, initiates start
@bot.message_handler(content_types=['text'])
def read_message(message):
	start_bot(message = message)

#REACTS TO CLICKED BUTTONS IN INLINE_KEYBOARD
@bot.callback_query_handler(func=lambda call: True)
def read_call(call):
	if "root: " in call.data:
		requested_root = call.data[6:]
		find_by_root_as_keyboard(call.message.chat.id, requested_root)
	elif "pattern: " in call.data:
		requested_pattern = call.data[9:]
		find_by_pattern_as_keyboard(call.message.chat.id, requested_pattern)
	elif "word: " in call.data:
		requested_word = call.data[6:]
		find_word(call.message.chat.id, requested_word)

recreate_tables()

#Begins the bot
while True:
	try:
		bot.polling()
	except Exception as error:
		print("A PROBLEM OCCURED", error)
