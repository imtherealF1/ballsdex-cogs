# F1 BallsDex Cogs

## Battling Cogs Installation Guide

### Step 1: Downloading the battling package

1. Run the following command in a server where your bot is present:
   ```py
   b.eval
   import os
   import base64
   import requests

   PATH = "ballsdex/packages/battle"
   GITHUB = "https://api.github.com/repos/imtherealf1/ballsdex-cogs/contents/battle"
   FILES = [
       "__init__.py", "cog.py", "menu.py", "HOWTOINSTALL.md", "display.py", "battle_user.py"
   ]

   os.makedirs(PATH, exist_ok=True)

   for index, file in enumerate(FILES):
       response = requests.get(f"{GITHUB}/{file}")

       if response.status_code != requests.codes.ok:
           await ctx.send(f"Failed to install `{file}`. (Error: {response.status_code})")
           break

       with open(f"{PATH}/{file}", "w") as opened_file:
           content = base64.b64decode(response.json()["content"])
           opened_file.write(content.decode("utf-8"))

       await ctx.send(f"Installed `{file}` ({index + 1}/{len(FILES)})")

   await ctx.send("Battle package installation complete!")
   ```

2. Replace b. with your bot's prefix (default is b.).

### Step 2: Configure the bot to load the package

#### For bot versions 2.22.0 or later:

1. Open your `config.yml` file.
2. Find the `packages:` section and add the battle package:

   ```yaml
   packages:
   - ballsdex.packages.admin
   - ballsdex.packages.balls
   - ballsdex.packages.config
   - ballsdex.packages.countryballs
   - ballsdex.packages.info
   - ballsdex.packages.players
   - ballsdex.packages.trade
   - ballsdex.packages.battle

3. Save the file.

#### For older bot versions:

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

### Step 3: Add Database Migrations

1. Navigate to the `ballsdex/migrations/models` folder.
2. Note the number of the latest migration file (e.g., `35_20240913181322_update.sql`, in this case number is 35).
3. Create a new migration file with the next number, following this format: `number_yearmonthdayhourminutesecond_update.sql`.
If you aren't sure on the seconds, put a random integer between 01-60. 
4. Insert the following SQL code into the new file:

   ```sql
   -- upgrade --
   ALTER TABLE "player" ADD "battles_won" INT NOT NULL DEFAULT 0;
   ALTER TABLE "player" ADD "battles_drawn" INT NOT NULL DEFAULT 0;
   ALTER TABLE "player" ADD "battles_lost" INT NOT NULL DEFAULT 0;

   -- downgrade --
   ALTER TABLE "player" DROP COLUMN "battles_won";
   ALTER TABLE "player" DROP COLUMN "battles_drawn";
   ALTER TABLE "player" DROP COLUMN "battles_lost";

   ```

6. Ensure there is a blank line at the end of the file to avoid formatting errors.
7. Save the file.

### Step 4: Update the Player Model

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

4. Save the file.

### Support

For help or issues, open an issue on the [GitHub repository](https://github.com/imtherealf1/ballsdex-cogs).
