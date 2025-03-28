import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, CallbackQueryHandler


API_TOKEN = ""
COURIER_ID = ""
FLORIST_ID = ""


logging.basicConfig(level=logging.INFO)


CHOOSING_EVENT, ENTERING_CUSTOM_EVENT, CHOOSING_BUDGET, AWAITING_ACTION, ORDERING, ASK_NAME, ASK_ADDRESS, ASK_DATETIME, ASK_PHONE = range(9)

# Клавиатура выбора события
event_keyboard = ReplyKeyboardMarkup([
    ["День рождения", "Свадьба"],
    ["В школу", "Без повода"],
    ["Другой повод"]
], resize_keyboard=True)

# Клавиатура выбора бюджета
budget_keyboard = ReplyKeyboardMarkup([
    ["~500", "~1000"],
    ["~2000", "Больше"],
    ["Не важно"]
], resize_keyboard=True)


def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Привет! К какому событию готовимся? Выберите один из вариантов, либо укажите свой", reply_markup=event_keyboard)
    return CHOOSING_EVENT

# Выбор события
def choose_event(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    if text == "Другой повод":
        update.message.reply_text("Напишите, пожалуйста, какой повод")
        return ENTERING_CUSTOM_EVENT
    else:
        context.user_data['event'] = text
        update.message.reply_text("На какую сумму рассчитываете?", reply_markup=budget_keyboard)
        return CHOOSING_BUDGET

# Ввод кастомного повода
def enter_custom_event(update: Update, context: CallbackContext) -> int:
    context.user_data['event'] = update.message.text
    update.message.reply_text("Спасибо! На какую сумму рассчитываете?", reply_markup=budget_keyboard)
    return CHOOSING_BUDGET

# Выбор бюджета и показ букета (здесь по идее должна быть база данных)
def show_bouquet(update: Update, context: CallbackContext) -> int:
    context.user_data['budget'] = update.message.text

    photo_url = ""
    description = "Этот букет несет в себе всю нежность ваших чувств и не способен оставить равнодушным ни одно сердце!"
    composition = "Состав: розы, альстромерии, зелень"
    price = "Цена: 1500 ₽"

    update.message.bot.send_photo(chat_id=update.message.chat_id, photo=photo_url,
        caption=f"{description}\n{composition}\n{price}")

    keyboard = [
        [InlineKeyboardButton("Заказать букет", callback_data='order')],
        [InlineKeyboardButton("Заказать консультацию", callback_data='consult')],
        [InlineKeyboardButton("Посмотреть всю коллекцию", callback_data='catalog')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "*Хотите что-то еще более уникальное?*\nПодберите другой букет из нашей коллекции или закажите консультацию флориста.",
        parse_mode='Markdown', reply_markup=reply_markup)

    return AWAITING_ACTION

# Обработка нажатий на кнопки
def handle_action(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    if query.data == 'order':
        query.edit_message_text("Давайте оформим заказ. Как вас зовут?")
        return ASK_NAME
    elif query.data == 'consult':
        query.edit_message_text("Укажите номер телефона, и наш флорист перезвонит вам в течение 20 минут")
        return ASK_PHONE
    elif query.data == 'catalog':
        return show_bouquet(query, context)

# Оформление заказа
def ask_name(update: Update, context: CallbackContext) -> int:
    context.user_data['name'] = update.message.text
    update.message.reply_text("Укажите адрес доставки:")
    return ASK_ADDRESS

def ask_address(update: Update, context: CallbackContext) -> int:
    context.user_data['address'] = update.message.text
    update.message.reply_text("Когда доставить букет? Укажите дату и время:")
    return ASK_DATETIME

def ask_datetime(update: Update, context: CallbackContext) -> int:
    context.user_data['datetime'] = update.message.text

    order_info = f"Новый заказ:\n\nИмя: {context.user_data['name']}\nАдрес: {context.user_data['address']}\nДата/время: {context.user_data['datetime']}\nПовод: {context.user_data['event']}\nБюджет: {context.user_data['budget']}"

    context.bot.send_message(chat_id=COURIER_ID, text=order_info)
    update.message.reply_text("Спасибо! Ваш заказ принят и скоро будет доставлен.")
    return ConversationHandler.END

# Телефон для консультации
def receive_phone(update: Update, context: CallbackContext) -> int:
    phone = update.message.text
    context.bot.send_message(chat_id=FLORIST_ID, text=f"Новая консультация: перезвоните по номеру {phone}")
    update.message.reply_text("Флорист скоро свяжется с вами. А пока можете присмотреть что-нибудь из готовой коллекции.")
    return show_bouquet(update, context)


if __name__ == '__main__':
    updater = Updater(API_TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_EVENT: [MessageHandler(Filters.text & ~Filters.command, choose_event)],
            ENTERING_CUSTOM_EVENT: [MessageHandler(Filters.text & ~Filters.command, enter_custom_event)],
            CHOOSING_BUDGET: [MessageHandler(Filters.text & ~Filters.command, show_bouquet)],
            AWAITING_ACTION: [CallbackQueryHandler(handle_action)],
            ASK_NAME: [MessageHandler(Filters.text & ~Filters.command, ask_name)],
            ASK_ADDRESS: [MessageHandler(Filters.text & ~Filters.command, ask_address)],
            ASK_DATETIME: [MessageHandler(Filters.text & ~Filters.command, ask_datetime)],
            ASK_PHONE: [MessageHandler(Filters.text & ~Filters.command, receive_phone)],
        },
        fallbacks=[CommandHandler('start', start)]
    )

    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()