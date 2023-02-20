from aiogram import Bot, types, Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from create_bot import dp, bot, lzt
from misc.keyboards import *
from misc.config import *
from misc.database import *
import arrow
import os
import requests

class UserState(StatesGroup):
	crystal_popol = State()
	lolz_popol = State()
	promocodename = State()

async def start(message: types.Message):
	if not message.chat.username:
		await message.answer("Для пользования ботом установите username в настройках телеграма.")
	if not Users.select().where(Users.user_id == message.chat.id).exists():
		date = arrow.utcnow().format('YYYY-MM-DD')
		Users.create(user_id=message.chat.id, username=message.chat.username, date=date)
		await message.answer("Добро пожаловать.", reply_markup=menuUser)
	else:
		userInfo = Users.select().where(Users.user_id == message.chat.id)[0]
		if userInfo.blocked:
			return await message.answer("Вы заблокированы.")
		Users.update(username=message.chat.username).where(Users.user_id == message.chat.id).execute()
		await message.answer("Добро пожаловать.", reply_markup=menuUser)

async def handler(message: types.Message):
	if not Users.select().where(Users.user_id == message.chat.id).exists():
		return await message.answer("Напиши /start.")
	userInfo = Users.select().where(Users.user_id == message.chat.id)[0]
	if userInfo.blocked:
		return await message.answer("Вы заблокированы.")
	if message.text == '👤 Профиль':
		await message.answer(f'👤Личный кабинет, <b>{message.chat.username}</b>:\n\n💾Логин в БД: <code>@{userInfo.username}</code>\n🦫Ваш ID: <code>{userInfo.user_id}</code>\n📆Дата вступления: <code>{userInfo.date}</code>\n\n💸Баланс: <code>{userInfo.balance} RUB</code>\n💎Количество покупок: <code>{userInfo.buy}</code>', reply_markup=profile_menu, parse_mode='html')

	elif message.text == '🎈 Купить':
		await message.answer('Просмотр разделов:', reply_markup=kategoryes)

@dp.callback_query_handler(lambda c: c.data == 'kategoryes_menu')
async def kategoryes_menu(call: types.CallbackQuery):
	await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
	alls = InlineKeyboardMarkup()
	for razdelss in Razdels.select():
		alls.add(
			InlineKeyboardButton(text=f'{razdelss.name}', callback_data=f'razdel_{razdelss.name}')
		)
	alls.add(
		InlineKeyboardButton(text="Назад", callback_data="back_startrazdel")
	)
	await call.message.answer('Просмотр товара:', reply_markup=alls)

@dp.callback_query_handler(lambda c: 'razdel_' in c.data)
async def razdels(call: types.CallbackQuery):
	name = call.data.split('razdel_')[1]
	razdelInfo = Razdels.select().where(Razdels.name == name)[0]
	broninfo = Tovars.select().where(Tovars.brony == False).where(Tovars.razdel == razdelInfo.name)
	if broninfo.exists():
		dadayf = InlineKeyboardMarkup(row_width=2)
		dadayf.add(
			InlineKeyboardButton(text="Купить 1", callback_data=f"buy_1/{name}"),
			InlineKeyboardButton(text="Купить 2", callback_data=f"buy_2/{name}"),
			InlineKeyboardButton(text="Купить 5", callback_data=f"buy_5/{name}"),
			InlineKeyboardButton(text="Купить 10", callback_data=f"buy_10/{name}"),
			InlineKeyboardButton(text="Назад", callback_data="back_ketegory"),
		)
		await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
									text=f'Просмотр категории <b>{name}</b>\n➖➖➖➖➖➖➖➖➖➖\nОписание товара: <code>{razdelInfo.description}</code>\n\nЦена товара: <code>{razdelInfo.price} RUB</code>\nОстаток товара: <code>{len(Tovars.select().where(Tovars.razdel == name))}</code>\n➖➖➖➖➖➖➖➖➖➖',
									reply_markup=dadayf, parse_mode='html')
	else:
		await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
		await call.message.answer('Нет доступного товара', reply_markup=menuUser)

@dp.callback_query_handler(lambda c: 'buy_' in c.data)
async def buys_(call: types.CallbackQuery):
	type = call.data.split('_')[1].split('/')[0]
	namerazdel = call.data.split('/')[1]
	if type == '1':
		userInfo = Users.select().where(Users.user_id == call.message.chat.id)[0]
		for razdelInfo in Razdels.select().where(Razdels.name == namerazdel):
			if userInfo.balance < int(razdelInfo.price):
				return await call.message.answer('У вас недостаточно средств.', reply_markup=menuUser)
			else:
				for broninfo in Tovars.select().where(Tovars.brony == False).where(Tovars.razdel == razdelInfo.name):
					keeks = InlineKeyboardMarkup(row_width=2)
					keeks.add(
						InlineKeyboardButton(text="Подтвердить", callback_data=f"accept_1/{namerazdel}"),
						InlineKeyboardButton(text="Отмена", callback_data=f"leavee_1/{namerazdel}")
					)
					await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
					Tovars.update(brony=True, user_id=call.message.chat.id).where(Tovars.name == broninfo.name).where(
						Tovars.razdel == namerazdel).execute()
					await call.message.answer(
						f'Вы забронировали товар!\n\nВы собираетесь купить товар: {namerazdel}\n➖➖➖➖➖➖➖➖➖➖\nОписание товара: {razdelInfo.description}\n\nЦена товара: {razdelInfo.price}\n➖➖➖➖➖➖➖➖➖➖\n\nПодтвердите покупку 1 товаров на общую сумму {razdelInfo.price}',
						reply_markup=keeks)
					Users.update(balance=userInfo.balance - int(razdelInfo.price)).where(
						Users.user_id == call.message.chat.id).execute()
	elif type == '2':
		userInfo = Users.select().where(Users.user_id == call.message.chat.id)[0]
		for razdelInfo in Razdels.select().where(Razdels.name == namerazdel):
			if userInfo.balance < int(razdelInfo.price) * 2:
				return await call.message.answer('У вас недостаточно средств.', reply_markup=menuUser)
			else:
				keeks = InlineKeyboardMarkup(row_width=2)
				keeks.add(
					InlineKeyboardButton(text="Подтвердить", callback_data=f"accept_2/{namerazdel}"),
					InlineKeyboardButton(text="Отмена", callback_data=f"leavee_2/{namerazdel}")
				)
				broninfo = Tovars.select().where(Tovars.brony == False).where(Tovars.razdel == razdelInfo.name)[0]
				Tovars.update(brony=True, user_id=call.message.chat.id).where(Tovars.name == broninfo.name).where(
					Tovars.razdel == namerazdel).execute()
				broninfo = Tovars.select().where(Tovars.brony == False).where(Tovars.razdel == razdelInfo.name)[0]
				Tovars.update(brony=True, user_id=call.message.chat.id).where(Tovars.name == broninfo.name).where(
					Tovars.razdel == namerazdel).execute()
				await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
				await call.message.answer(
					f'Вы забронировали товар!\n\nВы собираетесь купить товар: {namerazdel}\n➖➖➖➖➖➖➖➖➖➖\nОписание товара: {razdelInfo.description}\n\nЦена товара: {razdelInfo.price}\n➖➖➖➖➖➖➖➖➖➖\n\nПодтвердите покупку 2 товаров на общую сумму {int(razdelInfo.price) * 2}',
					reply_markup=keeks)
				Users.update(balance=userInfo.balance - int(razdelInfo.price) * 2).where(
					Users.user_id == call.message.chat.id).execute()
	elif type == '5':
		userInfo = Users.select().where(Users.user_id == call.message.chat.id)[0]
		for razdelInfo in Razdels.select().where(Razdels.name == namerazdel):
			if userInfo.balance < int(razdelInfo.price) * 2:
				return await call.message.answer('У вас недостаточно средств.', reply_markup=menuUser)
			else:
				keeks = InlineKeyboardMarkup(row_width=2)
				keeks.add(
					InlineKeyboardButton(text="Подтвердить", callback_data=f"accept_5/{namerazdel}"),
					InlineKeyboardButton(text="Отмена", callback_data=f"leavee_5/{namerazdel}")
				)
				broninfo = Tovars.select().where(Tovars.brony == False).where(Tovars.razdel == razdelInfo.name)[0]
				Tovars.update(brony=True, user_id=call.message.chat.id).where(Tovars.name == broninfo.name).where(
					Tovars.razdel == namerazdel).execute()
				broninfo = Tovars.select().where(Tovars.brony == False).where(Tovars.razdel == razdelInfo.name)[0]
				Tovars.update(brony=True, user_id=call.message.chat.id).where(Tovars.name == broninfo.name).where(
					Tovars.razdel == namerazdel).execute()
				broninfo = Tovars.select().where(Tovars.brony == False).where(Tovars.razdel == razdelInfo.name)[0]
				Tovars.update(brony=True, user_id=call.message.chat.id).where(Tovars.name == broninfo.name).where(
					Tovars.razdel == namerazdel).execute()
				broninfo = Tovars.select().where(Tovars.brony == False).where(Tovars.razdel == razdelInfo.name)[0]
				Tovars.update(brony=True, user_id=call.message.chat.id).where(Tovars.name == broninfo.name).where(
					Tovars.razdel == namerazdel).execute()
				broninfo = Tovars.select().where(Tovars.brony == False).where(Tovars.razdel == razdelInfo.name)[0]
				Tovars.update(brony=True, user_id=call.message.chat.id).where(Tovars.name == broninfo.name).where(
					Tovars.razdel == namerazdel).execute()
				await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
				await call.message.answer(
					f'Вы забронировали товар!\n\nВы собираетесь купить товар: {namerazdel}\n➖➖➖➖➖➖➖➖➖➖\nОписание товара: {razdelInfo.description}\n\nЦена товара: {razdelInfo.price}\n➖➖➖➖➖➖➖➖➖➖\n\nПодтвердите покупку 5 товаров на общую сумму {int(razdelInfo.price) * 5}',
					reply_markup=keeks)
				Users.update(balance=userInfo.balance - int(razdelInfo.price) * 5).where(
					Users.user_id == call.message.chat.id).execute()
	elif type == '10':
		userInfo = Users.select().where(Users.user_id == call.message.chat.id)[0]
		for razdelInfo in Razdels.select().where(Razdels.name == namerazdel):
			if userInfo.balance < int(razdelInfo.price) * 10:
				return await call.message.answer('У вас недостаточно средств.', reply_markup=menuUser)
			else:
				keeks = InlineKeyboardMarkup(row_width=2)
				keeks.add(
					InlineKeyboardButton(text="Подтвердить", callback_data=f"accept_10/{namerazdel}"),
					InlineKeyboardButton(text="Отмена", callback_data=f"leavee_10/{namerazdel}")
				)
				broninfo = Tovars.select().where(Tovars.brony == False).where(Tovars.razdel == razdelInfo.name)[0]
				Tovars.update(brony=True, user_id=call.message.chat.id).where(Tovars.name == broninfo.name).where(
					Tovars.razdel == namerazdel).execute()
				broninfo = Tovars.select().where(Tovars.brony == False).where(Tovars.razdel == razdelInfo.name)[0]
				Tovars.update(brony=True, user_id=call.message.chat.id).where(Tovars.name == broninfo.name).where(
					Tovars.razdel == namerazdel).execute()
				broninfo = Tovars.select().where(Tovars.brony == False).where(Tovars.razdel == razdelInfo.name)[0]
				Tovars.update(brony=True, user_id=call.message.chat.id).where(Tovars.name == broninfo.name).where(
					Tovars.razdel == namerazdel).execute()
				broninfo = Tovars.select().where(Tovars.brony == False).where(Tovars.razdel == razdelInfo.name)[0]
				Tovars.update(brony=True, user_id=call.message.chat.id).where(Tovars.name == broninfo.name).where(
					Tovars.razdel == namerazdel).execute()
				broninfo = Tovars.select().where(Tovars.brony == False).where(Tovars.razdel == razdelInfo.name)[0]
				Tovars.update(brony=True, user_id=call.message.chat.id).where(Tovars.name == broninfo.name).where(
					Tovars.razdel == namerazdel).execute()
				broninfo = Tovars.select().where(Tovars.brony == False).where(Tovars.razdel == razdelInfo.name)[0]
				Tovars.update(brony=True, user_id=call.message.chat.id).where(Tovars.name == broninfo.name).where(
					Tovars.razdel == namerazdel).execute()
				broninfo = Tovars.select().where(Tovars.brony == False).where(Tovars.razdel == razdelInfo.name)[0]
				Tovars.update(brony=True, user_id=call.message.chat.id).where(Tovars.name == broninfo.name).where(
					Tovars.razdel == namerazdel).execute()
				broninfo = Tovars.select().where(Tovars.brony == False).where(Tovars.razdel == razdelInfo.name)[0]
				Tovars.update(brony=True, user_id=call.message.chat.id).where(Tovars.name == broninfo.name).where(
					Tovars.razdel == namerazdel).execute()
				broninfo = Tovars.select().where(Tovars.brony == False).where(Tovars.razdel == razdelInfo.name)[0]
				Tovars.update(brony=True, user_id=call.message.chat.id).where(Tovars.name == broninfo.name).where(
					Tovars.razdel == namerazdel).execute()
				broninfo = Tovars.select().where(Tovars.brony == False).where(Tovars.razdel == razdelInfo.name)[0]
				Tovars.update(brony=True, user_id=call.message.chat.id).where(Tovars.name == broninfo.name).where(
					Tovars.razdel == namerazdel).execute()
				await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
				await call.message.answer(
					f'Вы забронировали товар!\n\nВы собираетесь купить товар: {namerazdel}\n➖➖➖➖➖➖➖➖➖➖\nОписание товара: {razdelInfo.description}\n\nЦена товара: {razdelInfo.price}\n➖➖➖➖➖➖➖➖➖➖\n\nПодтвердите покупку 10 товаров на общую сумму {int(razdelInfo.price) * 10}',
					reply_markup=keeks)
				Users.update(balance=userInfo.balance - int(razdelInfo.price) * 10).where(
					Users.user_id == call.message.chat.id).execute()

@dp.callback_query_handler(lambda c: 'leavee_' in c.data)
async def leavee(call: types.CallbackQuery):
	type = call.data.split('_')[1].split('/')[0]
	if type == '1':
		await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
		userInfo = Users.select().where(Users.user_id == call.message.chat.id)[0]
		razdelInfo = Razdels.select().where(Razdels.price)[0]
		broninfo = Tovars.select().where(Tovars.user_id == call.message.chat.id)[0]
		Tovars.update(brony=False, user_id=0).where(Tovars.name == broninfo.name).where(
			Tovars.user_id == call.message.chat.id).execute()
		Users.update(balance=userInfo.balance + int(razdelInfo.price)).where(
			Users.user_id == call.message.chat.id).execute()
		await call.message.answer('Бронь отменена', reply_markup=menuUser)
	elif type == '2':
		await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
		userInfo = Users.select().where(Users.user_id == call.message.chat.id)[0]
		razdelInfo = Razdels.select().where(Razdels.price)[0]
		broninfo = Tovars.select().where(Tovars.user_id == call.message.chat.id)[0]
		Tovars.update(brony=False, user_id=0).where(Tovars.name == broninfo.name).where(
			Tovars.user_id == call.message.chat.id).execute()
		broninfo = Tovars.select().where(Tovars.user_id == call.message.chat.id)[0]
		Tovars.update(brony=False, user_id=0).where(Tovars.name == broninfo.name).where(
			Tovars.user_id == call.message.chat.id).execute()
		Users.update(balance=userInfo.balance + int(razdelInfo.price * 2)).where(
			Users.user_id == call.message.chat.id).execute()
		await call.message.answer('Бронь отменена', reply_markup=menuUser)
	elif type == '5':
		await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
		userInfo = Users.select().where(Users.user_id == call.message.chat.id)[0]
		razdelInfo = Razdels.select().where(Razdels.price)[0]
		broninfo = Tovars.select().where(Tovars.user_id == call.message.chat.id)[0]
		Tovars.update(brony=False, user_id=0).where(Tovars.name == broninfo.name).where(
			Tovars.user_id == call.message.chat.id).execute()
		broninfo = Tovars.select().where(Tovars.user_id == call.message.chat.id)[0]
		Tovars.update(brony=False, user_id=0).where(Tovars.name == broninfo.name).where(
			Tovars.user_id == call.message.chat.id).execute()
		broninfo = Tovars.select().where(Tovars.user_id == call.message.chat.id)[0]
		Tovars.update(brony=False, user_id=0).where(Tovars.name == broninfo.name).where(
			Tovars.user_id == call.message.chat.id).execute()
		broninfo = Tovars.select().where(Tovars.user_id == call.message.chat.id)[0]
		Tovars.update(brony=False, user_id=0).where(Tovars.name == broninfo.name).where(
			Tovars.user_id == call.message.chat.id).execute()
		broninfo = Tovars.select().where(Tovars.user_id == call.message.chat.id)[0]
		Tovars.update(brony=False, user_id=0).where(Tovars.name == broninfo.name).where(
			Tovars.user_id == call.message.chat.id).execute()
		Users.update(balance=userInfo.balance + int(razdelInfo.price * 5)).where(
			Users.user_id == call.message.chat.id).execute()
		await call.message.answer('Бронь отменена', reply_markup=menuUser)
	elif type == '10':
		await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
		userInfo = Users.select().where(Users.user_id == call.message.chat.id)[0]
		razdelInfo = Razdels.select().where(Razdels.price)[0]
		broninfo = Tovars.select().where(Tovars.user_id == call.message.chat.id)[0]
		Tovars.update(brony=False, user_id=0).where(Tovars.name == broninfo.name).where(
			Tovars.user_id == call.message.chat.id).execute()
		broninfo = Tovars.select().where(Tovars.user_id == call.message.chat.id)[0]
		Tovars.update(brony=False, user_id=0).where(Tovars.name == broninfo.name).where(
			Tovars.user_id == call.message.chat.id).execute()
		broninfo = Tovars.select().where(Tovars.user_id == call.message.chat.id)[0]
		Tovars.update(brony=False, user_id=0).where(Tovars.name == broninfo.name).where(
			Tovars.user_id == call.message.chat.id).execute()
		broninfo = Tovars.select().where(Tovars.user_id == call.message.chat.id)[0]
		Tovars.update(brony=False, user_id=0).where(Tovars.name == broninfo.name).where(
			Tovars.user_id == call.message.chat.id).execute()
		broninfo = Tovars.select().where(Tovars.user_id == call.message.chat.id)[0]
		Tovars.update(brony=False, user_id=0).where(Tovars.name == broninfo.name).where(
			Tovars.user_id == call.message.chat.id).execute()
		broninfo = Tovars.select().where(Tovars.user_id == call.message.chat.id)[0]
		Tovars.update(brony=False, user_id=0).where(Tovars.name == broninfo.name).where(
			Tovars.user_id == call.message.chat.id).execute()
		broninfo = Tovars.select().where(Tovars.user_id == call.message.chat.id)[0]
		Tovars.update(brony=False, user_id=0).where(Tovars.name == broninfo.name).where(
			Tovars.user_id == call.message.chat.id).execute()
		broninfo = Tovars.select().where(Tovars.user_id == call.message.chat.id)[0]
		Tovars.update(brony=False, user_id=0).where(Tovars.name == broninfo.name).where(
			Tovars.user_id == call.message.chat.id).execute()
		broninfo = Tovars.select().where(Tovars.user_id == call.message.chat.id)[0]
		Tovars.update(brony=False, user_id=0).where(Tovars.name == broninfo.name).where(
			Tovars.user_id == call.message.chat.id).execute()
		broninfo = Tovars.select().where(Tovars.user_id == call.message.chat.id)[0]
		Tovars.update(brony=False, user_id=0).where(Tovars.name == broninfo.name).where(
			Tovars.user_id == call.message.chat.id).execute()
		Users.update(balance=userInfo.balance + int(razdelInfo.price * 10)).where(
			Users.user_id == call.message.chat.id).execute()
		await call.message.answer('Бронь отменена', reply_markup=menuUser)

@dp.callback_query_handler(lambda c: 'accept_' in c.data)
async def accept_(call: types.CallbackQuery):
	type = call.data.split('_')[1].split('/')[0]
	namerazdel = call.data.split('/')[1]
	if type == '1':
		userInfo = Users.select().where(Users.user_id == call.message.chat.id)[0]
		razdelInfo = Razdels.select().where(Razdels.price)[0]
		broninfo = Tovars.select().where(Tovars.user_id == call.message.chat.id)[0]
		with open(f'@{call.message.chat.username}.txt', 'w+') as file:
			file.write(f'{broninfo.name}')
		await bot.send_document(call.message.chat.id, open(f'@{call.message.chat.username}.txt', 'rb'))
		await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
		Users.update(buy=Users.buy + 1).where(Users.user_id == call.message.chat.id).execute()
		broninfo.delete_instance()
		os.remove(f"@{call.message.chat.username}.txt")
	elif type == '2':
		userInfo = Users.select().where(Users.user_id == call.message.chat.id)[0]
		razdelInfo = Razdels.select().where(Razdels.price)[0]
		broninfo = Tovars.select().where(Tovars.user_id == call.message.chat.id)[0]
		broninfo1 = Tovars.select().where(Tovars.user_id == call.message.chat.id)[1]
		with open(f'@{call.message.chat.username}.txt', 'w+') as file:
			file.write(broninfo.name + '\n' + broninfo1.name)
		await bot.send_document(call.message.chat.id, open(f'@{call.message.chat.username}.txt', 'rb'))
		await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
		Users.update(buy=Users.buy + 2).where(Users.user_id == call.message.chat.id).execute()
		broninfo.delete_instance(), broninfo1.delete_instance()
		os.remove(f"@{call.message.chat.username}.txt")
	elif type == '5':
		userInfo = Users.select().where(Users.user_id == call.message.chat.id)[0]
		razdelInfo = Razdels.select().where(Razdels.price)[0]
		broninfo = Tovars.select().where(Tovars.user_id == call.message.chat.id)[0]
		broninfo1 = Tovars.select().where(Tovars.user_id == call.message.chat.id)[1]
		broninfo2 = Tovars.select().where(Tovars.user_id == call.message.chat.id)[2]
		broninfo3 = Tovars.select().where(Tovars.user_id == call.message.chat.id)[3]
		broninfo4 = Tovars.select().where(Tovars.user_id == call.message.chat.id)[4]
		with open(f'@{call.message.chat.username}.txt', 'w+') as file:
			file.write(broninfo.name + '\n' + broninfo1.name)
			file.write('\n' + broninfo2.name + '\n' + broninfo3.name)
			file.write('\n' + broninfo4.name)
		await bot.send_document(call.message.chat.id, open(f'@{call.message.chat.username}.txt', 'rb'))
		await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
		Users.update(buy=Users.buy + 5).where(Users.user_id == call.message.chat.id).execute()
		broninfo.delete_instance(), broninfo1.delete_instance(), broninfo2.delete_instance(), broninfo3.delete_instance(), broninfo4.delete_instance()
		os.remove(f"@{call.message.chat.username}.txt")
	elif type == '10':
		userInfo = Users.select().where(Users.user_id == call.message.chat.id)[0]
		razdelInfo = Razdels.select().where(Razdels.price)[0]
		broninfo = Tovars.select().where(Tovars.user_id == call.message.chat.id)[0]
		broninfo1 = Tovars.select().where(Tovars.user_id == call.message.chat.id)[1]
		broninfo2 = Tovars.select().where(Tovars.user_id == call.message.chat.id)[2]
		broninfo3 = Tovars.select().where(Tovars.user_id == call.message.chat.id)[3]
		broninfo4 = Tovars.select().where(Tovars.user_id == call.message.chat.id)[4]
		broninfo5 = Tovars.select().where(Tovars.user_id == call.message.chat.id)[5]
		broninfo6 = Tovars.select().where(Tovars.user_id == call.message.chat.id)[6]
		broninfo7 = Tovars.select().where(Tovars.user_id == call.message.chat.id)[7]
		broninfo8 = Tovars.select().where(Tovars.user_id == call.message.chat.id)[8]
		broninfo9 = Tovars.select().where(Tovars.user_id == call.message.chat.id)[9]
		with open(f'@{call.message.chat.username}.txt', 'w+') as file:
			file.write(broninfo.name + '\n' + broninfo1.name)
			file.write('\n' + broninfo2.name + '\n' + broninfo3.name)
			file.write('\n' + broninfo4.name + '\n' + broninfo5.name)
			file.write('\n' + broninfo6.name + '\n' + broninfo7.name)
			file.write('\n' + broninfo8.name + '\n' + broninfo9.name)
		await bot.send_document(call.message.chat.id, open(f'@{call.message.chat.username}.txt', 'rb'))
		await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
		Users.update(buy=Users.buy + 10).where(Users.user_id == call.message.chat.id).execute()
		broninfo.delete_instance(), broninfo1.delete_instance(), broninfo2.delete_instance(), broninfo3.delete_instance(), broninfo4.delete_instance()
		broninfo5.delete_instance(), broninfo6.delete_instance(), broninfo7.delete_instance(), broninfo8.delete_instance(), broninfo9.delete_instance()
		os.remove(f"@{call.message.chat.username}.txt")

@dp.callback_query_handler(lambda c: c.data == 'popolnenie')
async def popolnenie(call: types.CallbackQuery):
	await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
	await call.message.answer('Выберите способ пополнения:', reply_markup=payments)

@dp.callback_query_handler(lambda c: 'payment' in c.data)
async def payment(call: types.CallbackQuery):
	type = call.data.split('_')[1]
	if type == 'crystal':
		await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
		await call.message.answer('Введите сумму пополнения в рублях:', reply_markup=back_)
		await UserState.crystal_popol.set()
	elif type == 'lolz':
		await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
		await call.message.answer('Введите сумму пополнения в рублях:', reply_markup=back_)
		await UserState.lolz_popol.set()

@dp.message_handler(state=UserState.lolz_popol)
async def lolz_popol(message: types.Message, state: FSMContext):
	if message.text.isdigit():
		link = lzt.get_link(amount=message.text, comment=lzt.get_random_string())
		comment = lzt.get_random_string()
		pay = types.InlineKeyboardMarkup()
		pay.add(
			types.InlineKeyboardButton(text="💳 Оплатить", url=link)
		).add(
			types.InlineKeyboardButton(text="🔄 Проверить оплату", callback_data=f"LZTcheck{comment}/{message.text}")
		)
		await message.answer(f'🧾Создали счёт. Не забудь нажать на кнопку сразу после оплаты!\n📨Способ пополнения: 🪐Lolz\n💰Сумма: {message.text} руб.', reply_markup=pay)
		await state.reset_state(with_data=False)
	else:
		await message.answer("Введите цифры.")

@dp.callback_query_handler(lambda c: 'LZTcheck' in c.data)
async def lzt_check(call: types.CallbackQuery):
	comment = call.data.split('LZTcheck')[-1].split("/")[0]
	amount = call.data.split('LZTcheck')[-1].split("/")[1]
	status = lzt.check_payment(amount=amount, comment=comment)
	if status:
		bot.delete_message(call.message.chat.id, call.message.message_id)
		userInfo = Users.select().where(Users.user_id == call.message.chat.id)[0]
		old_amount = userInfo.balance
		Users.update(balance=old_amount + int(amount)).where(Users.user_id == call.message.chat.id).execute()
		await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
		await bot.send_message(log_chat, f"Пользователь @{call.message.chat.id} пополнил счет на {amount} рублей.")
		await call.message.answer("Оплата найдена!\nНа ваш баланс пополнено {amount} рублей.")
	else:
		await call.answer('Оплата не найдена.', show_alert=True)

@dp.message_handler(state=UserState.crystal_popol)
async def crystal_popol(message: types.Message, state: FSMContext):
	if message.text.isdigit():
		r = requests.get(
			f'https://api.crystalpay.ru/v1/?s={api}&n={kassa}&o=invoice-create&amount={message.text}&lifetime=60').json()
		id_c = r['id']
		menu = types.InlineKeyboardMarkup()
		menu.add(
			types.InlineKeyboardButton(text="Перейти к оплате", url=r['url'])
		).add(
			types.InlineKeyboardButton(text="✅Проверить оплату", callback_data=f"CRYSTcheck{id_c}/{message.text}")
		)
		await message.answer(f'🧾Создали счёт. Не забудь нажать на кнопку сразу после оплаты!\n⏱Время на оплату: 60 минут!\n\n📨Способ пополнения: 💎CrystalPay\n💰Сумма: {message.text} руб.', reply_markup=menu)
		await state.reset_state(with_data=False)
	else:
		await message.answer("Введите цифры, пожалуйста.")

@dp.callback_query_handler(lambda c: 'CRYSTcheck' in c.data)
async def check(call: types.CallbackQuery):
	id = call.data.split('CRYSTcheck')[-1].split("/")[0]
	amount = call.data.split('CRYSTcheck')[-1].split("/")[1]
	r = requests.get(f'https://api.crystalpay.ru/v1/?s={api}&n={kassa}&o=receipt-check&i={id}').json()
	if r["state"] == "payed":
		userInfo = Users.select().where(Users.user_id == call.message.chat.id)[0]
		old_amount = userInfo.balance
		Users.update(balance=old_amount + int(amount)).where(Users.user_id == call.message.chat.id).execute()
		await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
		await call.message.answer(f"<code>На ваш баланс пополнено {amount} рублей.</code>", reply_markup=menuUser,
								  parse_mode='html')
		await call.bot.send_message(log_chat, f"@{call.message.chat.username} Пополнил счёт на {amount} рублей🔔")
	else:
		await call.answer('Оплата не найдена.', show_alert=True)

@dp.callback_query_handler(lambda c: c.data == 'back_main', state="*")
async def back_main(call: types.CallbackQuery, state: FSMContext):
	await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
	await state.finish()
	userInfo = Users.select().where(Users.user_id == call.message.chat.id)[0]
	if userInfo.blocked:
		return await call.message.answer("Вы заблокированы.")
	else:
		await call.message.answer(f'👤Личный кабинет, <b>{call.message.chat.username}</b>:\n\n💾Логин в БД: <code>@{userInfo.username}</code>\n🦫Ваш ID: <code>{userInfo.user_id}</code>\n📆Дата вступления: <code>{userInfo.date}</code>\n\n💸Баланс: <code>{userInfo.balance} RUB</code>\n💎Количество покупок: <code>{userInfo.buy}</code>', reply_markup=profile_menu, parse_mode='html')

@dp.callback_query_handler(lambda c: c.data == 'back_promocode', state="*")
async def back_main(call: types.CallbackQuery, state: FSMContext):
	await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
	await state.finish()

@dp.callback_query_handler(lambda c: 'back' in c.data)
async def back(call: types.CallbackQuery, state: FSMContext):
	type = call.data.split('_')[1]
	if type =='profile':
		await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
		userInfo = Users.select().where(Users.user_id == call.message.chat.id)[0]
		if userInfo.blocked:
			return await call.message.answer("Вы заблокированы.")
		else:
			await call.message.answer(f'👤Личный кабинет, <b>{call.message.chat.username}</b>:\n\n💾Логин в БД: <code>@{userInfo.username}</code>\n🦫Ваш ID: <code>{userInfo.user_id}</code>\n📆Дата вступления: <code>{userInfo.date}</code>\n\n💸Баланс: <code>{userInfo.balance} RUB</code>\n💎Количество покупок: <code>{userInfo.buy}</code>', reply_markup=profile_menu, parse_mode='html')
	elif type == 'startrazdel':
		await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
		await call.message.answer('Просмотр разделов:', reply_markup=kategoryes)
	elif type == 'ketegory':
		alls = InlineKeyboardMarkup()
		for razdelss in Razdels.select():
			alls.add(
				InlineKeyboardButton(text=f'{razdelss.name}', callback_data=f'razdel_{razdelss.name}')
			)
		await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Просмотр разделов:', reply_markup=alls)

@dp.callback_query_handler(lambda c: c.data == 'promocode')
async def promocode(call: types.CallbackQuery):
	await call.message.answer('Введите промокод:', reply_markup=back_promo)
	await UserState.promocodename.set()

@dp.message_handler(state=UserState.promocodename)
async def promocode2(message: types.Message, state: FSMContext):
	if not Promocode.select().where(Promocode.name == message.text).exists():
		await message.answer('Нету такого промокода.')
		await state.reset_state(with_data=False)
	else:
		userInfo = Users.select().where(Users.user_id == message.chat.id)[0]
		if userInfo.used == True:
			await message.answer('Вы уже использовали этот промокод.')
			await state.reset_state(with_data=False)
		else:
			promoInfo = Promocode.select().where(Promocode.name == message.text)[0]
			if promoInfo.used > promoInfo.quantity or promoInfo.used == promoInfo.quantity:
				await message.answer('Ты опоздал(')
				promoInfo.delete_instance()
				Users.update(used=False).where(Users.user_id).execute()
				await state.reset_state(with_data=False)
			else:
				promoInfo = Promocode.select().where(Promocode.name == message.text)[0]
				userInfo = Users.select().where(Users.user_id == message.chat.id)[0]
				Users.update(balance=userInfo.balance+int(promoInfo.amount), used=True).where(Users.user_id == message.chat.id).execute()
				Promocode.update(used=promoInfo.used+1).where(Promocode.name == message.text).execute()
				await message.answer('Успешно!', reply_markup=menuUser)
				await state.reset_state(with_data=False)

def register_handlers_user(dp: Dispatcher):
	dp.register_message_handler(start, commands=['start'])
	dp.register_message_handler(handler)