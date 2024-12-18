# F1 BallsDex Cogs

## Battle Cog Installation Guide

The following guide will assist you with installing the battle package. You are required to restart your bot to install this package.

### Step 1: Download The Battle Package

Inside of a server your bot is in, run the following eval code, replacing `b.` with your bot's prefix:

```py
b.eval
import base64, requests
r = requests.get(
    "https://api.github.com/repos/imtherealf1/ballsdex-cogs/contents/battle/installer.py"
)

if r.status_code == requests.codes.ok:
    content = base64.b64decode(r.json()["content"])
    await ctx.invoke(bot.get_command("eval"), body=content.decode("UTF-8"))
else:
    await ctx.send("Failed to install package.\nPlease submit an issue on the GitHub page.")
    print(f"ERROR CODE: {r.status_code}")
```

This eval will install and update the package using the package installer from the GitHub page.

### Step 2: Add The Package

> [!IMPORTANT]
> The installer will automatically add the package into your config.yml file if your Ballsdex instance is running on a version greater than or equal to **VERSION 2.22.0**. If your version is lower than version 2.22.0, follow the guide below.

1. Open `ballsdex/core/bot.py`.
2. Locate the `PACKAGES` list:

    ```py
    PACKAGES = ["config", "players", "countryballs", "info", "admin", "trade", "balls"]
    ```

3. Add "battle" to the list:

    ```py
    PACKAGES = ["config", "players", "countryballs", "info", "admin", "trade", "balls", "battle"]
    ```

4. Save the file.

### Step 3: Update The Player Model

1. Open `ballsdex/core/models.py`.
2. Find the player model:

    ```py
    class Player(models.Model):
        discord_id = fields.BigIntField(
            description="Discord user ID", unique=True, validators=[DiscordSnowflakeValidator()]
        )
        donation_policy = fields.IntEnumField(
            DonationPolicy,
            description="How you want to handle donations",
            default=DonationPolicy.ALWAYS_ACCEPT,
        )
        privacy_policy = fields.IntEnumField(
            PrivacyPolicy,
            description="How you want to handle privacy",
            default=PrivacyPolicy.DENY,
        )
    ```

3. Add the following fields to the model:

    ```py
    battles_won = fields.IntField(null=False, default=0)
    battles_drawn = fields.IntField(null=False, default=0)
    battles_lost = fields.IntField(null=False, default=0)
    ```

- Make sure to use correct indentation.

4. Save the file and restart your bot.

### Step 4: Load The Package

Once you have finished all of the steps, restart your bot to load the battle package.

### Support

For assistance with commands or issues, please open an issue on the [GitHub repository](https://github.com/imtherealf1/ballsdex-cogs).
