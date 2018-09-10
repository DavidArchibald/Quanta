#!/usr/bin/env python3
from discord.ext import commands

from typing import Optional

from ..helpers.database_helper import Database
from ..handlers.exit_handling import ExitHandler

exit_handler: Optional[ExitHandler] = None
bot: Optional[commands.Bot] = None
database: Optional[Database] = None
is_ready: bool = False
