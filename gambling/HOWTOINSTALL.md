# F1 BallsDex Cogs

## Gambling Cogs Installation Guide

### Step 1: Download the gambling package

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
           await ctx.send(f"Failed to fetch {file}. `({request.status_code})`")
           break
   
       # Decode the remote content
       remote_content = base64.b64decode(request.json()["content"]).decode("UTF-8")
       local_file_path = f"{PATH}/{file}"
   
       # Check if the local file exists
       if os.path.exists(local_file_path):
           with open(local_file_path, "r") as local_file:
               local_content = local_file.read()
           # Compare local and remote contents
           if local_content == remote_content:
               await ctx.send(f"'{file}' is already up-to-date. ({index + 1}/{len(FILES)})")
               continue
   
       # Write the updated or new file
       with open(local_file_path, "w") as opened_file:
           opened_file.write(remote_content)
   
       await ctx.send(f"Updated '{file}' ({index + 1}/{len(FILES)})")
   
   await ctx.send("Finished installing or updating everything!")
     ```
- This eval either updates or installs the package, use this for updating too.

2. Replace b. in b.eval with your bot's prefix, it's by default `b.`

### Step 2: Add the cog to your bot

#### For bot version 2.22.0 or later:

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

#### For older bot versions:

1. Navigate to `ballsdex/core/bot.py`.
2. Locate the `PACKAGES` list:

    ```py
    PACKAGES = ["config", "players", "countryballs", "info", "admin", "trade", "balls"]
    ```

3. Add "gambling" to the list:

    ```py
    PACKAGES = ["config", "players", "countryballs", "info", "admin", "trade", "balls", "gambling"]
    ```

4. Save the file.

### Support

For assistance with commands or issues, please open an issue on the [GitHub repository](https://github.com/imtherealf1/ballsdex-cogs).
