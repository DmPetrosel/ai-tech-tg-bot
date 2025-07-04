from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard(page=1):
    if page == 1:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="О нас"), KeyboardButton(text="Услуги")],
                [KeyboardButton(text="Портфолио"), KeyboardButton(text="ИИ в медицине")],
                [KeyboardButton(text="Наш блог ➡️")]
            ],
            resize_keyboard=True
        )
    else:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="FAQ"), KeyboardButton(text="Контакты")],
                [KeyboardButton(text="⬅️ Главное меню")]
            ],
            resize_keyboard=True
        )

confirm_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Пройти регистрацию заново')],
        [KeyboardButton(text='Данные корректны')]
    ],
    resize_keyboard=True
)