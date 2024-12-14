# F1 BallsDex Cogs

## Gambling Cogs Installation Guide

### Steps to Install

1. **Download the Gambling Package:**
   - Clone or download the `gambling` folder from the repository.
   - Move it to your `ballsdex/packages` directory in your bot's root folder.

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
