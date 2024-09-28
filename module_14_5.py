from dotenv import load_dotenv
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from crud_functions import *

load_dotenv()
BOT_TOKEN = os.getenv("TTN")

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)

initiate_db()
check_add_product()


class UserStates(StatesGroup):
    age = State()
    growth = State()
    weight = State()


keyb1 = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton("Рассчитать")
button2 = KeyboardButton("Информация")
button3 = KeyboardButton("Минералы и витамины")
button4 = KeyboardButton("Регистрация")
keyb1.row(button1, button2, button3)
keyb1.add(button4)

keyb2_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Рассчитать норму калорий", callback_data="calories"),
            InlineKeyboardButton(text="Формулы расчёта", callback_data="formulas")
        ],
        [
            InlineKeyboardButton(text="Выход", callback_data="exit")
        ]
    ]
)

catalog_kb_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Минералы", callback_data="minerals"),
            InlineKeyboardButton(text="Витамины", callback_data="vitamins"),
            InlineKeyboardMarkup(text="Разное", callback_data="other")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back")
        ]
    ]
)

buy_keys_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="продукт 1", callback_data="buy"),
            InlineKeyboardButton(text="продукт 2", callback_data="buy"),
            InlineKeyboardButton(text="продукт 3", callback_data="buy"),
            InlineKeyboardButton(text="продукт 4", callback_data="buy")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back")
        ]
    ]
)

formula_explanation = ("Доработанный вариант формулы Миффлина-Сан Жеора учитывает степень физической активности "
                       "человека: для мужчин: (10 x вес (кг) + 6.25 x рост (см) – 5 x возраст (г) + 5) x A, "
                       "где A – это уровень активности человека, его различают обычно по пяти степеням физических "
                       "нагрузок в сутки")


@dp.message_handler(commands=['start'])
async def start(message):
    content = "Привет {message.from_user.username} !".format(message=message)
    await message.answer(content, reply_markup=keyb1)


@dp.message_handler(text="Информация")
async def information(message):
    content = "Бот, позволяющий рассчитать суточное потребление калорий"
    with open("files/images/AP5ALL.jpg", "rb") as img:
        await message.answer_photo(img, caption=content, reply_markup=keyb1)


@dp.message_handler(text='Минералы и витамины')
async def get_buying_list(message):
    for single_product in get_all_products():
        idp, title, description, price = single_product
        image_dir = "files/images/AP{}.jpg".format(idp)
        with open(image_dir, 'rb') as img:
            await message.answer_photo(img, 'Название: {} | Описание: {} | Цена: {}p'.format(title, description, price))
    await message.answer('Выберите продукт для покупки:', reply_markup=buy_keys_inline)


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()


@dp.message_handler(text="Регистрация")
async def sign_up(message):
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    username = message.text
    if is_included(username):
        await message.answer_with_reply_markup("Пользователь существует, введите другое имя")
    else:
        await state.update_data(username=username)
        await message.answer("Введите свой email:")
        await RegistrationState.email.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    email = message.text
    await state.update_data(email=email)
    await message.answer("Введите свой возраст:")
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    age = message.text
    age = int(age)
    user_data = await state.get_data()
    username = user_data['username']
    email = user_data['email']
    add_user(username, email, age)
    await message.answer("Регистрация завершена! Добро пожаловать, {}.".format(username), reply_markup=keyb1)
    await state.finish()



@dp.message_handler(text="Рассчитать")
async def main_menu(message):
    await message.answer("Выберите опцию: ", reply_markup=keyb2_inline)


@dp.callback_query_handler(text="formulas")
async def formulas(call):
    await call.message.answer(formula_explanation, reply_markup=keyb1)
    await call.answer()


@dp.callback_query_handler(text=["back", "exit"])
async def exit_to_main(call):
    await call.message.answer("Вы вернулись в главное меню", reply_markup=keyb1)
    await call.answer()


@dp.callback_query_handler(text='buy')
async def send_confirm_message(call):
    await call.message.answer('Продукт успешно куплен!')
    await call.answer()


@dp.callback_query_handler(text="calories")
async def age_set(call):
    age_question = "Введите свой возраст: "
    await call.message.answer(age_question)
    await UserStates.age.set()


@dp.message_handler(state=UserStates.age)
async def growth_set(message, state):
    await state.update_data(age=int(message.text))
    growth_question = "Введите свой рост в сантиметрах: "
    await message.answer(growth_question)
    await UserStates.growth.set()


@dp.message_handler(state=UserStates.growth)
async def weight_set(message, state):
    await state.update_data(growth=int(message.text))
    weight_question = "Введите свой вес: "
    await message.answer(weight_question)
    await UserStates.weight.set()


@dp.message_handler(state=UserStates.weight)
async def result(message, state):
    await state.update_data(weight=int(message.text))
    data = await state.get_data()
    calories_spend = (10 * data['age'] + 6.25 * data['growth'] - 5 * data['weight'] + 5) * 1.375
    await message.answer(
        "Ваша суточная норма каллорий при слвбой физической активности: {} каллорий".format(int(calories_spend)))
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
