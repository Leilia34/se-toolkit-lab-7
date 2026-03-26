"""Inline keyboard buttons for quick actions."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Get main menu keyboard with common actions."""
    keyboard = [
        [
            InlineKeyboardButton(text="📚 Labs", callback_data="cmd_labs"),
            InlineKeyboardButton(text="🏥 Health", callback_data="cmd_health"),
        ],
        [
            InlineKeyboardButton(text="📊 Scores Lab 01", callback_data="cmd_scores_lab-01"),
            InlineKeyboardButton(text="📊 Scores Lab 04", callback_data="cmd_scores_lab-04"),
        ],
        [
            InlineKeyboardButton(text="👥 Top Learners", callback_data="cmd_top_lab-04"),
            InlineKeyboardButton(text="📈 Completion Rate", callback_data="cmd_completion_lab-04"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_scores_keyboard(lab_id: str) -> InlineKeyboardMarkup:
    """Get keyboard for lab-specific actions."""
    keyboard = [
        [
            InlineKeyboardButton(text="📊 Pass Rates", callback_data=f"pass_rates_{lab_id}"),
            InlineKeyboardButton(text="📈 Timeline", callback_data=f"timeline_{lab_id}"),
        ],
        [
            InlineKeyboardButton(text="👥 Groups", callback_data=f"groups_{lab_id}"),
            InlineKeyboardButton(text="🏆 Top Learners", callback_data=f"top_{lab_id}"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Get back button keyboard."""
    keyboard = [
        [InlineKeyboardButton(text="← Back to Menu", callback_data="cmd_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
