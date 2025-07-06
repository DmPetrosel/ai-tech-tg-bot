from aiogram import F, Router
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
import app.database.requests as rq
from app.keyboards import get_main_keyboard, confirm_keyboard
from aiogram.types import CallbackQuery

router = Router()


class RegistrationStates(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_gender = State()
    waiting_for_age = State()
    waiting_for_ai_interest = State()
    waiting_for_phone = State()


async def show_main_menu(message: Message, page=1):
    await message.answer(
        "Главное меню:" if page == 1 else "Дополнительное меню",
        reply_markup=get_main_keyboard(page),
    )


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = await rq.get_user(message.from_user.id)
    if not user or not user.is_registered:
        await message.answer(
            "Привет! Я бот команды AI Tech. Давайте зарегистрируемся!",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Начать регистрацию")]],
                resize_keyboard=True,
            ),
        )
    else:
        await show_main_menu(message, page=1)


@router.message(F.text == "Начать регистрацию")
async def start_registration(message: Message, state: FSMContext):
    await state.set_state(RegistrationStates.waiting_for_full_name)
    await message.answer(
        "Введите ваше ФИО (полное имя):", reply_markup=ReplyKeyboardRemove()
    )


@router.message(RegistrationStates.waiting_for_full_name)
async def process_full_name(message: Message, state: FSMContext):
    if len(message.text) < 5:
        await message.answer("Пожалуйста, введите полное ФИО (минимум 5 символов)")
        return

    await state.update_data(full_name=message.text)
    await state.set_state(RegistrationStates.waiting_for_gender)
    await message.answer(
        "Ваш пол:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Мужской"), KeyboardButton(text="Женский")]],
            resize_keyboard=True,
        ),
    )


@router.message(RegistrationStates.waiting_for_gender)
async def process_gender(message: Message, state: FSMContext):
    valid_genders = ["Мужской", "Женский"]
    if message.text not in valid_genders:
        await message.answer("Пожалуйста, используйте кнопки")
        return

    await state.update_data(gender=message.text)
    await state.set_state(RegistrationStates.waiting_for_age)
    await message.answer(
        "Ваш возраст:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="до 18"), KeyboardButton(text="18-25")],
                [KeyboardButton(text="25-30"), KeyboardButton(text="30-45")],
                [KeyboardButton(text="45+")],
            ],
            resize_keyboard=True,
        ),
    )


@router.message(RegistrationStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    valid_ages = ["до 18", "18-25", "25-30", "30-45", "45+"]
    if message.text not in valid_ages:
        await message.answer("Пожалуйста, используйте кнопки")
        return

    await state.update_data(age=message.text)
    await message.answer(
        "Пожалуйста, поделитесь контактом или введите вручную:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text="Отправить контакт",
                        callback_data="contact",
                        request_contact=True,
                    ),
                ]
            ]
        ),
    )
    await state.set_state(RegistrationStates.waiting_for_phone)


@router.message(RegistrationStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):

    if not message.contact and len(message.text) <= 3:
        await message.answer(
            "Пожалуйста, введите номер телефона в формате +79991234567"
        )
        await state.set_state(RegistrationStates.waiting_for_phone)
        return
    if message.contact:
        await state.update_data(phone_number=message.contact.phone_number)
    else:
        await state.update_data(phone_number=message.text)

    await message.answer(text="Спасибо за контакт!")

    await state.set_state(RegistrationStates.waiting_for_ai_interest)
    await message.answer(
        "Рассматриваете ли вы внедрение нейросетей?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Да"), KeyboardButton(text="Нет")],
                [KeyboardButton(text="Возможно")],
            ],
            resize_keyboard=True,
        ),
    )


# @router.callback_query(F.data == "contact")
# async def process_contact(call: CallbackQuery, state: FSMContext):
#     if call.message.contact:
#         await call.answer(text="Спасибо за контакт!", show_alert=True)
#         await state.update_data(phone_number=call.message.contact.phone_number)

#     await state.set_state(RegistrationStates.waiting_for_ai_interest)
#     await call.message.answer(
#         "Рассматриваете ли вы внедрение нейросетей?",
#         reply_markup=ReplyKeyboardMarkup(
#             keyboard=[
#                 [KeyboardButton(text="Да"), KeyboardButton(text="Нет")],
#                 [KeyboardButton(text="Возможно")],
#             ],
#             resize_keyboard=True,
#         ),
#     )


@router.message(RegistrationStates.waiting_for_ai_interest)
async def process_ai_interest(message: Message, state: FSMContext):
    await state.update_data(ai_interest=message.text)
    user_data = await state.get_data()

    await message.answer(
        "Проверьте данные:\n\n"
        f"ФИО: {user_data['full_name']}\n"
        f"Пол: {user_data['gender']}\n"
        f"Возраст: {user_data['age']}\n"
        f"Номер телефона: {user_data['phone_number']}\n"
        f"Интерес к AI: {user_data['ai_interest']}",
        reply_markup=confirm_keyboard,
    )
    await state.set_state(None)


@router.message(F.text == "Данные корректны")
async def confirm_data(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await rq.create_or_update_user(
        tg_id=message.from_user.id,
        full_name=user_data["full_name"],
        gender=user_data["gender"],
        age=user_data["age"],
        phone_number=user_data["phone_number"],
        ai_interest=user_data["ai_interest"],
    )
    await state.clear()
    await show_main_menu(message, page=1)


@router.message(F.text == "Пройти регистрацию заново")
async def restart_registration(message: Message, state: FSMContext):
    await state.clear()
    await start_registration(message, state)


@router.message(F.text == "Наш блог ➡️")
async def next_page(message: Message):
    await show_main_menu(message, page=2)


@router.message(F.text == "⬅️ Главное меню")
async def prev_page(message: Message):
    await show_main_menu(message, page=1)


@router.message(F.text == "О нас")
async def about_us(message: Message):
    await message.answer(
        "🌟 <b>AI Tech - ваш надежный партнер в мире искусственного интеллекта!</b> 🌟\n\n"
        "🚀 Мы - команда экспертов с более чем 5-летним опытом в разработке AI-решений.\n"
        "💡 Наша миссия - сделать передовые технологии доступными для бизнеса любого масштаба.\n\n"
        "🔹 <b>50+</b> успешных проектов\n"
        "🔹 <b>25+</b> профессионалов в команде\n"
        "🔹 <b>100%</b> ориентация на результат клиента\n\n"
        "Мы создаем не просто технологии, а инструменты для вашего бизнес-прорыва!",
        reply_markup=get_main_keyboard(page=1),
        parse_mode="HTML",
    )


@router.message(F.text == "Услуги")
async def services(message: Message):
    await message.answer(
        "💼 <b>Наши ключевые услуги:</b>\n\n"
        "🤖 <b>AI-решения под ключ:</b> Полный цикл разработки интеллектуальных систем\n"
        "📊 <b>Аналитика данных:</b> Глубокий анализ и визуализация бизнес-показателей\n"
        "🛠 <b>Инструменты для работы с AI:</b> Собственные платформы для ваших задач\n"
        "🔍 <b>Консалтинг:</b> Стратегии внедрения ИИ в ваши процессы\n"
        "⚙️ <b>Оптимизация бизнес-процессов:</b> Автоматизация рутинных операций\n\n"
        "Каждое решение адаптируется под специфику вашей компании!",
        reply_markup=get_main_keyboard(page=1),
        parse_mode="HTML",
    )


@router.message(F.text == "Портфолио")
async def portfolio(message: Message):
    await message.answer(
        text="📂 <b>Наши кейсы</b>\n\n"
        "Вы можете запросить примеры наших работ у менеджера через раздел <b>Контакты</b>.\n\n"
        "🔹 Система диагностики для медицинского центра\n"
        "🔹 Оптимизация логистики для ритейл-сети\n"
        "🔹Делаем цифровой аналог для магазина с различными интеграциями и вспомогательными системами\n"
        "🔹Цифровая упаковка для персонального бренда\n"
        "🔹Разработка и внедрение искусственного интеллекта для раннего выявления онкологических заболеваний\n",
        reply_markup=get_main_keyboard(page=1),
        parse_mode="HTML",
    )

    # "📂 <b>Наши кейсы</b>\n\n"
    # "К сожалению, ссылки на полное портфолио временно недоступны.\n"
    # "Вы можете запросить примеры наших работ у менеджера через раздел <b>Контакты</b>.\n\n"
    # "🔹 Система диагностики для медицинского центра\n"
    # "🔹 Оптимизация логистики для ритейл-сети\n"
    # "🔹 AI-ассистент для банковского сектора",


@router.message(F.text == "ИИ в медицине")
async def ai_in_medicine(message: Message):
    await message.answer(
        "🏥 <b>Искусственный интеллект в медицине</b>\n\n"
        "Мы разрабатываем решения для:\n"
        "🔸 Автоматической диагностики по медицинским изображениям\n"
        "🔸 Прогнозирования течения заболеваний\n"
        "🔸 Персонализированного подбора терапии\n\n"
        "Наши технологии помогают:\n"
        "✅ Уменьшить количество диагностических ошибок\n"
        "✅ Сократить время обработки анализов\n"
        "✅ Повысить эффективность лечения\n\n"
        "<i>Пример внедрения: точность диагностики пневмонии по рентген-снимкам - 94%</i>",
        reply_markup=get_main_keyboard(page=1),
        parse_mode="HTML",
    )


@router.message(F.text == "FAQ")
async def faq(message: Message):
    await message.answer(
        "❓ <b>Часто задаваемые вопросы:</b>",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Как начать сотрудничество?", callback_data="faq_start"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Сколько стоит разработка?", callback_data="faq_cost"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Какие технологии вы используете?",
                        callback_data="faq_tech",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Есть ли готовые решения?", callback_data="faq_ready"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Какой срок реализации?", callback_data="faq_time"
                    )
                ],
            ]
        ),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("faq_"))
async def faq_answer(callback: CallbackQuery):
    question = callback.data.split("_")[1]
    answers = {
        "start": "🛠 <b>Как начать сотрудничество?</b>\n\n1. Оставьте заявку любым удобным вам способом: Telegram, WhatsApp, сайт или просто нам позвоните\n2. Мы проведем бесплатный аудит\n3. Получите индивидуальное предложение\n\nВесь процесс занимает 1-2 рабочих дня.",
        "cost": "💵 <b>Стоимость разработки</b>\n\nЦена зависит от сложности проекта:\n• MVP: от 500 000 руб.\n• Полноценное решение: от 1 500 000 руб.\n• Корпоративные системы: индивидуальный расчет",
        "tech": "🧠 <b>Используемые технологии</b>\n\n• Python, TensorFlow, PyTorch\n• Computer Vision (OpenCV)\n• NLP (BERT, GPT)\n• Анализ данных (Pandas, NumPy)\n• Облачные платформы (AWS, Yandex Cloud)",
        "ready": "📦 <b>Готовые решения</b>\n\n• Система распознавания документов\n• Чат-бот с NLP\n• Аналитика retail-данных\n• Медицинский диагностический модуль",
        "time": "⏱ <b>Сроки реализации</b>\n\n• Прототип: 2-4 недели\n• MVP: 1-3 месяца\n• Полноценный продукт: от 6 месяцев\n\nТочные сроки определяются после анализа задач.",
    }
    await callback.message.answer(answers[question], parse_mode="HTML")
    await callback.answer()


@router.message(F.text == "Контакты")
async def contacts(message: Message):
    await message.answer(
        "📞 <b>Как с нами связаться:</b>\n\n"
        "📍 <b>Адрес:</b> Наш главный офис сейчас в Новосибирске\n"
        "🕒 <b>Часы работы:</b> Пн-Пт 9:00-18:00\n\n"
        "<b>Контакты:</b>\n"
        "• Телефон: +7(985)555-17-79\n"
        "• Телеграм: @ai_tech_llc\n"
        "• Email: aitech2025@mail.ru\n"
        "• Сайт: <a href='https://xn--80akkb9bt4c.xn--p1ai//'>эйайтех.рф</a>\n\n"
        "<i>Закажите бесплатную консультацию через наш сайт!</i>",
        reply_markup=get_main_keyboard(page=2),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
