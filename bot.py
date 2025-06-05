import os
import logging
import sys
import asyncio
from datetime import datetime, timedelta
import json
import shutil
from telethon import TelegramClient, events
from dotenv import load_dotenv

# Logging configuration
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

current_date = datetime.now().strftime("%Y-%m-%d")
log_filename = os.path.join(log_directory, f"telegram_downloader_{current_date}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler(sys.stdout)
    ]
)

# Filter out noisy Telethon logs
logging.getLogger('telethon.client.updates').setLevel(logging.WARNING)
logging.getLogger('telethon.network').setLevel(logging.WARNING)
logging.getLogger('telethon.client.auth').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Load variables from config.env
load_dotenv("config.env")

# Get credentials from config.env file
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH", "/media/medialibrary/downloaded")
TARGET_CHAT_ID_STR = os.getenv("TARGET_CHAT_ID")
ALLOWED_USER = os.getenv("ALLOWED_USER")  # Username of authorized user
STATS_FILE = os.getenv("STATS_FILE", "bot_stats.json")
DISK_WARNING_THRESHOLD = int(os.getenv("DISK_WARNING_THRESHOLD", "90"))  # in percent

# Verify credentials were loaded correctly
if not API_ID or not API_HASH:
    logger.error("❌ API_ID or API_HASH not found in config.env file")
    sys.exit(1)

if not TARGET_CHAT_ID_STR:
    logger.error("❌ TARGET_CHAT_ID not found in config.env file")
    sys.exit(1)

if not ALLOWED_USER:
    logger.error("❌ ALLOWED_USER not found in config.env file")
    sys.exit(1)

# Clean and convert TARGET_CHAT_ID
try:
    # Handle any comments in the .env file by taking only the part before "#"
    # and convert to integer
    TARGET_CHAT_ID = int(TARGET_CHAT_ID_STR.split('#')[0].strip())
    logger.info(f"Target chat ID: {TARGET_CHAT_ID}")
except ValueError:
    logger.error(f"❌ Invalid TARGET_CHAT_ID format: '{TARGET_CHAT_ID_STR}'. Must be an integer.")
    sys.exit(1)

# Verify download directory exists
logger.info(f"🔍 Checking download folder: '{DOWNLOAD_PATH}'")
if not os.path.exists(DOWNLOAD_PATH):
    logger.error(f"❌ Download folder '{DOWNLOAD_PATH}' does not exist. Terminating program.")
    sys.exit(1)
else:
    logger.info(f"✅ Download folder verified: {DOWNLOAD_PATH}")

# Statistics management
def load_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"⚠️ Could not load stats file: {str(e)}")
    return {"downloads": 0, "success": 0, "failed": 0, "total_bytes": 0}


def save_stats():
    try:
        with open(STATS_FILE, "w") as f:
            json.dump(stats, f)
    except Exception as e:
        logger.warning(f"⚠️ Could not save stats file: {str(e)}")


stats = load_stats()
paused = False
bot_start_time = datetime.now()


async def is_authorized(event):
    sender = await event.get_sender()
    sender_username = getattr(sender, 'username', None)
    sender_id = str(sender.id) if hasattr(sender, 'id') else None
    authorized = (sender_username and sender_username == ALLOWED_USER) or (
        sender_id and sender_id == ALLOWED_USER)
    if not authorized:
        logger.info(
            f"🚫 Unauthorized access attempt from @{sender_username or 'unknown'} (ID: {sender_id or 'unknown'})")
    return authorized

# Create Telegram client with persistent session
logger.info("🔄 Initializing Telegram client...")
client = TelegramClient("session_name", int(API_ID), API_HASH)

async def setup_client():
    # Check if we can access the target chat
    try:
        # Try to get entity information
        entity = await client.get_entity(TARGET_CHAT_ID)
        logger.info(f"✅ Successfully connected to chat: {getattr(entity, 'title', str(TARGET_CHAT_ID))}")
    except ValueError as e:
        logger.error(f"❌ Could not find chat with ID {TARGET_CHAT_ID}. Error: {str(e)}")
        logger.info("⚠️ Make sure the account is a member of this chat/channel/group")
        return False
    except Exception as e:
        logger.error(f"❌ Error accessing chat: {str(e)}")
        return False
    
    return True


@client.on(events.NewMessage(pattern='/start'))
async def cmd_start(event):
    if not (hasattr(event.chat, 'id') and event.chat.id == TARGET_CHAT_ID):
        return
    if not await is_authorized(event):
        return
    logger.info("/start command invoked")
    msg = (
        "👋 *Telegram Media Downloader*\n"
        "Use /help to see available commands." )
    await event.reply(msg)


@client.on(events.NewMessage(pattern='/help'))
async def cmd_help(event):
    if not (hasattr(event.chat, 'id') and event.chat.id == TARGET_CHAT_ID):
        return
    if not await is_authorized(event):
        return
    logger.info("/help command invoked")
    help_text = (
        "*/start* - Welcome message\n"
        "*/help* - Command reference\n"
        "*/status* - Current bot status\n"
        "*/stats* - Download statistics\n"
        "*/pause* - Pause downloads\n"
        "*/resume* - Resume downloads\n"
        "*/disk* - Disk usage info\n"
        "*/logs* - Show recent log entries")
    await event.reply(help_text)


@client.on(events.NewMessage(pattern='/pause'))
async def cmd_pause(event):
    global paused
    if not (hasattr(event.chat, 'id') and event.chat.id == TARGET_CHAT_ID):
        return
    if not await is_authorized(event):
        return
    logger.info("/pause command invoked")
    paused = True
    await event.reply("⏸️ Downloads paused")


@client.on(events.NewMessage(pattern='/resume'))
async def cmd_resume(event):
    global paused
    if not (hasattr(event.chat, 'id') and event.chat.id == TARGET_CHAT_ID):
        return
    if not await is_authorized(event):
        return
    logger.info("/resume command invoked")
    paused = False
    await event.reply("▶️ Downloads resumed")


@client.on(events.NewMessage(pattern='/status'))
async def cmd_status(event):
    if not (hasattr(event.chat, 'id') and event.chat.id == TARGET_CHAT_ID):
        return
    if not await is_authorized(event):
        return
    logger.info("/status command invoked")
    uptime = datetime.now() - bot_start_time
    status = "Paused" if paused else "Running"
    msg = (
        "📊 *Bot Status*\n"
        f"🟢 Status: {status}\n"
        f"⏱️ Uptime: {str(uptime).split('.')[0]}\n"
        f"✅ Downloads: {stats.get('success',0)}\n"
        f"📁 Total size: {stats.get('total_bytes',0)/1024/1024:.1f} MB")
    await event.reply(msg)


@client.on(events.NewMessage(pattern='/stats'))
async def cmd_stats(event):
    if not (hasattr(event.chat, 'id') and event.chat.id == TARGET_CHAT_ID):
        return
    if not await is_authorized(event):
        return
    logger.info("/stats command invoked")
    total = stats.get('downloads',0)
    success = stats.get('success',0)
    failed = stats.get('failed',0)
    success_rate = (success/total*100) if total else 0
    msg = (
        "📈 *Download Statistics*\n"
        f"Total: {total}\n"
        f"Success: {success}\n"
        f"Failed: {failed}\n"
        f"Success rate: {success_rate:.1f}%\n"
        f"Total size: {stats.get('total_bytes',0)/1024/1024:.1f} MB")
    await event.reply(msg)


@client.on(events.NewMessage(pattern='/disk'))
async def cmd_disk(event):
    if not (hasattr(event.chat, 'id') and event.chat.id == TARGET_CHAT_ID):
        return
    if not await is_authorized(event):
        return
    logger.info("/disk command invoked")
    total, used, free = shutil.disk_usage(DOWNLOAD_PATH)
    percent = used/total*100
    status = "⚠️ Low space" if percent >= DISK_WARNING_THRESHOLD else "🟢 Status: Good"
    msg = (
        "💾 *Disk Usage*\n"
        f"📂 Path: {DOWNLOAD_PATH}\n"
        f"💽 Total: {total/1024/1024/1024:.0f} GB\n"
        f"📊 Used: {used/1024/1024/1024:.0f} GB ({percent:.1f}%)\n"
        f"🆓 Free: {free/1024/1024/1024:.0f} GB\n"
        f"{status}")
    await event.reply(msg)


@client.on(events.NewMessage(pattern='/logs'))
async def cmd_logs(event):
    if not (hasattr(event.chat, 'id') and event.chat.id == TARGET_CHAT_ID):
        return
    if not await is_authorized(event):
        return
    logger.info("/logs command invoked")
    try:
        with open(log_filename, 'r') as f:
            lines = f.readlines()[-10:]
        await event.reply("\n".join([line.strip() for line in lines]) or "No logs")
    except Exception as e:
        await event.reply(f"❌ Could not read log file: {str(e)}")

@client.on(events.NewMessage())
async def download_video(event):
    # First check if this is the right chat
    if not hasattr(event.chat, 'id') or event.chat.id != TARGET_CHAT_ID:
        return

    if not await is_authorized(event):
        return

    if paused:
        logger.info("⏸️ Downloads are currently paused")
        return

    sender = await event.get_sender()
    sender_username = getattr(sender, 'username', None)

    logger.info(f"📩 New message received from authorized user: @{sender_username or 'unknown'}")
    
    if event.media:
        stats['downloads'] = stats.get('downloads', 0) + 1
        try:
            logger.info("🔄 Starting media download...")
            
            # Send initial progress message
            progress_message = await event.reply("🔄 Starting download... 0%")
            
            # Progress callback function
            async def progress_callback(current, total):
                try:
                    percentage = (current / total) * 100
                    progress_bar = "█" * int(percentage // 5) + "░" * (20 - int(percentage // 5))
                    progress_text = f"📥 Downloading: {percentage:.1f}%\n[{progress_bar}]\n{current / (1024*1024):.1f} MB / {total / (1024*1024):.1f} MB"
                    
                    # Update message every 5% to avoid rate limiting
                    if int(percentage) % 5 == 0 and int(percentage) != getattr(progress_callback, 'last_percentage', -1):
                        await progress_message.edit(progress_text)
                        progress_callback.last_percentage = int(percentage)
                except Exception as e:
                    logger.warning(f"⚠️ Error updating progress message: {str(e)}")
            
            file_path = await event.download_media(DOWNLOAD_PATH, progress_callback=progress_callback)
            size_bytes = os.path.getsize(file_path)
            file_size = size_bytes / (1024 * 1024)  # Size in MB

            logger.info(f"✅ File downloaded: {file_path} ({file_size:.2f} MB)")
            stats['success'] = stats.get('success', 0) + 1
            stats['total_bytes'] = stats.get('total_bytes', 0) + size_bytes
            save_stats()
            await progress_message.edit("📥 Download completed! ✅")
        except Exception as e:
            logger.error(f"❌ Error during download: {str(e)}")
            try:
                await progress_message.edit("❌ Download failed!")
            except:
                await event.reply("❌ An error occurred during download.")
            stats['failed'] = stats.get('failed', 0) + 1
            save_stats()
    else:
        logger.info("📝 Message does not contain media, ignored.")

async def main():
    # Add a small delay to ensure client is fully connected
    await asyncio.sleep(1)
    
    # First connect to the chat to verify it exists
    is_setup_ok = await setup_client()
    if not is_setup_ok:
        logger.error("❌ Setup failed. Terminating program.")
        return
    
    logger.info("🚀 Bot started successfully!")
    logger.info(f"👀 Listening for new media in chat ID: {TARGET_CHAT_ID}")
    logger.info(f"👤 Downloads authorized only from user: {ALLOWED_USER}")
    
    # Show status summary message
    logger.info(f"📂 Download path: {DOWNLOAD_PATH}")
    logger.info(f"📜 Log file: {log_filename}")
    
    # Keep client running
    await client.run_until_disconnected()

# Start the bot
if __name__ == "__main__":
    try:
        logger.info("🔄 Starting Telegram client...")
        client.start()
        client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("👋 Bot manually interrupted")
    except Exception as e:
        logger.critical(f"❌ Critical error: {str(e)}")
    finally:
        logger.info("🛑 Bot terminated")
