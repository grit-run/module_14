from dotenv import load_dotenv
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()
BOT_TOKEN = os.getenv("TTN")

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)


class UserStates(StatesGroup):
    age = State()
    growth = State()
    weight = State()


keyb1 = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton("Рассчитать")
button2 = KeyboardButton("Информация")
button3 = KeyboardButton("Минералы и витамины")
keyb1.row(button1, button2, button3)

keyb2_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Рассчитать норму калорий", callback_data="calories"),
            InlineKeyboardButton(text="Формулы расчёта'", callback_data="formulas"),
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
    with open('files/images/AP1.jpg', 'rb') as img:
        await message.answer_photo(img, 'Название: 1 | Описание: описание 1 | Цена: 100p'.format(message))
    with open('files/images/AP2.png', 'rb') as img:
        await message.answer_photo(img, 'Название: 2 | Описание: описание 2 | Цена: 150p'.format(message))
    with open('files/images/AP3.png', 'rb') as img:
        await message.answer_photo(img, 'Название: 3 | Описание: описание 3 | Цена: 300p'.format(message))
    with open('files/images/AP4.jpg', 'rb') as img:
        await message.answer_photo(img, 'Название: 4 | Описание: описание 4 | Цена: 410p'.format(message))
    await message.answer('Выберите продукт для покупки:', reply_markup=buy_keys_inline)


@dp.message_handler(text="Рассчитать")
async def main_menu(message):
    await message.answer("Выберите опцию: ", reply_markup=keyb2_inline)


@dp.callback_query_handler(text="formulas")
async def formulas(call):
    await call.message.answer(formula_explanation, reply_markup=keyb1)
    await call.answer()


# @dp.callback_query_handler(text="exit")
# async def exit_to_main(call):
#     await call.message.answer("Вы вернулись в главное меню", reply_markup=keyb1)
#     await call.answer() @ dp.callback_query_handler(text="exit")


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
