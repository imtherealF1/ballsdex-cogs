# F1 BallsDex Cogs

## Gambling Cogs Installation Guide

### Steps to install

#### Step 1: Download the gambling package
1. On a guild that your bot is in, run the following eval:
   ```py
   b.eval
   import os
   import base64
   import requests

   PATH = "ballsdex/packages/gambling"
   GITHUB = "https://api.github.com/repos/imtherealf1/ballsdex-cogs/contents/gambling"
   FILES = ["__init__.py", "cog.py", "blackjack.py", "HOWTOINSTALL.md"]

   os.makedirs(PATH, exist_ok=True)

   for index, file in enumerate(FILES):
      request = requests.get(f"{GITHUB}/{file}")

      if request.status_code != requests.codes.ok:
         await ctx.send(f"Failed to install {file}. `({request.status_code})`")
         break

      with open(f"{PATH}/{file}", "w") as opened_file:
         content = base64.b64decode(request.json()["content"])
         opened_file.write(content.decode("UTF-8"))

      await ctx.send(f"Installed '{file}' ({index + 1}/{len(FILES)})")

   await ctx.send("Finished installing everything!")
     ```
2. Replace b. in b.eval with your bot's prefix, it's by default `b.`

#### Step 2: Add the cog to your bot

**For bot version 2.22.0 or later:**

1. Open `config.yml` and locate the `packages:` section.
2. Add the gambling package to the list of packages:
   ```yaml
   packages:
      - ballsdex.packages.admin
      - ballsdex.packages.balls
      - ballsdex.packages.config
      - ballsdex.packages.countryballs
      - ballsdex.packages.info
      - ballsdex.packages.players
      - ballsdex.packages.trade
      - ballsdex.packages.gambling
   ```
3. Save the file.

**For bot versions before 2.22.0:**

1. Navigate to `ballsdex/core/bot.py`.
2. Find the `PACKAGES` list and add `"gambling"` after `"balls"`:
   ```py
   PACKAGES = ["config", "players", "countryballs", "info", "admin", "trade", "balls", "gambling"]
   ```
3. Save the file.

### Support

For assistance with commands or issues, please open an issue on the [GitHub repository](https://github.com/imtherealf1/ballsdex-cogs).
