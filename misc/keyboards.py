from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

menuUser = ReplyKeyboardMarkup(resize_keyboard=True)
menuUser.add("👤 Профиль", "🎈 Купить")

menuAdmin = InlineKeyboardMarkup()
menuAdmin.add(
    InlineKeyboardButton(text='Бан/Разбан', callback_data='blocked'),
    InlineKeyboardButton(text='Рассылка', callback_data='mailing'),
    InlineKeyboardButton(text='Статистика', callback_data='stats')
).add(
    InlineKeyboardButton(text='Добавить баланс', callback_data='add_balance'),
    InlineKeyboardButton(text='Убрать баланс', callback_data='del_balance'),
    InlineKeyboardButton(text='add категорию', callback_data='add_ketegory')
).add(
    InlineKeyboardButton(text='del категорию', callback_data='del_ketegory'),
    InlineKeyboardButton(text='Добавить Товар', callback_data='add_tovar'),
    InlineKeyboardButton(text='Удалить товар', callback_data='del_tovar')
).add(
    InlineKeyboardButton(text='Добавить промокод', callback_data='installpromocode'),
    InlineKeyboardButton(text='Удалить промокод', callback_data='del_promocode')
)

back_ = InlineKeyboardMarkup()
back_.add(
    InlineKeyboardButton(text='Назад', callback_data='back_main')
)

back_promo = InlineKeyboardMarkup()
back_promo.add(
    InlineKeyboardButton(text='Отмена', callback_data='back_promocode')
)

menu = InlineKeyboardMarkup()
menu.add(
    InlineKeyboardButton(text='Отмена', callback_data='cancel')
)

profile_menu = InlineKeyboardMarkup()
profile_menu.add(
    InlineKeyboardButton(text='Пополнить баланс', callback_data='popolnenie')
).add(
    InlineKeyboardButton(text='Ввести промокод', callback_data='promocode')
)

kategoryes = InlineKeyboardMarkup()
kategoryes.add(
    InlineKeyboardButton(text='🔮Vpn', callback_data='kategoryes_menu')
)

payments = InlineKeyboardMarkup()
payments.add(
    InlineKeyboardButton(text='💎CrystalPay', callback_data='payment_crystal')
).add(
    InlineKeyboardButton(text='🪐Lolz', callback_data='payment_lolz')
).add(
    InlineKeyboardButton(text='Назад', callback_data='back_profile')
)

menu_delstovar = InlineKeyboardMarkup()
menu_delstovar.add(
    InlineKeyboardButton(text='Продолжить', callback_data='dels_next')
).add(
    InlineKeyboardButton(text='Назад', callback_data='cancel')
)

menu_delsrazdel = InlineKeyboardMarkup()
menu_delsrazdel.add(
    InlineKeyboardButton(text='Продолжить', callback_data='razdel_delete')
).add(
    InlineKeyboardButton(text='Назад', callback_data='cancel')
)
