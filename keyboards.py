# Стартовая клавиатура
start_keyboard = {
    "Type": "keyboard",
    "Buttons": [
        {
            "Columns": 6,
            "Rows": 1,
            "BgColor": "#ca9df4",
            "ActionType": "reply",
            "ActionBody": "start",
            "ReplyType": "message",
            "Text": "Давай начнем!"
        }
    ]
}

# Клавиатура "второго окна"
round_keyboard = {
    "Type": "keyboard",
    "Buttons": [
        {
            "Columns": 3,
            "Rows": 1,
            "BgColor": "#ca9df4",
            "ActionType": "reply",
            "ActionBody": "",
            "ReplyType": "message",
            "Text": ""
        },

        {
            "Columns": 3,
            "Rows": 1,
            "BgColor": "#ca9df4",
            "ActionType": "reply",
            "ActionBody": "",
            "ReplyType": "message",
            "Text": ""
        },

        {
            "Columns": 3,
            "Rows": 1,
            "BgColor": "#ca9df4",
            "ActionType": "reply",
            "ActionBody": "",
            "ReplyType": "message",
            "Text": ""
        },

        {
            "Columns": 3,
            "Rows": 1,
            "BgColor": "#ca9df4",
            "ActionType": "reply",
            "ActionBody": "",
            "ReplyType": "message",
            "Text": ""
        },

        {
            "Columns": 6,
            "Rows": 1,
            "BgColor": "#e8d6fc",
            "ActionType": "reply",
            "ActionBody": "show_example",
            "ReplyType": "",
            "Text": "привести пример"
        },
    ]
}

# Клавиатура "напоминания"
remind_keyboard = {
    "Type": "keyboard",
    "Buttons": [
        {
            "Columns": 6,
            "Rows": 1,
            "BgColor": "#ca9df4",
            "ActionType": "reply",
            "ActionBody": "start",
            "ReplyType": "message",
            "Text": "Повторить!"
        },

        {
            "Columns": 6,
            "Rows": 1,
            "BgColor": "#ca9df4",
            "ActionType": "reply",
            "ActionBody": "remind_later",
            "ReplyType": "message",
            "Text": "Напомнить позже"
        },
    ]
}