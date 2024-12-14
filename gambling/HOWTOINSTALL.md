# F1 BallsDex Cogs

## Gambling Cogs Installation Guide

### Steps to Install

1. **Download the Gambling Package:**
   - On a server that your bot is in, run the following eval:
     b.eval
     ```py
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

          await ctx.send(f"Installed `{file}` ({index + 1}/{len(FILES)})")

     await ctx.send("Finished installing everything!")
      ```
   - Replace b. in b.eval with your bot's prefix, it's by default `b.`

2. **For Bot Version 2.22.0 or Later:**
   - Open `config.yml` and locate the `packages:` section.
   - Add the gambling package to the list of packages:
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
   - Save the file.

3. **For Bot Versions Before 2.22.0:**
   - Navigate to `ballsdex/core/bot.py`.
   - Find the `PACKAGES` list and add `"gambling"` after `"balls"`:
     ```python
     PACKAGES = ["config", "players", "countryballs", "info", "admin", "trade", "balls", "gambling"]
     ```
   - Save the file.

### Support

For assistance with commands or issues, please open an issue on the [GitHub repository](https://github.com/imtherealF1/ballsdex-cogs).
