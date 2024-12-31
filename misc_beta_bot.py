# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from config import TOKEN

from const import REG_OK

import os
import re
import random
import time

import pymysql
import pymysql.cursors

import sqlite3

db_pymysql = True#set True or False
db_sqlite3 = True#set True or False

if db_sqlite3:
	con=sqlite3.connect("db4tg.sqlite")
	cur=con.cursor()
	cur.execute('''CREATE TABLE IF NOT EXISTS users (
	user_id	INTEGER NOT NULL DEFAULT 0 UNIQUE,
	reg_int	INTEGER NOT NULL DEFAULT 0,
	f_name	VARCHAR NOT NULL DEFAULT 'хз',
	mcoins	INTEGER NOT NULL DEFAULT 1024,
	rnd_kd	INTEGER NOT NULL DEFAULT 0,
	lng_code	VARCHAR NOT NULL DEFAULT ''
	)''');
	con.commit()

if db_pymysql:
	ldb=pymysql.connect(
	host='localhost',
	user='root',
	password='V3rY$tR0NgPaS$Sw0Rd',
	db='db',
	charset='utf8mb4',
	cursorclass=pymysql.cursors.DictCursor)
	dbc = ldb.cursor()
	dbc.execute('''CREATE TABLE IF NOT EXISTS `tg_bot_users` (
	`user_id` bigint(20) unsigned NOT NULL DEFAULT '0',
	`reg_int` int(11) unsigned NOT NULL DEFAULT '0',
	`f_name` text NOT NULL,
	`mcoins` bigint(20) unsigned NOT NULL DEFAULT '1024',
	`rnd_kd` int(11) unsigned NOT NULL DEFAULT '0',
	`lng_code` varchar(8) NOT NULL DEFAULT '',
	PRIMARY KEY (`user_id`)
	);''');
	ldb.commit()
	#bot users.
	dbc.execute('''CREATE TABLE IF NOT EXISTS `tg_iris_zarazy` (
	`when_int` int(11) unsigned NOT NULL DEFAULT '0',
	`who_id` bigint(20) unsigned NOT NULL DEFAULT '0',
	`user_id` bigint(20) unsigned NOT NULL DEFAULT '0',
	`u_link` varchar(500) NOT NULL DEFAULT '',
	`bio_str` varchar(11) NOT NULL DEFAULT '1',
	`bio_int` int(11) unsigned NOT NULL DEFAULT '1',
	`expr_int` int(11) unsigned NOT NULL DEFAULT '0',
	`expr_str` varchar(11) NOT NULL DEFAULT '0',
	UNIQUE KEY `UNIQUE` (`who_id`,`user_id`)
	);''');
	#зберігалка: https://github.com/S1S13AF7/ub4tg
	ldb.commit()

async def reg_user(message: types.Message):
	print(message)
	user_id = int(message.from_user.id)
	user_fn = message.from_user.first_name or ''
	lng_code = message.from_user.language_code or ''
	when_int = int(datetime.timestamp(message.date))
	reg_date = 0
	mcoins_c = 0
	if db_sqlite3:
		try:
			cur.execute("INSERT OR IGNORE INTO users(user_id,reg_int,f_name,lng_code) VALUES (?,?,?,?)", (int(user_id),int(when_int),str(user_fn),str(lng_code))); con.commit()
		except Exception as Err:
			print(f"sqlite INSERT:{Err}")
		
		sqlite_rd=when_int#for min (rd,rd)
		sqlite_co=1024
		try:
			cur.execute("SELECT reg_int,mcoins FROM users WHERE user_id = %d" % int(user_id)); 
			rd = cur.fetchone();
			if rd is None:
				print('не знайшли юзера у базі sqlite')
			else:
				sqlite_rd=int(rd[0])
				sqlite_co=int(rd[1])
				if sqlite_rd > 0:
					reg_date=sqlite_rd
				else:
					reg_date=when_int
				if sqlite_co > 0:
					mcoins_c=sqlite_co
		except Exception as Err:
			print(f"sqlite SELECT:{Err}")
	
	if db_pymysql:
		try:
			dbc.execute("INSERT INTO `tg_bot_users` (user_id,reg_int,f_name,lng_code) VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE f_name=VALUES(f_name);",(int(user_id),int(when_int),str(user_fn),str(lng_code))); ldb.commit();
		except Exception as Err:
			print(f"localhost INSERT:{Err}")
		pymysql_rd=when_int#for min (rd,rd)
		pymysql_co=1024
		try:
			dbc.execute("SELECT reg_int,mcoins FROM `tg_bot_users` WHERE user_id = %d" % int(user_id)); 
			rd = dbc.fetchone();
			if rd is None:
				print('не знайшли юзера у базі localhost')
			else:
				pymysql_rd=int(rd['reg_int'])
				pymysql_co=int(rd['mcoins'])
				if pymysql_rd > 0:
					reg_date=pymysql_rd
				else:
					reg_date=when_int
				if pymysql_co > 0:
					mcoins_c=pymysql_co
		except Exception as Err:
			print(f"localhost SELECT:{Err}")

	if db_sqlite3 and db_pymysql:
		#якщо юзаємо обидві бази,то
		reg_date=int(min(sqlite_rd,pymysql_rd))
		mcoins_c=int(max(sqlite_co,pymysql_co))
		
		if sqlite_rd < pymysql_rd or sqlite_co > pymysql_co:
			#UPDATE `tg_bot_users` SET `reg_int`=?,`mcoins`=? WHERE `user_id`=?;
			try:
				dbc.execute(f"UPDATE `tg_bot_users` SET `reg_int` ='{reg_date}',`mcoins` ='{mcoins_c}' WHERE user_id = %d" % int(user_id)); ldb.commit()#як я хотів воно нехотіло, тому буде пока так.
			except Exception as Err:
				print(f"localhost UPDATE:{Err}")
		
		if sqlite_rd > pymysql_rd or sqlite_co < pymysql_co:
			try:
				cur.execute("UPDATE users SET reg_int =?,mcoins=? WHERE user_id=?", (int(reg_date),int(mcoins_c),int(user_id))); con.commit()
			except Exception as Err:
				print(f"sqlite UPDATE:{Err}")
	
	if reg_date==when_int:
		print(REG_OK.get(lng_code, REG_OK['default']).format(user_fn=user_fn))
	
	return reg_date

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML) #see: https://mastergroosha.github.io/aiogram-2-guide/messages/
dp = Dispatcher(bot)   

print('Bot started') 

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
	#print(message)
	snd_msg = "🖖"
	user_id = int(message.from_user.id)
	user_fn = message.from_user.first_name or ''
	lng_code = message.from_user.language_code or ''
	when_int = int(datetime.timestamp(message.date))
	rd=int(await reg_user(message))#create or date
	if rd == when_int:
		snd_msg = REG_OK.get(lng_code, REG_OK['default']).format(user_fn=user_fn)
	await message.answer(snd_msg)

@dp.message_handler(commands=['reg'])
async def cmd_reg(message: types.Message):
	#print(message)
	snd_msg = "🤷"
	user_id = int(message.from_user.id)
	user_fn = message.from_user.first_name or ''
	lng_code = message.from_user.language_code or ''
	when_int = int(datetime.timestamp(message.date))
	rd=int(await reg_user(message))#create or date
	if rd == when_int:
		snd_msg = REG_OK.get(lng_code, REG_OK['default']).format(user_fn=user_fn)
	elif rd > 0:
		snd_msg = time.strftime('%d.%m.%Y', time.localtime(rd))
	await message.answer(snd_msg)

@dp.message_handler(commands=['mz','мж','мз'])
async def cmd_myzh (message: types.Message):
	msg="🤷"
	user_id = int(message.from_user.id)
	user_fn = message.from_user.first_name or ''
	lng_code = message.from_user.language_code or ''
	when_int = int(datetime.timestamp(message.date))
	rd=int(await reg_user(message))#create or date
	if db_pymysql:
		ii=0
		try:
			
			dbc.execute("SELECT user_id,bio_str,expr_int,expr_str FROM `tg_iris_zarazy` WHERE who_id = %d ORDER BY when_int DESC LIMIT 20;" % int(user_id));
			bz_info = dbc.fetchmany(20)#получить
			all_sicknes=[]#інфа
			count=len(bz_info)
			who=f'🦠 <a href="tg://openmessage?user_id={user_id}">{user_fn}</a>:'
			for row in bz_info:
				ii+=1
				print(row)
				id_user=row["user_id"]
				bio_str=row["bio_str"]
				u_link =f'tg://openmessage?user_id={id_user}'	#fix для любителів мінять його
				expr_str=re.sub(r'.20', r'.',row["expr_str"]) #.2024->.24
				if int(row["expr_int"]) > 1735596000:	#31.12.2024 00:00:00
					expr_str='31.12.24' # Fix? Iris off biogame 31.12.24 :(
				a_href = f'<a href="{u_link}"><code>@{id_user}</code></a>'
				all_sicknes.append(f"{ii}.	{a_href}	➕{bio_str}\n")
			if len(all_sicknes)!=0:
				all_sicknes=f'{who}\n{"".join(all_sicknes)}'
			else:
				all_sicknes='🤷 інфа нема.'
			msg=all_sicknes
		except Exception as Err:
			msg = Err
			print(f"localhost SELECT:{Err}")
	await message.answer(msg, parse_mode=types.ParseMode.HTML)

@dp.message_handler(commands=['ends'])
async def cmd_ends (message: types.Message):
	user_id = int(message.from_user.id)
	user_fn = message.from_user.first_name or ''
	lng_code = message.from_user.language_code or ''
	when_int = int(datetime.timestamp(message.date))
	rd=int(await reg_user(message))#create or date
	msg="<code>Биослет</code>"
	if when_int<1735682400:
		if db_pymysql:
			ii=0
			try:
				dbc.execute(f"SELECT user_id,bio_str,expr_str FROM `tg_iris_zarazy` WHERE who_id = {user_id} AND expr_int < {when_int} ORDER BY `bio_int` DESC, `when_int` DESC LIMIT 20;")
				bz_info = dbc.fetchmany(20)#получить
				all_sicknes=[]#інфа
				count=len(bz_info)
				who=f'🦠 <a href="tg://openmessage?user_id={user_id}">{user_fn}</a>:'
				for row in bz_info:
					print(row)
					ii+=1
					id_user=row["user_id"]
					bio_str=row["bio_str"]
					u_link =f'tg://openmessage?user_id={id_user}'
					a_href = f'<a href="{u_link}"><code>@{id_user}</code></a>'
					all_sicknes.append(f"{ii}.	{a_href}	➕{bio_str}\n")
				if len(all_sicknes)!=0:
					all_sicknes=f'{who}\n{"".join(all_sicknes)}'
				else:
					all_sicknes=msg="<code>Биослет</code>"
				msg=all_sicknes
			except Exception as Err:
				msg = Err
				print(f"localhost SELECT:{Err}")
	await message.answer(msg, parse_mode=types.ParseMode.HTML)

@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
	#await message.answer(emoji="🤷")
	await message.answer('''
•	💬 /chats
•	📃 /code
•	🎲 /dice
''')

@dp.message_handler(commands=['ping'])
async def process_ping_command(message: types.Message):
	await message.reply("PONG!")

@dp.message_handler(commands=['dice','кубик'])
async def cmd_dice(message: types.Message):
	await message.answer_dice(emoji="🎲")

@dp.message_handler(commands=['code','код'])
async def cmd_code(message: types.Message):
	text='''
<code>https://github.com/S1S13AF7/misc_beta_bot</code> – код бота @misc_beta_bot
<code>https://github.com/S1S13AF7/ub4tg</code> – юб. 
<code>https://code.criminallycute.fi/bioeb_org/ub4tg</code> – fork
<code>https://code.criminallycute.fi/S1S13AF7/victims</code>
	'''
	await message.answer(text,parse_mode=types.ParseMode.HTML)

@dp.message_handler(commands=['termux','термукс'])
async def cmd_termux(message: types.Message):
	text='''
<a href="https://f-droid.org/repo/com.termux_1020.apk">Termux_1020</a> / <a 
	href="https://f-droid.org/repo/com.termux.api_51.apk">Termux API</a>

<code>pkg install openssl python3 git termux-api</code>

далі клонуємо із /code
<code>git clone </code>Адреса

<code>cd ub4tg && pip3 install -r requirements.txt</code>

запуск: <code>python3 ubot.py</code>

	'''
	await message.answer(text,parse_mode=types.ParseMode.HTML)

@dp.message_handler(commands=['st','startrek'])
async def cmd_startrek(message: types.Message):
	text='''
Як дивитись «Star Trek»?! Легко і просто береш і дивишся. 
Або якщо цікавить правильний порядок то 
<a href = "https://thestartrekchronologyproject.blogspot.com/2009/09/and-now-conclusion.html">список всіх серій</a>:
<code>https://thestartrekchronologyproject.blogspot.com/2009/09/and-now-conclusion.html</code>

	'''
	await message.answer(text,parse_mode=types.ParseMode.HTML)

@dp.message_handler(commands=['victims','дн'])
async def cmd_victims(message: types.Message):
	text='''
‼️ для бота @bio_attacker_bot

@avocado_victims
	'''
	await message.answer(text,parse_mode=types.ParseMode.HTML)

@dp.message_handler(commands=['chats','чати','чаты','чаті'])
async def cmd_chats(message: types.Message):
	await message.answer('''
•	☕ @misc_chat
•	🦠 @misc_games
•	🗃 @misc_files_v2
•	🥑 @avocado_victims
•	😈 @ub4tg
''')

if __name__ == '__main__':
	executor.start_polling(dp)
