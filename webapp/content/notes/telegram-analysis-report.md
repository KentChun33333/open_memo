# Telegram Integration Analysis & Security Fix Report

*Date: February 20, 2026*

## Background

The WebApp's "Active Consciousness" tab (`ReflectionAgent.jsx`) contained hardcoded hyperlinked suggestions pointing to `t.me/Clawdbot`.

## The Vulnerability

Clicking these Deep Links opens the user's Telegram application and drafts a message directly to the `@Clawdbot` account.
Because Telegram deep links sidestep the web app's authentication entirely, a user did not theoretically need to be logged into the WebApp (or even visit the WebApp) to send a message to the bot. Anyone observing the link or knowing the bot's username could interact with the conversational AI python backend directly.

If the Pybot handler does not check user authorization, this setup was fully exposed to the public internet, risking:

1. High API usage (OpenAI/Anthropic token scraping)
2. Potential memory poisoning/context manipulation
3. Unauthorized usage of background scraping and execution tools.

## The Solution

To secure the backend while allowing the frontend links to remain clickable for the authorized owner, the following patch was deployed to the Telegram long-polling handler in the `nanobot` repository (`nanobot/channels/telegram.py`):

1. **Allowlist Configuration:** Leveraging the `TelegramConfig` class, an array property `allow_from` specifies which Telegram User IDs are permitted to interact.
2. **Auth Verification Function:**

```python
def _is_allowed(self, user) -> bool:
    if not self.config.allow_from:
        return True # Default open if empty

    allowed = [str(a) for a in self.config.allow_from]
    if str(user.id) in allowed or (user.username and user.username in allowed):
        return True
    return False
```

3. **Execution Pipeline Block:** Both `_on_start` and the primary `_on_message` routes were updated to run the `_is_allowed()` check before sending typing indicators, starting workflows, or responding.

### Resulting Architecture

The `t.me` links can now safely exist in the frontend UI. If an unauthorized user attempts to trigger the bot via the web deep-links or manual Telegram searches, their requests are immediately and silently ignored by the `nanobot` Python process.

## Note on "Clawdbot" Naming

The username `Clawdbot` hardcoded in the frontend is a default placeholder. For the links to function correctly for the intended owner, the frontend `ReflectionAgent.jsx` should be updated to match the actual username of the Telegram Bot registered with `@BotFather`.
