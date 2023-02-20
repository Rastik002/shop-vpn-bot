from aiogram import Bot, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from create_bot import dp, bot
from misc.keyboards import *
from misc.config import *
from misc.database import *
import os

class AdminState(StatesGroup):
	blocked = State()
	mailing = State()
	addbalance = State()
	addbalance2 = State()
	delbalance = State()
	delbalance2 = State()
	add_ketegory2 = State()
	add_ketegory3 = State()
	add_ketegory4 = State()
	del_ketegory2 = State()
	addtovars_ = State()
	installpromocode2 = State()
	installpromocode3 = State()
	installpromocode4 = State()

@dp.message_handler(commands=['adm', 'admin'])
async def admin(message: types.Message):
	if message.chat.id not in admins:
		pass
	else:
		await message.answer("Админ меню", reply_markup=menuAdmin)

@dp.callback_query_handler(lambda c: c.data == 'add_tovar')
async def add_tovars(call: types.CallbackQuery):
	await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
	razdels = InlineKeyboardMarkup()
	for razdelss in Razdels.select():
		razdels.add(
			InlineKeyboardButton(text=f'{razdelss.name}', callback_data=f'addtovars_{razdelss.name}')
		)
	razdels.add(
		InlineKeyboardButton(text="Отмена", callback_data="cancel")
	)
	await call.message.answer('Выберите раздел куда добавить товар:', reply_markup=razdels)

@dp.callback_query_handler(lambda c: 'addtovars' in c.data)
async def addtovars_2(call: types.CallbackQuery, state: FSMContext):
	name = call.data.split('addtovars_')[1]
	await state.update_data(namerazdel=name)
	await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
	await call.message.answer('Скиньте отправьте мне txt файл с товаром:', reply_markup=menu)
	await AdminState.addtovars_.set()

@dp.message_handler(content_types=['document'], state=AdminState.addtovars_)
async def addtovars_(message: types.Message, state: FSMContext):
	file_info = await bot.get_file(message.document.file_id)
	namefile = message.document.file_name.split('.txt')[0]
	await message.answer('Скачиваю товар..')
	await message.document.download(destination_file=f"{namefile}" + ".txt")
	data = await state.get_data()
	namerazdel = data['namerazdel']
	a = await tovar2s_(namefile, namerazdel)
	await state.reset_state(with_data=False)
	if a['success']:
		await message.answer('Товар загружен.', reply_markup=menuAdmin)
	else:
		await message.answer('Товар не был загружен..', reply_markup=menuAdmin)
	os.remove(f"{namefile}" + ".txt")

async def tovar2s_(namefile, namerazdel):
	try:
		with open(f'{namefile}.txt', 'r') as f:
			for i in f:
				if '\n' in i:
					tovar = i.split('\n')[0]
				else:
					tovar = i
				tovarInfo = Razdels.select().where(Razdels.name == namerazdel)[0]
				Tovars.create(name=tovar, price=tovarInfo.price, razdel=namerazdel)
			return {'success': True}
	except:
		return {'success': False}

@dp.callback_query_handler(lambda c: c.data == 'del_tovar')
async def del_tovars(call: types.CallbackQuery):
	await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
	razdels = InlineKeyboardMarkup()
	for razdelss in Razdels.select():
		razdels.add(
			InlineKeyboardButton(text=f'{razdelss.name}', callback_data=f'deltovars_{razdelss.name}')
		)
	razdels.add(
		InlineKeyboardButton(text="Отмена", callback_data="cancel")
	)
	await call.message.answer('Выберите раздел откуда удалить товар:', reply_markup=razdels)

@dp.callback_query_handler(lambda c: 'deltovars' in c.data)
async def deltovars_2(call: types.CallbackQuery, state: FSMContext):
	name = call.data.split('deltovars_')[1]
	await state.update_data(dels_namerazdel=name)
	await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
	await call.message.answer(f'Удалить все товары из раздела: {name}?', reply_markup=menu_delstovar)

@dp.callback_query_handler(lambda c: 'dels' in c.data)
async def deltovars_next(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	tovarInfo = Tovars.select().where(Tovars.razdel == data['dels_namerazdel'])
	for i in tovarInfo:
		Tovars.delete_instance(i)
	await call.message.answer('Товар удален.', reply_markup=menuAdmin)

@dp.callback_query_handler(lambda c: c.data == 'stats')
async def stats(call: types.CallbackQuery):
	info = Users.select()
	sum = 0
	for i in info:
		sum+= i.buy
		await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Всего в базе <code>{len(Users.select())}</code> пользователей.\nВсего покупок: <code>{sum}</code>\nАккаунтов в базе: <code>{len(Tovars.select())}</code>", reply_markup=menuAdmin, parse_mode='html')

@dp.callback_query_handler(lambda c: c.data == 'mailing')
async def mailing(call: types.CallbackQuery, state: FSMContext):
	await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
	await call.message.answer('Введите текст рассылки:', reply_markup=menu)
	await AdminState.mailing.set()

@dp.message_handler(state=AdminState.mailing, content_types=types.ContentType.ANY)
async def mailing(message: types.Message, state: FSMContext):
	await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
	await message.answer("Рассылка начата.")
	success = 0
	errors = 0
	for user in Users.select():
		try:
			success += 1
			if types.ContentType.TEXT == message.content_type:
				await bot.send_message(user.user_id, message.text)

			elif types.ContentType.PHOTO == message.content_type:
				await bot.send_photo(chat_id=user.user_id, photo=message.photo[-1].file_id, caption=message.html_text if message.caption else None)

			elif types.ContentType.VIDEO == message.content_type:
				await bot.send_video(chat_id=user.user_id, video=message.video.file_id, caption=message.html_text if message.caption else None)

			elif types.ContentType.ANIMATION == message.content_type:
				await bot.send_animation(chat_id=user.user_id, animation=message.animation.file_id, caption=message.html_text if message.caption else None)

			elif types.ContentType.STICKER == message.content_type:
				await bot.send_sticker(chat_id=user.user_id, sticker=message.sticker.file_id)
		except:
			errors += 1
	await message.answer(f"Рассылка окончена.\n\nУспешно: {success}\nОшибок: {errors}", reply_markup=menuAdmin)
	await state.reset_state(with_data=False)

@dp.callback_query_handler(lambda c: c.data == 'blocked')
async def blocked(call: types.CallbackQuery, state: FSMContext):
	await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
	await call.message.answer('Введите @username пользователя:', reply_markup=menu)
	await AdminState.blocked.set()

@dp.message_handler(state=AdminState.blocked)
async def blocked(message: types.Message, state: FSMContext):
	username = message.text.replace('@', "")
	if not Users.select().where(Users.username == username).exists():
		await state.reset_state(with_data=False)
		return await message.answer("Это че? Это где?.", reply_markup=menuAdmin)
	userInfo = Users.select().where(Users.username == username)[0]
	if userInfo.blocked:
		await message.answer('Пользователя уебали. Жалею пользователя')
		await message.answer("Пожалел.", reply_markup=menuAdmin)
		await state.reset_state(with_data=False)
	else:
		await message.answer('Ебу пользователя..')
		await message.answer("Выебал..", reply_markup=menuAdmin)
	Users.update(blocked=not userInfo.blocked).where(Users.username == username).execute()
	await state.reset_state(with_data=False)

@dp.callback_query_handler(lambda c: c.data == 'add_balance')
async def addbalance(call: types.CallbackQuery):
	await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
	await call.message.answer("Введите @username пользователя.", reply_markup=menu)
	await AdminState.addbalance.set()

@dp.message_handler(state=AdminState.addbalance)
async def addbalance2(message: types.Message, state: FSMContext):
	username = message.text.replace('@', "")
	await state.update_data(username=username)
	if not Users.select().where(Users.username == username).exists():
		await state.reset_state(with_data=False)
		return await message.answer("Это че? Это где?.", reply_markup=menuAdmin)
	await message.answer("Сколько баланса добавить?", reply_markup=menu)
	await AdminState.addbalance2.set()

@dp.message_handler(state=AdminState.addbalance2)
async def addbalance3(message: types.Message, state: FSMContext):
	if message.text.isdigit():
		data = await state.get_data()
		userInfo = Users.select().where(Users.username == {data['username']})[0]
		Users.update(balance=userInfo.balance+int(message.text)).where(Users.username == userInfo.username).execute()
		await message.answer(f"<code>Добавил пользователю </code>@{userInfo.username}, <code>{message.text} рублей.</code>", reply_markup=menuAdmin, parse_mode='html')
		await bot.send_message(userInfo.user_id, f"<code>На ваш баланс пополнено {message.text} рублей.</code>", parse_mode='html')
		await state.reset_state(with_data=False)
	else:
		await message.answer("Введите цифры, пожалуйста.", reply_markup=menuAdmin)
		await state.reset_state(with_data=False)

@dp.callback_query_handler(lambda c: c.data == 'del_balance')
async def delbalance(call: types.CallbackQuery):
	await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
	await call.message.answer("Введите @username пользователя.", reply_markup=menu)
	await AdminState.delbalance.set()

@dp.message_handler(state=AdminState.delbalance)
async def delbalance2(message: types.Message, state: FSMContext):
	username = message.text.replace('@', "")
	await state.update_data(username=username)
	if not Users.select().where(Users.username == username).exists():
		await state.reset_state(with_data=False)
		return await message.answer("Это че? Это где?.", reply_markup=menuAdmin)
	await message.answer("Сколько баланса убрать?", reply_markup=menu)
	await AdminState.delbalance2.set()

@dp.message_handler(state=AdminState.delbalance2)
async def delbalance2(message: types.Message, state: FSMContext):
	if message.text.isdigit():
		data = await state.get_data()
		userInfo = Users.select().where(Users.username == {data['username']})[0]
		Users.update(balance=userInfo.balance-int(message.text)).where(Users.username == userInfo.username).execute()
		await message.answer(f"<code>Спиздил у пользователя </code>@{userInfo.username}, <code>{message.text} рублей.</code>", reply_markup=menuAdmin, parse_mode='html')
		await state.reset_state(with_data=False)
	else:
		await message.answer("Введите цифры, пожалуйста.", reply_markup=menuAdmin)
		await state.reset_state(with_data=False)

@dp.callback_query_handler(lambda c: c.data == 'add_ketegory')
async def add_ketegory(call: types.CallbackQuery):
	await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
	await call.message.answer('Введите название раздела:', reply_markup=menu)
	await AdminState.add_ketegory2.set()

@dp.message_handler(state=AdminState.add_ketegory2)
async def add_ketegory2(message: types.Message, state: FSMContext):
	await message.answer('Введите описание товара:', reply_markup=menu)
	await state.update_data(name=message.text)
	await AdminState.add_ketegory3.set()

@dp.message_handler(state=AdminState.add_ketegory3)
async def add_ketegory3(message: types.Message, state: FSMContext):
	await message.answer('Введите цену:', reply_markup=menu)
	await state.update_data(description=message.text)
	await AdminState.add_ketegory4.set()

@dp.message_handler(state=AdminState.add_ketegory4)
async def add_ketegory4(message: types.Message, state: FSMContext):
	if message.text.isdigit():
		data = await state.get_data()
		if not Razdels.select().where(Razdels.name == data['name']):
			Razdels.create(name=(data['name']), description=(data['description']), price=message.text)
			await message.answer('Добавил <3', reply_markup=menuAdmin)
			await state.reset_state(with_data=False)
		else:
			await message.answer('Такой раздел уже существует.', reply_markup=menuAdmin)
			await state.reset_state(with_data=False)
	else:
		await message.answer('Введите цифры')

@dp.callback_query_handler(lambda c: c.data == 'del_ketegory')
async def del_ketegory(call: types.CallbackQuery):
	alls = InlineKeyboardMarkup()
	for razdelss in Razdels.select():
		alls.add(
			InlineKeyboardButton(text=f'{razdelss.name}', callback_data=f'delrazdel_{razdelss.name}')
		)
	await call.message.answer('Доступные разделы:', reply_markup=alls)

@dp.callback_query_handler(lambda c: 'delrazdel_' in c.data)
async def delrazdel(call: types.CallbackQuery, state: FSMContext):
	name = call.data.split('razdel_')[1]
	await state.update_data(dels_razdel=name)
	await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
	await call.message.answer(f'Удалить раздел {name}?', reply_markup=menu_delsrazdel)

@dp.callback_query_handler(lambda c: c.data == 'razdel_delete')
async def razdel_delete(call: types.CallbackQuery, state: FSMContext):
	data = await state.get_data()
	RazdelsInfo = Razdels.select().where(Razdels.name == data['dels_razdel'])[0]
	RazdelsInfo.delete_instance(Razdels.name == data['dels_razdel'])
	await call.message.answer('Удалил', reply_markup=menuAdmin)

@dp.callback_query_handler(lambda c: c.data == 'installpromocode')
async def installpromocode1(call: types.CallbackQuery):
	await call.message.answer("Введите название:", reply_markup=menu)
	await AdminState.installpromocode2.set()

@dp.message_handler(state=AdminState.installpromocode2)
async def installpromocode2(message: types.Message, state: FSMContext):
	await message.answer('Введите сумму промокода:', reply_markup=menu)
	await state.update_data(username=message.text)
	await AdminState.installpromocode3.set()

@dp.message_handler(state=AdminState.installpromocode3)
async def installpromocode3(message: types.Message, state: FSMContext):
	amount = message.text
	await state.update_data(amount=amount)
	if amount.isdigit():
		await message.answer('Введите количество использований:', reply_markup=menu)
		await AdminState.installpromocode4.set()
	else:
		await message.answer('Введите цифры, пожалуйста.')
		await state.reset_state(with_data=False)

@dp.message_handler(state=AdminState.installpromocode4)
async def installpromocode4(message: types.Message, state: FSMContext):
	if message.text.isdigit():
		data = await state.get_data()
		if not Promocode.select():
			Promocode.create(name=(data['username']), amount=int(data['amount']), quantity=message.text)
			await message.answer('Промокод создан.', reply_markup=menuAdmin)
			await state.reset_state(with_data=False)
		else:
			Promocode.update(name=(data['username']), amount=int(data['amount']), quantity=message.text).execute()
			await message.answer('Промокод обновлён.', reply_markup=menuAdmin)
			await state.reset_state(with_data=False)
	else:
		await message.answer('Введите цифры.')
		await state.reset_state(with_data=False)

@dp.callback_query_handler(lambda c: c.data == 'del_promocode')
async def del_promocode(call: types.CallbackQuery):
	alls_promocodes = InlineKeyboardMarkup()
	for promo in Promocode.select():
		alls_promocodes.add(
			InlineKeyboardButton(text=f'{promo.name}', callback_data=f'delpromo_{promo.name}')
		)
	await call.message.answer('Доступные промокоды:', reply_markup=alls_promocodes)

@dp.callback_query_handler(lambda c: 'delpromo_' in c.data)
async def delpromo(call: types.CallbackQuery):
	await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
	name = call.data.split('delpromo_')[1]
	promoInfo = Promocode.select().where(Promocode.name == name)[0]
	promoInfo.delete_instance(Promocode.name == name)
	await call.message.answer('Удалил.', reply_markup=menuAdmin)

@dp.callback_query_handler(lambda c: c.data == 'cancel', state="*")
async def cancel_promo(call: types.CallbackQuery, state: FSMContext):
	await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
	await state.finish()
	await call.message.answer("Админ меню", reply_markup=menuAdmin)