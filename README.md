# Telegram Media Downloader Bot

A Python bot that automatically downloads media files from a specific Telegram chat when sent by authorized users. The bot monitors a designated chat and downloads any media (videos, images, documents) to a specified local directory.

## Features

- 🔐 **User Authorization**: Only specified users can trigger downloads
- 📁 **Automatic Download**: Downloads media files to a configurable directory
- 📊 **Progress Tracking**: Shows real-time download progress with progress bars
- 📝 **Comprehensive Logging**: Detailed logs with timestamps and status updates
- 🛡️ **Error Handling**: Robust error handling and recovery
- 🔄 **Session Persistence**: Maintains login session across restarts
- ⏸️ **Pause/Resume Downloads**: Temporarily pause automatic downloads
- 📈 **Persistent Statistics**: Tracks download counts and sizes across restarts
- 💾 **Disk Usage Monitoring**: Shows disk space with warnings
- 🕒 **Uptime Tracking**: Displays how long the bot has been running
- 💬 **Interactive Commands**: Control the bot with slash commands

## Prerequisites

- Python 3.7 or higher
- A Telegram account
- Telegram API credentials (API_ID and API_HASH)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd telegram-media-downloader
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Get Telegram API credentials**:
   - Go to [my.telegram.org](https://my.telegram.org)
   - Log in with your phone number
   - Go to "API Development Tools"
   - Create a new application to get your `API_ID` and `API_HASH`

## Configuration

1. **Copy the example configuration file**:
   ```bash
   cp config.env.example config.env
   ```

2. **Edit `config.env` with your settings**:
   ```env
   # Telegram API credentials
   API_ID=your_api_id_here
   API_HASH=your_api_hash_here
   
   # Download directory (absolute path)
   DOWNLOAD_PATH=/path/to/your/download/folder
   
   # Target chat ID (group/channel/private chat)
   TARGET_CHAT_ID=-1001234567890
   
   # Authorized user (username without @ or numeric user ID)
   ALLOWED_USER=your_username
   ```

### Configuration Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `API_ID` | Your Telegram API ID | `12345678` |
| `API_HASH` | Your Telegram API Hash | `abcdef1234567890abcdef1234567890` |
| `DOWNLOAD_PATH` | Absolute path where files will be saved | `/home/user/downloads` |
| `TARGET_CHAT_ID` | Chat ID to monitor (see below for how to get this) | `-1001234567890` |
| `ALLOWED_USER` | Username (without @) or numeric user ID | `john_doe` or `123456789` |
| `STATS_FILE` | Path to JSON file for statistics | `bot_stats.json` |
| `DISK_WARNING_THRESHOLD` | Disk usage warning percentage | `90` |

### Getting the Chat ID

There are several ways to get a chat ID:

1. **For groups/channels**: Use [@userinfobot](https://t.me/userinfobot) - forward a message from the target chat
2. **Using the bot**: Add some temporary logging to see chat IDs in the console
3. **Telegram web**: Check the URL when viewing the chat
4. **For private chats**: Use the user's numeric ID

## Usage

1. **Start the bot**:
   ```bash
   python bot.py
   ```

2. **First run**: The bot will ask you to authenticate with Telegram (enter your phone number and verification code)

3. **Monitor logs**: Check the console output or the log files in the `logs/` directory

4. **Send media**: Have the authorized user send media files to the target chat

### Commands

Use these slash commands in the target chat:

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/help` | Show command list |
| `/status` | Current bot status |
| `/stats` | Detailed download statistics |
| `/pause` | Pause automatic downloads |
| `/resume` | Resume automatic downloads |
| `/disk` | Disk usage information |
| `/logs` | Show recent log entries |

Example:

```
/status
📊 Bot Status
🟢 Status: Running
⏱️ Uptime: 2:30:15
✅ Downloads: 47
📁 Total size: 2.3 GB
```

```
/disk
💾 Disk Usage Information
📂 Path: /downloads
💽 Total: 500 GB
📊 Used: 234 GB (46.8%)
🆓 Free: 266 GB
🟢 Status: Good
```

## How It Works

1. The bot connects to Telegram using your API credentials
2. It monitors the specified chat for new messages
3. When a message with media is received from an authorized user:
   - Downloads the media file to the specified directory
   - Shows download progress in real-time
   - Logs the operation details
4. Messages from unauthorized users are ignored

## Logging

The bot creates detailed logs in the `logs/` directory:
- Log files are named with the current date: `telegram_downloader_YYYY-MM-DD.log`
- Logs include timestamps, user information, download progress, and errors
- Both file and console logging are enabled

## File Structure

```
telegram-media-downloader/
├── bot.py                    # Main bot script
├── config.env               # Configuration file (create from example)
├── config.env.example       # Example configuration
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── LICENSE                 # GPL v3 license
├── logs/                   # Log files directory (auto-created)
└── session_name.session    # Telegram session file (auto-created)
```

## Security Considerations

- Keep your `config.env` file secure
- The `session_name.session` file contains your authentication data - keep it secure
- Only authorized users can trigger downloads, but ensure your chat is properly secured
- Consider the legal implications of downloading media content

## Troubleshooting

### Common Issues

1. **"Could not find chat with ID"**:
   - Verify the chat ID is correct
   - Ensure your account is a member of the target chat
   - For private chats, make sure you have a conversation history

2. **"API_ID or API_HASH not found"**:
   - Check that `config.env` exists and contains valid credentials
   - Ensure there are no extra spaces or quotes in the configuration

3. **"Download folder does not exist"**:
   - Create the download directory or update the path in `config.env`
   - Ensure the path is absolute and the bot has write permissions

4. **Authentication issues**:
   - Delete the `session_name.session` file and restart the bot
   - Ensure your API credentials are correct

### Debug Mode

For detailed debugging, you can modify the logging level in `bot.py`:
```python
logging.basicConfig(level=logging.DEBUG, ...)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This bot is for educational and personal use only. Users are responsible for complying with Telegram's Terms of Service and applicable laws regarding media downloading and storage. The authors are not responsible for any misuse of this software.

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the log files for error details
3. Ensure all configuration parameters are correct
4. Create an issue with detailed error information and logs

---

**Note**: This bot requires your Telegram account credentials and should be used responsibly. Always respect copyright laws and Telegram's terms of service when downloading media content.
