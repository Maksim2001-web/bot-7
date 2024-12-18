# pip install aiogram
# pip install aiogram
# pip uninstall aiogram
# pip install aiogram==2.9

from crud_functions import initiate_db, get_all_products, add_product, delete_products_table
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import aiohttp


BOT_TOKEN = "7521461197:AAH52vbD5jk4evH1LECmyGnaJEBZC_apLkY"

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)



# Inline клавиатура для выбора продукта
product_keyboard = InlineKeyboardMarkup(row_width=4)  # Устанавливаем ширину строки
product_keyboard.add(
    InlineKeyboardButton("OPTIMUM NUTRITION Opti-Men", callback_data="product_buying_1"),
    InlineKeyboardButton("Витамины UNIECO", callback_data="product_buying_2"),
    InlineKeyboardButton("Optimum Nutrition Opti-Women", callback_data="product_buying_3"),
    InlineKeyboardButton("NOW Eve Woman's multi", callback_data="product_buying_4")
)

async def get_buying_list(message: types.Message):
    # возвращает все записи из таблицы Products
    products = get_all_products()

    for product in products:
        product_info = f'Название: {product[1]} | Описание: {product[2]} | Цена: {product[3]}'
        await message.answer(product_info)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(product[4]) as response:
                    if response.status == 200:
                        photo = await response.read()
                        await message.answer_photo(photo)
                    else:
                        await message.answer(f"Не удалось загрузить изображение для {product[1]}. Статус код: {response.status}")
        except Exception as e:
            await message.answer(f"Произошла ошибка при загрузке изображения для {product[1]}: {e}")

    await message.answer("Выберите продукт для покупки:", reply_markup=product_keyboard)

@dp.callback_query_handler(lambda call: call.data.startswith('product_buying'))
async def send_confirm_message(call: types.CallbackQuery):
    products = get_all_products()
    product_number = int(call.data.split('_')[-1])
    product_name = products[product_number - 1][1]

    await call.message.answer(f"Вы успешно приобрели {product_name}!")
    await call.answer()

# --- Калькулятор калорий ---
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Привет! Я бот для покупок и расчета калорий. Выберите опцию:", reply_markup=main_keyboard)

# Главная клавиатура
main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add(KeyboardButton("Купить"), KeyboardButton("Рассчитать"), KeyboardButton("Информация"))  # Все кнопки в одной строке

@dp.message_handler(lambda message: message.text == "Купить")
async def handle_buy_button(message: types.Message):
    await get_buying_list(message)

@dp.message_handler(lambda message: message.text == "Рассчитать")
async def main_menu(message: types.Message):
    await message.answer("Выберите опцию:", reply_markup=inline_keyboard)

@dp.message_handler(lambda message: message.text == 'Информация')  # Обработчик для информации
async def send_info(message: types.Message):
    await message.answer("Я помогу вам рассчитать норму калорий на основе вашего возраста, роста и веса.")

# Inline клавиатура для расчета калорий
inline_keyboard = InlineKeyboardMarkup()
button_calories = InlineKeyboardButton("Рассчитать норму калорий", callback_data='calories')
button_formulas = InlineKeyboardButton("Формулы расчёта", callback_data='formulas')
inline_keyboard.add(button_calories, button_formulas)

@dp.callback_query_handler(lambda call: call.data == 'formulas')
async def get_formulas(call: types.CallbackQuery):
    await call.answer()  # Убираем "часики" загрузки
    formulas_text = (
        "Формула Миффлина-Сан Жеора:\n"
        "Для мужчин: BMR = 10 * вес(кг) + 6.25 * рост(см) - 5 * возраст(лет) + 5\n"
        "Для женщин: BMR = 10 * вес(кг) + 6.25 * рост(см) - 5 * возраст(лет) - 161"
    )
    await call.message.answer(formulas_text)

@dp.callback_query_handler(lambda call: call.data == 'calories')
async def set_age(call: types.CallbackQuery):
    await call.answer()  # Убираем "часики" загрузки
    await call.message.answer("Введите свой возраст:")
    await UserState.age.set()

@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Введите свой рост в сантиметрах:")
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=message.text)
    await message.answer("Введите свой вес в килограммах:")
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)

    data = await state.get_data()
    age = int(data['age'])
    growth = int(data['growth'])
    weight = int(data['weight'])

    calories = 10 * weight + 6.25 * growth - 5 * age + 5  # Формула для мужчин
    await message.answer(f"Ваша норма калорий: {calories:.2f} ккал.")
    await state.finish()

@dp.message_handler(lambda message: True)
async def all_messages(message: types.Message):
    await message.answer("Введите команду /start, чтобы начать общение.")

if __name__ == "__main__":
    # удаление таблицы Products, если она существует.
    delete_products_table()

    # создаем таблицу Products, если она ещё не существует
    initiate_db()

    # добавление записей в таблицу Products
    add_product("OPTIMUM NUTRITION Opti-Men 150 таб", "Opti-Men от Optimum Nutrition - Фундаментальными строительными блоками человеческого тела являются витамины, минералы и другие незаменимые питательные вещества.", 150, "https://avatars.mds.yandex.net/get-mpic/5219133/img_id2438820024609966979.png/180x240")
    add_product("Витамины UNIECO 60 капсул", "комплекс витаминов, мультивитамины (поливитамины) для мужчин и для женщин, содержит группы необходимые витамины и минералы.", 200, "https://avatars.mds.yandex.net/get-mpic/7728649/img_id8146482534627482726.jpeg/180x240")
    add_product("NOW Eve Woman's multi, мультивитамины 120 капсул", "мультивитамины, разработанные для поддержания красоты, гормонального баланса и обеспечения организма всеми необходимыми витаминами и минералами", 500, "https://avatars.mds.yandex.net/get-mpic/1374520/2a000001929abfab26ff7ec64d0b4ed94007/180x240")
    add_product("Optimum Nutrition Opti-Women, 60 капс.", "сбалансированный комплекс витаминов и минералов, сочетание которых идеально подобрано для удовлетворения нужд женского организма.", 200, "https://avatars.mds.yandex.net/get-mpic/7728649/img_id8146482534627482726.jpeg/180x240")


    products = get_all_products()
    for product in products:
        print(product)
    executor.start_polling(dp, skip_updates=True)
