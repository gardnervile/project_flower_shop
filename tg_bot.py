import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, CallbackQueryHandler
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flower_shop.settings')
django.setup()

from bot.models import Bouquet, Order, Occasion, Budget, Customer

API_TOKEN = "7897677286:AAHQVy2LWkYPCeiMrZFu-H2SHdqRm4qFsec"
COURIER_ID = "1008286752"
FLORIST_ID = "1008286752"


logging.basicConfig(level=logging.INFO)


CHOOSING_EVENT, ENTERING_CUSTOM_EVENT, CHOOSING_BUDGET, AWAITING_ACTION, ORDERING, ASK_NAME, ASK_ADDRESS, ASK_DATETIME, ASK_PHONE = range(9)

#Клавиатура выбора повода
def get_occasion_keyboard() -> ReplyKeyboardMarkup:
    # Загружаем доступные поводы из базы данных
    occasions = Occasion.objects.all()  # Предположим, что у вас есть модель Occasion
    occasion_list = [[occasion.name] for occasion in occasions]  # Форматируем для клавиатуры

    return ReplyKeyboardMarkup(occasion_list, one_time_keyboard=True, resize_keyboard=True)

# Клавиатура выбора бюджета
def get_budget_keyboard() -> ReplyKeyboardMarkup:
    budgets = Budget.objects.all()
    budget_list = [[budget.name] for budget in budgets]
    return ReplyKeyboardMarkup(budget_list, one_time_keyboard=True, resize_keyboard=True)

def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Привет! К какому событию готовимся? Выберите один из вариантов, либо укажите свой", reply_markup = get_occasion_keyboard())
    return CHOOSING_EVENT

# Выбор события
def choose_event(update: Update, context: CallbackContext) -> int:
    occasions = Occasion.objects.all()
    context.user_data['occasions'] = occasions

    if update.message.text == "Другой повод":
        update.message.reply_text("Напишите, пожалуйста, какой повод")
        return ENTERING_CUSTOM_EVENT
    else:
        context.user_data['event'] = update.message.text
        update.message.reply_text("На какую сумму рассчитываете?", reply_markup=get_budget_keyboard())
        return CHOOSING_BUDGET


# Ввод кастомного повода
def enter_custom_event(update: Update, context: CallbackContext) -> int:
    custom_event = update.message.text
    context.user_data['event'] = custom_event
    update.message.reply_text("На какую сумму рассчитываете?", reply_markup=get_budget_keyboard())
    return CHOOSING_BUDGET


# Выбор бюджета и показ букета (здесь по идее должна быть база данных)
def show_bouquet(update: Update, context: CallbackContext) -> int:
    context.user_data['budget'] = update.message.text
    event = context.user_data.get('event')
    budget = context.user_data.get('budget')

    # Получаем объект Occasion по имени
    occasion = Occasion.objects.filter(name=event).first()

    # Фильтруем букеты по выбранному событию
    bouquets = Bouquet.objects.filter(occasion=occasion)

    if budget != "Не важно":
        # Получаем объект бюджета по имени
        budget_obj = Budget.objects.filter(name=budget).first()
        if budget_obj:
            bouquets = bouquets.filter(price__gte=budget_obj.min_price, price__lte=budget_obj.max_price)

    if bouquets.exists():
        bouquet = bouquets.first()
        photo = bouquet.image if bouquet.image else " "
        description = bouquet.description
        price = f"Цена: {bouquet.price} ₽"

        update.message.bot.send_photo(chat_id=update.message.chat_id, photo=photo,
                                      caption=f"{description}\n{price}")

        keyboard = [
            [InlineKeyboardButton("Заказать букет", callback_data='order')],
            [InlineKeyboardButton("Заказать консультацию", callback_data='consult')],
            [InlineKeyboardButton("Посмотреть всю коллекцию", callback_data='catalog')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text(
            "*Хотите что-то еще более уникальное?*\nПодберите другой букет из нашей коллекции или закажите консультацию флориста.",
            parse_mode='Markdown', reply_markup=reply_markup)

    else:
        update.message.reply_text("К сожалению, нет доступных букетов для вашего выбора.")

    return AWAITING_ACTION


#выбор бюджета
def choose_budget(update: Update, context: CallbackContext) -> int:
    selected_budget_name = update.message.text
    selected_budget = Budget.objects.filter(name=selected_budget_name).first()


    if selected_budget is None:
        update.message.reply_text("Извините, выбранный бюджет не найден.")
        return CHOOSING_BUDGET

    context.user_data['budget'] = selected_budget

    # Сразу показываем букеты после выбора бюджета
    show_bouquet(update, context)

    return AWAITING_ACTION

def show_all_bouquets_by_event_and_budget(update: Update, context: CallbackContext) -> int:
    event = context.user_data.get('event')  # Получаем выбранный повод
    budget = context.user_data.get('budget')  # Получаем выбранный бюджет

    # Получаем объект Occasion по имени
    occasion = Occasion.objects.filter(name=event).first()

    # Фильтруем букеты по выбранному событию
    bouquets = Bouquet.objects.filter(occasion=occasion)

    if budget != "Не важно":
        # Получаем объект бюджета по имени
        budget_obj = Budget.objects.filter(name=budget).first()
        if budget_obj:
            bouquets = bouquets.filter(price__gte=budget_obj.min_price, price__lte=budget_obj.max_price)

    if bouquets.exists():
        for bouquet in bouquets:
            photo = bouquet.image if bouquet.image else None
            description = bouquet.description
            price = f"Цена: {bouquet.price} ₽"

            try:
                # Создаем клавиатуру для каждого букета
                keyboard = [
                    [InlineKeyboardButton("Заказать букет", callback_data=f'order_{bouquet.id}')],
                    [InlineKeyboardButton("Заказать консультацию", callback_data='consult')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                if photo:
                    update.message.bot.send_photo(chat_id=update.message.chat_id, photo=photo,
                                                  caption=f"{bouquet.name}\n{description}\n{price}",
                                                  reply_markup=reply_markup)
                else:
                    update.message.reply_text(f"Букет: {bouquet.name}\nОписание: {description}\nЦена: {price}\n(Изображение отсутствует)",
                                              reply_markup=reply_markup)
            except Exception as e:
                logging.error(f"Ошибка при отправке сообщения: {e}")
                update.message.reply_text("Произошла ошибка при отправке сообщения. Пожалуйста, попробуйте позже.")
    else:
        update.message.reply_text("К сожалению, нет доступных букетов для выбранного повода и бюджета.")

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
        return show_all_bouquets_by_event_and_budget(query, context)

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

    # Сохраняем клиента в базе данных
    customer = Customer.objects.create(
        name=context.user_data['name'],
        phone=context.user_data.get('phone', '')
    )

    # Получаем выбранный букет
    bouquet = Bouquet.objects.filter(occasion__name=context.user_data['event']).first()

    # Создаем заказ
    order = Order.objects.create(
        customer=customer,
        bouquet=bouquet,
        quantity=1,
        status='ожидание'
    )


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