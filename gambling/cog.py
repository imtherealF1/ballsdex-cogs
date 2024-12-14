import asyncio
import random
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from discord.ui import Button, button, View
from discord.utils import format_dt

from ballsdex.settings import settings
from ballsdex.core.models import BallInstance, Player
from ballsdex.core.utils.transformers import BallInstanceTransform

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot


class Card:
    SUITS = [":heart:", ":diamonds:", ":clubs:", ":spades:"]
    VALUES = [2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K", "A"]

    def __init__(self, value: int | str, suit: str) -> None:
        self.value = value
        self.suit = suit

    def __str__(self):
        return f"{self.value}{self.suit}"

    def get_value(self):
        if isinstance(self.value, int):
            return self.value
        elif self.value in ["J", "Q", "K"]:
            return 10
        elif self.value == "A":
            return 11


class BlackjackGame:
    def __init__(self):
        self.deck = [Card(value, suit) for suit in Card.SUITS for value in Card.VALUES]
        random.shuffle(self.deck)

    def deal_hand(self):
        return [self.deck.pop(), self.deck.pop()]

    @staticmethod
    def calculate_hand_value(hand):
        value = sum(card.get_value() for card in hand)
        aces = sum(1 for card in hand if card.value == "A")
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    @staticmethod
    def hand_to_str(hand):
        return " ".join(str(card) for card in hand)


class BlackjackGameView(View):
    def __init__(
        self,
        bot: "BallsDexBot",
        player,
        bj_game: BlackjackGame,
        countryball: BallInstanceTransform,
    ):
        super().__init__()
        self.bot = bot
        self.player = player
        self.bj_game = bj_game
        self.countryball = countryball
        self.player_hand = [bj_game.deck.pop()]
        self.ai_hand = [bj_game.deck.pop()]
        self.player_value = bj_game.calculate_hand_value(self.player_hand)
        self.ai_value = bj_game.calculate_hand_value(self.ai_hand)
        self.message = None

    async def send_initial_message(self, interaction: discord.Interaction):
        """Send the initial message and store its reference."""
        embed = discord.Embed(
            title="Blackjack",
            description=(
                f"Your first card: {self.bj_game.hand_to_str(self.player_hand)} "
                f"({self.player_value})"
            ),
            color=discord.Colour.blurple(),
        )
        embed.add_field(
            name="Bet",
            value=(
                f"{self.countryball.description(include_emoji=True, bot=self.bot, is_trade=False)}"
            ),
            inline=False,
        )

        await interaction.response.send_message(embed=embed, view=self)
        self.message = await interaction.original_response()

    @button(label="Hit", style=discord.ButtonStyle.primary)
    async def hit(self, button: Button, interaction: discord.Interaction):
        # TODO: fix annoying app fail on button tap
        self.player_hand.append(self.bj_game.deck.pop())
        self.player_value = self.bj_game.calculate_hand_value(self.player_hand)

        if self.player_value > 21:
            result = "You bust! You lose!"
            color = discord.Colour.red()
            reward = None
            await self.countryball.delete()
            await self.end_game(result, color, reward)
            return

        await self.update_embed("Hit! Your move.")

    @button(label="Stand", style=discord.ButtonStyle.secondary)
    async def stand(self, button: Button, interaction: discord.Interaction):
        # TODO: fix annoying app fail on button tap
        while self.ai_value < 17:
            self.ai_hand.append(self.bj_game.deck.pop())
            self.ai_value = self.bj_game.calculate_hand_value(self.ai_hand)

        result = ""
        color = discord.Colour.green()
        reward = None
        ball = await self.countryball.ball.first()
        if self.player_value > 21 or (self.ai_value <= 21 and self.ai_value >= self.player_value):
            result = "You lose!"
            color = discord.Colour.red()
            await self.countryball.delete()
        elif self.player_value == self.ai_value:
            result = "It's a draw!"
            color = discord.Colour.blurple()
            reward = f"{settings.collectible_name.title()} returned."
        else:
            result = "You win!"
            color = discord.Colour.green()
            reward = f"You win your bet {settings.collectible_name} and a new instance!"
            await BallInstance.create(
                player=self.player,
                ball=ball,
                attack_bonus=random.randint(-20, 20),
                health_bonus=random.randint(-20, 20),
            )

        await self.end_game(result, color, reward)

    async def end_game(self, result, color, reward):
        embed = discord.Embed(
            title="Blackjack Results",
            description=result,
            color=color,
        )
        embed.add_field(
            name="Your Hand",
            value=f"{self.bj_game.hand_to_str(self.player_hand)} ({self.player_value})",
            inline=False,
        )
        embed.add_field(
            name="AI's Hand",
            value=f"{self.bj_game.hand_to_str(self.ai_hand)} ({self.ai_value})",
            inline=False,
        )
        embed.add_field(
            name="Bet",
            value=f"{self.countryball.description(include_emoji=True, bot=self.bot, is_trade=False)}",
            inline=False,
        )
        if reward:
            embed.add_field(name="Reward", value=reward, inline=False)

        await self.message.edit(embed=embed, view=None)

    async def update_embed(self, title):
        """Updates the existing embed in the same message."""
        if not self.message:
            await self.send_initial_message()

        embed = discord.Embed(
            title=title,
            description="Make your move!",
            color=discord.Colour.blue(),
        )
        embed.add_field(
            name="Your Hand",
            value=f"{self.bj_game.hand_to_str(self.player_hand)} ({self.player_value})",
            inline=False,
        )
        embed.add_field(
            name="AI's Hand",
            value=f"{self.bj_game.hand_to_str(self.ai_hand)} ({self.ai_value})",
            inline=False,
        )
        embed.add_field(
            name="Bet",
            value=f"{self.countryball.description(include_emoji=True, bot=self.bot, is_trade=False)}",
            inline=False,
        )

        await self.message.edit(embed=embed, view=self)


class Gambling(commands.Cog):
    def __init__(self, bot: "BallsDexBot", bj: BlackjackGame):
        self.bot = bot
        self.bj = bj
        self.games = {}

    roulette = app_commands.Group(name="roulette", description="Roulette commands")

    @app_commands.command()
    async def blackjack(
        self,
        interaction: discord.Interaction,
        countryball: BallInstanceTransform,
    ):
        """
        Start an interactive blackjack game, where you bet a countryball.

        Parameters
        ----------
        countryball: BallInstanceTransform
            The countryball to bet.
        """
        player = await Player.get(discord_id=interaction.user.id)
        if countryball.special:
            await interaction.response.send_message(
                f"You cannot gamble with a special {settings.collectible_name}.", ephemeral=True
            )
            return

        bj_game = BlackjackGame()
        view = BlackjackGameView(self.bot, player, bj_game, countryball)
        await view.send_initial_message(interaction)

    @app_commands.command()
    async def slots(self, interaction: discord.Interaction, countryball: BallInstanceTransform):
        """
        Start a game of slots.

        Parameters
        ----------
        countryball: BallInstanceTransform
            The countryball to bet.
        """
        player = await Player.get(discord_id = interaction.user.id)
        bj_game = BlackjackGame()
        view = BlackjackGameView(self.bot, player, bj_game, countryball)

        emojis = ["🍒", "🍊", "🍋", "🍇", "🍉", "🍓"]
        result = [random.choice(emojis) for _ in range(3)]

        embed = discord.Embed(
            title="🎰 Slot Machine 🎰",
            description="Spinning... please wait...",
            color=discord.Color.blue()
        )

        start_format = [
            " 🍊 | 🍉 | 🍓",
            " 🍋 | 🍇 | 🍒",
            "🍋 | 🍊 | 🍇",
            "🍇 | 🍉 | 🍓",
            "🍒 | 🍉 | 🍊",
            "🍒 | 🍊 | 🍓"
        ]
        embed.add_field(name="Spinning...", value=random.choice(start_format), inline=False)
        await interaction.response.send_message(embed=embed)
        view.message = await interaction.original_response()

        for _ in range(5):
            result = [random.choice(emojis) for _ in range(3)]
            slot_result = " | ".join(result)
            embed.set_field_at(0, name="Spinning...", value=slot_result, inline=False)
            await view.message.edit(embed=embed)
            await asyncio.sleep(0.4)

        slot_result = " | ".join(result)
        embed = discord.Embed(
            title="🎰 Slot Machine 🎰",
            description=f"Result: {slot_result}",
            color=(
                discord.Color.green()
                if result[0] == result[1] == result[2]
                or any(result[i] == result[j] for i in range(3) for j in range(i + 1, 3))
                else discord.Color.red()
            ),
        )
        embed.add_field(
            name="Bet",
            value=(
                f"{countryball.description(include_emoji=True, bot=self.bot, is_trade=False)}"
            ),
            inline=False,
        )

        ball = await view.countryball.ball.first()
        if result[0] == result[1] == result[2]:
            embed.add_field(name="You win 4:1!", value="🎉 Congratulations! 🎉", inline=False)
            for u in range(3):
                await BallInstance.create(
                    player=player,
                    ball=ball,
                    attack_bonus=random.randint(-20, 20),
                    health_bonus=random.randint(-20, 20),
                )
            embed.set_footer(
                text=f"You won your bet back and 3 new {settings.plural_collectible_name}!"
            )
        elif any(result[i] == result[j] for i in range(3) for j in range(i + 1, 3)):
            embed.add_field(name="You win!", value="🎉 Congratulations! 🎉", inline=False)
            await BallInstance.create(
                player=player,
                ball=ball,
                attack_bonus=random.randint(-20, 20),
                health_bonus=random.randint(-20, 20),
            )
            embed.set_footer(text=f"You won your bet back and a new {settings.collectible_name}!")
        else:
            embed.add_field(name="You Lose!", value="😞 Better luck next time! 😞", inline=False)
            await countryball.delete()
            embed.set_footer(text="You lost your bet.")

        await view.message.edit(embed=embed)

    @roulette.command(name="start")
    @app_commands.choices(
        mode=[
            Choice(name="Alone", value=1),
            Choice(name="With other players", value=2),
        ])
    async def roulette_start(
        self,
        interaction: discord.Interaction,
        mode: Choice[int],
        countryball: BallInstanceTransform | None = None,
        bet_number: int | None = None,
        bet_color: str | None = None,
        time_before_start: int | None = 30,
    ):
        """
        Start a game of roulette.

        Parameters
        ----------
        mode: Choice[int]
            Whether to play alone or with other players.
        countryball: BallInstanceTransform
            The countryball to bet.
        bet_number: int
            The number to bet on if any.
        bet_color: str
            The color to bet on if any (red, black, or green).
        time_before_start: int
            How many seconds to wait before starting (only applicable for `other players` mode)
        """
        if mode.value == 1:
            if (bet_color and bet_number) or (not bet_color and not bet_number):
                await interaction.response.send_message(
                    "You need to select either `bet_color` or `bet_number`.", ephemeral=True
                )
                return

            if bet_color and bet_color.lower() not in ["red", "black", "green"]:
                await interaction.response.send_message(
                    "Invalid color! Choose from `red`, `black`, or `green`.", ephemeral=True
                )
                return

            if not countryball:
                await interaction.response.send_message(
                    "You must not leave `countryball` empty when starting "
                    "a roulette game with `mode` set to `Alone`.",
                    ephemeral=True,
                )
                return

            if time_before_start:
                await interaction.response.send_message(
                    "You must not add a value for `time_before_start` when starting "
                    "a roulette game with `mode` set to `Alone`.",
                    ephemeral=True,
                )
                return

            if bet_number:
                if bet_number < 0 or bet_number > 19:
                    await interaction.response.send_message(
                        "`bet_number` must be 0 or bigger, and 19 or smaller.", ephemeral=True
                    )
                    return

            player = await Player.get(discord_id=interaction.user.id)
            if countryball.special:
                await interaction.response.send_message(
                    f"You cannot gamble with a special {settings.collectible_name}.", ephemeral=True
                )
                return

            embed = discord.Embed(
                title="🎡 Roulette 🎡",
                description="Spinning the wheel...",
                color=discord.Color.blue(),
            )
            embed.add_field(
                name="Bet",
                value=f"{countryball.description(include_emoji=True, bot=self.bot, is_trade=False)}",
                inline=False,
            )
            if bet_number:
                embed.add_field(name="Bet Number", value=str(bet_number), inline=False)
            if bet_color:
                embed.add_field(name="Bet Color", value=bet_color.capitalize(), inline=False)

            await interaction.response.send_message(embed=embed)
            message = await interaction.original_response()

            await asyncio.sleep(2)

            pockets = [f"{color}{number}" for color, number in zip(
                ["🔴"] * 18 + ["⚫"] * 18 + ["🟢"], list(range(1, 19)) * 2 + [0]
            )]
            result = random.choice(pockets)
            result_color = "red" if "🔴" in result else "black" if "⚫" in result else "green"
            result_number = int(result[1:]) if result[1:].isdigit() else 0
            color_handler = (
                discord.Colour.green()
                if bet_color is not None and result_color == bet_color
                or bet_number is not None and result_number == bet_number
                else discord.Colour.red()
            )

            embed = discord.Embed(
                title="🎡 Roulette Results 🎡",
                description=f"The wheel lands on {result}!",
                color=color_handler,
            )
            embed.add_field(
                name="Bet",
                value=f"{countryball.description(include_emoji=True, bot=self.bot, is_trade=False)}",
                inline=False,
            )

            reward = 0
            ball = await countryball.ball.first()

            if bet_number == result_number:
                reward = 18
                embed.add_field(name="You guessed the number!", value="🎉 18:1 payout! 🎉", inline=False)
            elif bet_color and bet_color.lower() == result_color:
                reward = 18 if result_color == "green" else 2
                embed.add_field(
                    name="You guessed the color!",
                    value=f"🎉 {reward}:1 payout! 🎉",
                    inline=False,
                )
            else:
                embed.add_field(
                    name="Better luck next time.", value="😞 You lost your bet. 😞", inline=False
                )
                await countryball.delete()

            if reward > 0:
                for _ in range(reward - 1):
                    await BallInstance.create(
                        player=player,
                        ball=ball,
                        attack_bonus=random.randint(-20, 20),
                        health_bonus=random.randint(-20, 20),
                    )

            await message.edit(embed=embed)
        else:
            if countryball:
                await interaction.response.send_message(
                    "You must not use `countryball` when starting "
                    "a roulette game with `mode` set to `With other players`.",
                    ephemeral=True,
                )
                return

            if bet_number or bet_color:
                await interaction.response.send_message(
                    "You must use neither `bet_number`, nor `bet_color` when starting "
                    "a roulette game with `mode` set to `With other players`.",
                    ephemeral=True,
                )
                return

            game_id = random.randint(100, 99999)
            remaining_time = datetime.now(timezone.utc) + timedelta(seconds=time_before_start)
            time = format_dt(remaining_time, style="R")
            self.games[game_id] = {"players": [], "bets": []}
            embed = discord.Embed(
                title="🎡 Roulette Game 🎡",
                description=(
                    "A new roulette game has started! Use `/roulette add` to join "
                    f"with your bet.\nThis roulette game will start {time}."
                ),
                color=discord.Color.blue(),
            )
            embed.add_field(name="Game ID", value=f"#{game_id}", inline=False)
            embed.add_field(name="Bets", value="No bets yet.", inline=False)
            await interaction.response.send_message(embed=embed)
            message = await interaction.original_response()

            for _ in range(time_before_start):
                await asyncio.sleep(1)
                if not self.games[game_id]["bets"]:
                    continue

                bets_summary = "\n".join(
                    [
                        f"{bet['player'].mention}: "
                        f"{bet['countryball'].description(
                            include_emoji=True, bot=self.bot, is_trade=False
                        )} "
                        for bet in self.games[game_id]["bets"]
                    ]
                )

                embed.set_field_at(1, name="Bets", value=bets_summary)
                await message.edit(embed=embed)

            if not self.games[game_id]["bets"]:
                embed.description = "No bets were placed. The game has been canceled."
                embed.color = discord.Color.red()
                await message.edit(embed=embed)
                if game_id in self.games:
                    del self.games[game_id]
                return

            pockets = [f"🔴{i}" for i in range(1, 19)] + [f"⚫{i}" for i in range(1, 19)] + ["🟢0"]
            result = random.choice(pockets)
            result_color = "red" if "🔴" in result else "black" if "⚫" in result else "green"
            result_number = int(result[1:]) if result[1:].isdigit() else 0

            winners = []
            losers = []
            for bet in self.games[game_id]["bets"]:
                player = bet["db_player"]
                countryball = bet["countryball"]
                bet_number = bet["bet_number"]
                bet_color = bet["bet_color"]
                reward = 0

                if bet_number == result_number:
                    reward = 18
                elif bet_color and bet_color.lower() == result_color:
                    reward = 18 if result_color == "green" else 2

                if reward > 0:
                    ball = await countryball.ball.first()
                    for _ in range(reward - 1):
                        await BallInstance.create(
                            player=player,
                            ball=ball,
                            attack_bonus=random.randint(-20, 20),
                            health_bonus=random.randint(-20, 20),
                        )
                    winners.append(f"<@{player.discord_id}>")
                else:
                    await countryball.delete()
                    losers.append(f"<@{player.discord_id}>")

            embed = discord.Embed(
                title="🎡 Roulette Results 🎡",
                description=f"The wheel lands on {result}!",
                color=discord.Color.green() if winners else discord.Color.red(),
            )
            if winners:
                embed.add_field(name="Winners", value=", ".join(winners), inline=False)
            if losers:
                embed.add_field(name="Losers", value=", ".join(losers), inline=False)

            await message.edit(embed=embed)
            if game_id in self.games:
                del self.games[game_id]

    @roulette.command(name="add")
    async def roulette_add(
        self,
        interaction: discord.Interaction,
        game_id: int,
        countryball: BallInstanceTransform,
        bet_number: int | None = None,
        bet_color: str | None = None,
    ):
        """
        Add a countryball as a bet to a roulette game.

        Parameters
        ----------
        """
        if game_id not in self.games:
            await interaction.response.send_message(
                "Invalid game ID. Please ensure the game is active.", ephemeral=True
            )
            return

        if any(bet["player"] == interaction.user for bet in self.games[game_id]["bets"]):
            await interaction.response.send_message(
                "You have already joined this game.", ephemeral=True
            )
            return

        if bet_color and bet_color.lower() not in ["red", "black", "green"]:
            await interaction.response.send_message(
                "Invalid color! Choose from `red`, `black`, or `green`.", ephemeral=True
            )
            return

        if bet_number and (bet_number < 0 or bet_number > 19):
            await interaction.response.send_message(
                "`bet_number` must be between 0 and 19.", ephemeral=True
            )
            return

        if (bet_color and bet_number) or (not bet_color and not bet_number):
            await interaction.response.send_message(
                "You need to select either `bet_color` or `bet_number`.", ephemeral=True
            )
            return

        db_player = await Player.get(discord_id=interaction.user.id)
        if countryball.special:
            await interaction.response.send_message(
                f"You cannot gamble with a special {settings.collectible_name}.", ephemeral=True
            )
            return

        self.games[game_id]["bets"].append(
            {
                "player": interaction.user,
                "db_player": db_player,
                "countryball": countryball,
                "bet_number": bet_number,
                "bet_color": bet_color,
            }
        )

        await interaction.response.send_message(
            f"You have joined Roulette Game #{game_id}!", ephemeral=True
        )
