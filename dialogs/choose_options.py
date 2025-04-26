from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Group
from aiogram_dialog.widgets.text import Const
from aiogram_dialog import DialogManager
from aiogram.types import CallbackQuery
from states import States


async def on_choose(callback: CallbackQuery, button: Button, manager: DialogManager):
    texts = {
        "only_color": "Ваш цветотип: Тёплая весна 🌸",
        "makeup": "Рекомендуемый макияж: нюдовый с золотистыми тенями 💄",
        "hair_color": "Рекомендуемые цвета волос: золотистый блонд, карамельный ☀️",
        "clothes": "Одежда: пастельные оттенки, нежные ткани 👗",
        "all": "Всё вместе: Цветотип - Весна, макияж - нюд, волосы - карамель, одежда - пастель 🌼",
    }
    manager.dialog_data["result_text"] = texts.get(button.widget_id, "Выберите опцию заново!")
    await manager.next()


choose_options_window = Window(
    Const("Вы добавили фото.\n"
          "Выберите, что Вы хотите узнать дополнительно:"),
    Group(
        Button(Const("Только цветотип"), id="only_color", on_click=on_choose),
        Button(Const("Макияж"), id="makeup", on_click=on_choose),
        Button(Const("Цвет волос"), id="hair_color", on_click=on_choose),
        Button(Const("Одежда"), id="clothes", on_click=on_choose),
        Button(Const("Все выше перечисленное"), id="all", on_click=on_choose),
    ),
    state=States.choose_option,
)
