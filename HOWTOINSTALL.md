#  F1 BallsDex Cogs

## Gambling

### How to Install

1. Grab the folder named `gambling` from the repository, and drag it to your
dex's folder. Then, drag it inside the folder named `ballsdex`, then into `packages`,
and drop it there.
2. If your bot version is 2.22.0 or after, go to `config.yml`, and go to `packages:`.
There, you will see a list of packages, e.g:
* "# list of packages that will be loaded
packages:
  - ballsdex.packages.admin
  - ballsdex.packages.balls
  - ballsdex.packages.config
  - ballsdex.packages.countryballs
  - ballsdex.packages.info
  - ballsdex.packages.players
  - ballsdex.packages.trade"
* In there, below trade, go ahead and add:
`- ballsdex.packages.gambling`
Make sure it's at the same place horizontally, and then save the file.
If your bot version is before 2.22.0, tap the `ballsdex` folder, then `core`, and then
`bot.py`. In there, you will find:
`PACKAGES = ["config", "players", "countryballs", "info", "admin", "trade", "balls"]`
After `"balls"`, go ahead and add `"gambling"`, so it should be:
`PACKAGES = ["config", "players", "countryballs", "info", "admin", "trade", "balls", "gambling"]`
For support regarding the commands, make an issue on the [GitHub repository](https://github.com/imtherealF1/ballsdex-cogs). Enjoy!
