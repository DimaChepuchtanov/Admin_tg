from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import requests


TOKEN = "7970568558:AAEEquAIXuyf3Ac2piZibqwJ9GvkxY56XPA"
bot = AsyncTeleBot(token=TOKEN, parse_mode='HTML')


@bot.message_handler(['post'])
async def get_posts(message):
    posts = requests.get('http://127.0.0.1:5000/posts/?desc=created_at')
    posts = eval(posts.content)

    button = InlineKeyboardMarkup(row_width=3)
    for i in posts:
        button.add(InlineKeyboardButton(i["title"], callback_data=f"id:{i['id']}"))

    await bot.send_message(chat_id=message.chat.id,
                           text=f"Существующих постов: {len(posts)}",
                           reply_markup=button)


@bot.callback_query_handler(func=lambda call: call.data == 'back')
async def back(call):
    posts = requests.get('http://127.0.0.1:5000/posts/?desc=created_at')
    posts = eval(posts.content)

    button = InlineKeyboardMarkup(row_width=3)
    for i in posts:
        button.add(InlineKeyboardButton(i["title"], callback_data=f"id:{i['id']}"))

    await bot.edit_message_text(message_id=call.message.id,
                                chat_id=call.message.chat.id,
                                text=f"Существующих постов: {len(posts)}",
                                reply_markup=button)


@bot.callback_query_handler(func=lambda call: "id" in call.data)
async def get_post(call):
    id = int(call.data.removeprefix('id:'))
    post = requests.get(f'http://127.0.0.1:5000/posts/{id}')
    post = eval(post.content)

    text = f"<b>{post['title']}</b>\n" + \
           f"Автор: <u>{post['author']}</u>\n" + \
           f"{post['text']}\n" + \
           f"<i>Опубликовано: <u>{post['created_at']}</u></i>"

    button = InlineKeyboardMarkup(row_width=3)
    button.add(InlineKeyboardButton("Назад", callback_data="back"))

    await bot.edit_message_text(message_id=call.message.id,
                                chat_id=call.message.chat.id,
                                text=text,
                                reply_markup=button)


if __name__ == "__main__":
    asyncio.run(bot.infinity_polling())
