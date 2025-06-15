# -*- coding: utf-8 -*-
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging
from bot.texts import TEXTS
from bot.config import PLANS, ADMIN_IDS
from bot.interaction_logger import interaction_logger

logger = logging.getLogger(__name__)

# Global state for user languages and age verification
user_languages = {}
age_verified = {}

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all callback queries"""
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id
    interaction_logger.log(user_id, "callback", {"data": data})
    
    try:
        if data.startswith("lang_"):
            await handle_language_selection(query, user_id, data)
        elif data == "confirm_age":
            await handle_age_confirmation(query, user_id)
        elif data == "decline_age":
            await handle_age_decline(query, user_id)
        elif data == "main_menu":
            await show_main_menu(query, user_id)
        elif data == "show_plans":
            await show_plans(query, user_id)
        elif data == "policies":
            await show_policies(query, user_id)
        elif data == "terms":
            await show_terms(query, user_id)
        elif data == "privacy":
            await show_privacy(query, user_id)
        elif data == "refund":
            await show_refund(query, user_id)
        elif data == "contact":
            await show_contact(query, user_id)
        elif data == "help":
            await show_help(query, user_id)
        elif data == "admin_stats":
            await show_admin_stats(query, user_id)
        elif data == "admin_broadcast":
            await show_admin_broadcast(query, user_id)
        elif data.startswith("plan_"):
            await handle_plan_selection(query, user_id, data)
        else:
            logger.warning(f"Unknown callback data: {data}")
            
    except Exception as e:
        logger.error(f"Error handling callback {data}: {e}")
        await query.edit_message_text("❌ An error occurred. Please try again.")

async def handle_language_selection(query, user_id, data):
    """Handle language selection"""
    lang = data.split("_")[1]
    user_languages[user_id] = lang
    
    logger.info(f"User {user_id} selected language: {lang}")
    await show_age_verification(query, user_id)

async def show_age_verification(query, user_id):
    """Show age verification screen"""
    lang = user_languages.get(user_id, "en")
    
    keyboard = [
        [InlineKeyboardButton(TEXTS[lang]["confirm_age"], callback_data="confirm_age")],
        [InlineKeyboardButton(TEXTS[lang]["decline_age"], callback_data="decline_age")]
    ]
    
    await query.edit_message_text(
        text=TEXTS[lang]["age_warning"],
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def handle_age_confirmation(query, user_id):
    """Handle age confirmation"""
    age_verified[user_id] = True
    logger.info(f"User {user_id} confirmed age verification")
    await show_main_menu(query, user_id)

async def handle_age_decline(query, user_id):
    """Handle age decline"""
    lang = user_languages.get(user_id, "en")
    await query.edit_message_text("❌ You must be 18+ to use this service.\n❌ Debes tener 18+ para usar este servicio.")

async def show_main_menu(query, user_id):
    """Show main menu"""
    if not age_verified.get(user_id, False):
        await show_age_verification(query, user_id)
        return
    
    lang = user_languages.get(user_id, "en")
    
    keyboard = [
        [InlineKeyboardButton(TEXTS[lang]["plans"], callback_data="show_plans")],
        [InlineKeyboardButton(TEXTS[lang]["policies_menu"], callback_data="policies")],
        [InlineKeyboardButton(TEXTS[lang]["contact"], callback_data="contact")]
    ]
    
    # Add admin button if user is admin
    if user_id in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("🔧 Admin Stats", callback_data="admin_stats")])
    
    text = f"{TEXTS[lang]['welcome']}\n\n{TEXTS[lang]['welcome_desc']}"
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def show_plans(query, user_id):
    """Show subscription plans"""
    lang = user_languages.get(user_id, "en")
    
    keyboard = []
    
    for plan_id, plan_info in PLANS.items():
        plan_text = f"{plan_info['name']} - {plan_info['price']}"
        keyboard.append([
            InlineKeyboardButton(plan_text, callback_data=f"plan_{plan_id}")
        ])
    
    keyboard.append([InlineKeyboardButton(TEXTS[lang]["back"], callback_data="main_menu")])
    
    text = f"{TEXTS[lang]['plans_title']}\n\n{TEXTS[lang]['plan_benefits']}"
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def handle_plan_selection(query, user_id, data):
    """Handle plan selection with new BOLD payment system"""
    lang = user_languages.get(user_id, "en")
    plan_id = data.replace("plan_", "")
    
    plan_info = PLANS.get(plan_id)
    if not plan_info:
        await query.edit_message_text("❌ Plan not found")
        return
    
    # Get description in user's language
    from bot.config import PLAN_DESCRIPTIONS
    description = PLAN_DESCRIPTIONS.get(lang, PLAN_DESCRIPTIONS["en"])
    
    # Generate BOLD payment link and store transaction
    from bot.payment_links import payment_generator
    payment_url, tx_id = payment_generator.generate_payment_link(
        user_id=user_id,
        plan_name=plan_info["name"],
    )
    interaction_logger.log(user_id, "payment_link", {"plan": plan_id, "tx": tx_id})
    
    text = f"""**{plan_info['name']}**

💰 **Price:** {plan_info['price']}
⏱️ **Duration:** {plan_info['duration_days']} days

**Benefits:**
{description}

🔐 **Secure Payment Link Generated**
👤 User ID: {user_id}

Click below to complete payment:"""
    
    keyboard = [
        [InlineKeyboardButton("💳 Pay Securely", url=payment_url)],
        [InlineKeyboardButton(TEXTS[lang]["back"], callback_data="show_plans")]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def show_policies(query, user_id):
    """Show policies menu"""
    lang = user_languages.get(user_id, "en")
    
    keyboard = [
        [InlineKeyboardButton(TEXTS[lang]["terms_label"], callback_data="terms")],
        [InlineKeyboardButton(TEXTS[lang]["privacy_label"], callback_data="privacy")],
        [InlineKeyboardButton(TEXTS[lang]["refund_label"], callback_data="refund")],
        [InlineKeyboardButton(TEXTS[lang]["back"], callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text=TEXTS[lang]["policies_menu"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_terms(query, user_id):
    """Show terms and conditions"""
    lang = user_languages.get(user_id, "en")
    
    keyboard = [
        [InlineKeyboardButton(TEXTS[lang]["back"], callback_data="policies")]
    ]
    
    await query.edit_message_text(
        text=TEXTS[lang]["terms_content"],
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def show_privacy(query, user_id):
    """Show privacy policy"""
    lang = user_languages.get(user_id, "en")
    
    keyboard = [
        [InlineKeyboardButton(TEXTS[lang]["back"], callback_data="policies")]
    ]
    
    await query.edit_message_text(
        text=TEXTS[lang]["privacy_content"],
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def show_refund(query, user_id):
    """Show refund policy"""
    lang = user_languages.get(user_id, "en")
    
    keyboard = [
        [InlineKeyboardButton(TEXTS[lang]["back"], callback_data="policies")]
    ]
    
    await query.edit_message_text(
        text=TEXTS[lang]["refund_content"],
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def show_contact(query, user_id):
    """Show contact information"""
    lang = user_languages.get(user_id, "en")
    
    keyboard = [
        [InlineKeyboardButton(TEXTS[lang]["back"], callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text=TEXTS[lang]["contact_info"],
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def show_help(query, user_id):
    """Show help information"""
    lang = user_languages.get(user_id, "en")
    
    help_text = """🎬 **PNP Television Bot Help**

**Available Commands:**
/start - Start the bot and select language
/help - Show this help message
/plans - View subscription plans

**How to Subscribe:**
1. Use /plans to see available options
2. Choose your preferred plan
3. Complete payment through the secure link
4. Get instant access to your content!

**Support:**
If you need help, contact our support team at @PNPTVSupport"""
    
    keyboard = [
        [InlineKeyboardButton(TEXTS[lang]["back"], callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text=help_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def show_admin_stats(query, user_id):
    """Show admin statistics"""
    if user_id not in ADMIN_IDS:
        await query.edit_message_text("⛔ Unauthorized access")
        return
    
    text = """📊 **Bot Statistics**

👥 Total users: 0
✅ Active subscriptions: 0
📅 New users today: 0
💰 Total revenue: $0.00

**Plan Distribution:**
• Trial Trip: 0
• Monthly Adventure: 0
• Frequent Flyer: 0
• Full Year Experience: 0

Last updated: Just now"""
    
    keyboard = [
        [InlineKeyboardButton("🔄 Refresh", callback_data="admin_stats")]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def show_admin_broadcast(query, user_id):
    """Show instructions for broadcast"""
    if user_id not in ADMIN_IDS:
        await query.edit_message_text("⛔ Unauthorized access")
        return

    text = (
        "Use /broadcast <GROUP> <message> as text or caption.\n"
        "Groups: NEVER_PURCHASED, ACTIVE_MEMBER, CHURNED, ALL."
    )
    keyboard = [
        [InlineKeyboardButton(TEXTS['en']['back'], callback_data="admin_stats")]
    ]

    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )