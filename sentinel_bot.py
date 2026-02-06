import logging
import os
import asyncio
import psutil
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

# --- IMPORT MODULES ---
import tools
import brain

# --- CONFIG ---
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
CHECK_INTERVAL = 3600  # 1 Hour

# --- LOGGING ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# =========================================
#  CORE FUNCTIONS
# =========================================

async def system_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Feature: System Stats """
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('.').percent
    
    msg = (
        f"🖥️ **SENTINEL GALATEA v1.0**\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🧠 **Brain:** Online (Qwen)\n"
        f"⚙️ **CPU:** {cpu}%\n"
        f"💾 **RAM:** {ram}%\n"
        f"💿 **Disk:** {disk}%\n"
        f"👀 **Vision:** Waiting for input."
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode='Markdown')

async def summarize_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Usage: `/summary [URL]`")
        return

    url = context.args[0]
    chat_id = update.effective_chat.id

    status_msg = await update.message.reply_text("🧠 **Reading Video Metadata...**")

    # 1. Get the Raw Data (Tool)
    video_data = tools.get_video_metadata(url)

    if not video_data:
        await context.bot.edit_message_text(chat_id=chat_id, message_id=status_msg.message_id, text="❌ Failed to read" )
        return

    await context.bot.edit_message_text(chat_id=chat_id, message_id=status_msg.message_id, text="🤔 **Analyzing Conten")
    # 2. Ask the Brain (Qwen)
    # We craft a specific prompt for the AI
    prompt = "Please summarize this video based on the metadata provided. Tell me if it's worth watching."
    summary = brain.query_llm(prompt, context_data=video_data)

    # 3. Send Result
    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=status_msg.message_id,
        text=f"📝 **Video Briefing**\n━━━━━━━━━━━━━━\n{summary}",
        parse_mode='Markdown'
    )




async def track_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Feature: Manual Tracking Command """
    if not context.args:
        await update.message.reply_text("⚠️ Usage: `/track [URL]`")
        return

    url = context.args[0]
    chat_id = update.effective_chat.id
    
    status_msg = await update.message.reply_text("🕵️ **Analyzing Product...**")
    
    # Scrape
    title, price = tools.check_price(url)
    
    if price and price != "Not Found":
        # Save to DB
        added = tools.add_to_tracker(chat_id, url, title, price)
        if added:
            await context.bot.edit_message_text(
                chat_id=chat_id, 
                message_id=status_msg.message_id, 
                text=f"✅ **Tracking Started**\n📦 {title}\n💰 {price}\n\n*I will watch this for you.*"
            )
        else:
            await context.bot.edit_message_text(chat_id=chat_id, message_id=status_msg.message_id, text="⚠️ I am already tracking this item.")
    else:
        await context.bot.edit_message_text(chat_id=chat_id, message_id=status_msg.message_id, text="❌ Could not read price. Is the link valid?")



async def trend_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    status_msg = await update.message.reply_text("🌍 **Scanning the Atmosphere...**")

    # 1. Get the Raw Data
    # Run in thread because network requests block the bot
    raw_data = await asyncio.to_thread(tools.get_trending_report)
    
    if "Error" in raw_data:
        await context.bot.edit_message_text(chat_id=chat_id, message_id=status_msg.message_id, text=f"❌ {raw_data}")
        return

    # 2. Update Status
    await context.bot.edit_message_text(chat_id=chat_id, message_id=status_msg.message_id, text="🧠 **Analyzing Patterns...**")

    # 3. Ask the Brain
    prompt = (
        "Here is a list of the Top 10 Trending Videos on YouTube right now.\n"
        "Analyze the titles and tell me:\n"
        "1. What is the main topic everyone is watching?\n"
        "2. Is there any breaking news?\n"
        "3. Give me a 1-sentence 'Vibe Check' of the internet today.\n\n"
        f"DATA:\n{raw_data}"
    )
    
    analysis = brain.query_llm(prompt)

    # 4. Send Report
    await context.bot.edit_message_text(
        chat_id=chat_id, 
        message_id=status_msg.message_id, 
        text=f"📊 **Zeitgeist Report**\n━━━━━━━━━━━━━━\n{analysis}",
        parse_mode='Markdown'
    )

# Don't forget to add the handler!
# application.add_handler(CommandHandler('trends', trend_command))
# =========================================
#  THE SMART ROUTER (BRAIN + HANDS)
# =========================================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.effective_chat.id

    # 1. LINK DETECTION (The Tools)
    if "http" in text:
        # A. SHOPPING LINK -> Price Check
        if any(x in text.lower() for x in ["amazon", "flipkart", "amzn", "fkrt"]):
            await update.message.reply_text("🛍️ **Shopping Link Detected.**")
            title, price = tools.check_price(text)
            if price != "Not Found":
                msg = f"📦 **{title}**\n💰 **{price}**\n\nType `/track {text}` to save this."
                await update.message.reply_text(msg, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Price hidden or out of stock.")
        
        # B. VIDEO LINK -> Download
        elif any(x in text.lower() for x in ["youtube", "youtu.be", "instagram", "reel"]):
            await tools.download_video_logic(text, chat_id, context.bot)
        
        # C. UNKNOWN LINK
        else:
            await update.message.reply_text("⚠️ Unknown link type. Sentinel stands down.")

    # 2. CHAT DETECTION (The Brain)
    else:
        # Send typing action so user knows we are thinking
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        
        # Get reply from Qwen
        reply = brain.query_llm(text)
        await update.message.reply_text(reply)

# =========================================
#  BACKGROUND LOOP (PRICE MONITOR)
# =========================================
async def price_monitor_loop(app):
    """ Checks all tracked items every hour """
    while True:
        print(">> 🔄 Running Hourly Scan...")
        db = tools.load_data()
        
        for chat_id, items in db.items():
            for item in items:
                try:
                    # Re-check
                    _, new_price = tools.check_price(item['url'])
                    
                    # Compare (Simple string comparison for now)
                    if new_price and new_price != "Not Found" and new_price != item['last_price']:
                        alert = (
                            f"🚨 **PRICE DROP ALERT**\n"
                            f"📦 {item['title']}\n"
                            f"📉 Old: {item['last_price']} -> New: {new_price}\n"
                            f"🔗 [Buy Now]({item['url']})"
                        )
                        # Update DB
                        item['last_price'] = new_price
                        tools.save_data(db)
                        # Send Alert
                        await app.bot.send_message(chat_id=chat_id, text=alert, parse_mode='Markdown')
                        
                except Exception as e:
                    print(f"Error checking {item.get('title')}: {e}")
                
                await asyncio.sleep(5) # Be polite to servers

        await asyncio.sleep(CHECK_INTERVAL)

# =========================================
#  MAIN ENTRY POINT
# =========================================
if __name__ == '__main__':
    if not TOKEN:
        print("❌ ERROR: No Token found. Check .env")
        exit()

    application = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler('start', system_status))
    application.add_handler(CommandHandler('sys', system_status))
    application.add_handler(CommandHandler('track', track_command))
    application.add_handler(CommandHandler('summary', summarize_command))
    application.add_handler(CommandHandler('trends', trend_command))

    # The Router (Handles everything else)
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print(">> SENTINEL GALATEA V1.0: ONLINE.")
    
    # Start Background Loop
    loop = asyncio.get_event_loop()
    loop.create_task(price_monitor_loop(application))

    application.run_polling()
