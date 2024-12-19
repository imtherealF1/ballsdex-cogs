import base64
import os
from datetime import datetime

import requests
from tortoise import Tortoise

PATH = "ballsdex/packages/battle"
GITHUB = "imtherealf1/ballsdex-cogs/contents/battle"
FILES = ["__init__.py", "cog.py", "display.py", "HOWTOINSTALL.md", "menu.py", "battle_user.py"]

MIGRATION = """-- upgrade --
ALTER TABLE "player" ADD "battles_won" INT NOT NULL DEFAULT 0;
ALTER TABLE "player" ADD "battles_drawn" INT NOT NULL DEFAULT 0;
ALTER TABLE "player" ADD "battles_lost" INT NOT NULL DEFAULT 0;

-- downgrade --
ALTER TABLE "player" DROP COLUMN "battles_won";
ALTER TABLE "player" DROP COLUMN "battles_drawn";
ALTER TABLE "player" DROP COLUMN "battles_lost";"""

MODEL_CONTENT = """
    battles_won = fields.IntField(null=False, default=0)
    battles_drawn = fields.IntField(null=False, default=0)
    battles_lost = fields.IntField(null=False, default=0)
"""

os.makedirs(PATH, exist_ok=True)


async def add_to_file(file, add, search, stop):
  """
  Adds content underneath of a line in a file.

  Parameters
  ----------
  file: str
    The file you want to read and write back to.
  add: tuple[str, int]
    The content you want to add and the amount of lines it will be under `search`.
  search: str
    The line you want to add the content underneath of.
  stop: str
    If the content in `stop` is found within the file, the function will stop.
  """
  with open(file, "r") as read_file:
    lines = read_file.readlines()
  
  stripped_lines = [x.lstrip() for x in lines]
  
  if stop in stripped_lines:
    return

  if search[0] in stripped_lines:
     lines.insert(stripped_lines.index(search[0]) + add[1], add)

  with open(file, "w") as write_file:
    write_file.writelines(lines)

  await ctx.send(f"Updated {file}")


async def run_migration(migration):
  """
  Creates a migration file and runs it live.

  Parameters
  ----------
  migration: str
    The SQL code the file will contain and the code that will be run.
  """
  current = datetime.now().strftime("%Y%m%d%H%M%S")

  version = len([f for f in os.listdir("migrations/models") if f.endswith(".sql")]) + 1

  file_name = f"{version}_{current}_update.sql"

  with open(f"migrations/models/{file_name}", "w") as file:
    file.write(migration)

  await Tortoise.get_connection("default").execute_query(
    migration.split("-- downgrade --")[0]
  )


async def add_package(package: str):
    """
    Adds a package to the config.yml file.

    Parameters
    ----------
    package: str
      The package you want to append to the config.yml file.
    """
    with open("config.yml", "r") as file:
      lines = file.readlines()

    item = f"  - {package}\n"

    if "packages:\n" not in lines or item in lines:
      return

    for i, line in enumerate(lines):
      if line.rstrip().startswith("packages:"):
          lines.insert(i + 1, item)
          break

    with open("config.yml", "w") as file:
      file.writelines(lines)

    await ctx.send("Added package to config file")


async def install_files():
    """
    Installs and updates files from the GitHub page.
    """
    for index, file in enumerate(FILES):
        request = requests.get(f"https://api.github.com/repos/{GITHUB}/{file}")

        if request.status_code != requests.codes.ok:
            await ctx.send(f"Failed to fetch {file}. `({request.status_code})`")
            break

        remote_content = base64.b64decode(request.json()["content"]).decode("UTF-8")
        local_file_path = f"{PATH}/{file}"

        if os.path.exists(local_file_path):
            with open(local_file_path, "r") as local_file:
                if local_file.read() == remote_content:
                    await ctx.send(f"'{file}' is already up-to-date. ({index + 1}/{len(FILES)})")
                    continue

        with open(local_file_path, "w") as opened_file:
            opened_file.write(remote_content)

        await ctx.send(f"Updated '{file}' ({index + 1}/{len(FILES)})")

found_migration = False

for file_name in os.listdir("migrations/models"):
  if not file_name.endswith(".sql"):
    continue

  with open("migrations/models/" + file_name, "r") as file:
    if MIGRATION in file.read():
      found_migration = True
      break

await install_files()
await add_package(PATH.replace("/", "."))

if not found_migration:
  await run_migration(MIGRATION)

await add_to_file(
  "models.py",
  (MODEL_CONTENT, 5),
  "friend_policy = fields.IntEnumField(\n",
  "battles_won = fields.IntField(null=False, default=0)\n",
)

await ctx.send("Finished installing/updating everything!")
