#!/usr/bin/env python3
from typing import Optional

from discord.ext import commands

from ..handlers.exit_handling import ExitHandler
from ..helpers.database_helper import Database

exit_handler: Optional[ExitHandler] = None
bot: Optional[commands.Bot] = None
database: Optional[Database] = None
is_ready: bool = False
