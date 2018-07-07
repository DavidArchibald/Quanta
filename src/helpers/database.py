import discord
from discord.ext import commands

import psycopg2

import os
import os.path

import json

connection = None
cursor = None
def connect(dbInfoPath = None):
    global connection # I should probably make this a class
    global cursor

    dbname = None
    user = None
    password = None

    dbInfoPath = dbInfoPath or os.path.join(os.path.dirname(__file__), "../secrets/dbInfo.json")
    with open(dbInfoPath, "r") as dbInfoFile:
        dbInfo = json.load(dbInfoFile)
        dbname = dbInfo["dbname"]
        user = dbInfo["user"]
        password = dbInfo["password"]
        host = dbInfo.get("host", None)
        port = dbInfo.get("port", None)

    connection = psycopg2.connect(dbname = dbname, user = user, password = password, host = host, port = port)
    cursor = connection.cursor()

def get_prefix(identifier):
    global connection
    global cursor
    
    serverId = None
    if hasattr(identifier, "id"):
        serverId = str(identifier.id)
    
    if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
        serverId = str(identifier)

    cursor.execute("SELECT prefixes.prefix FROM prefixes WHERE prefixes.serverId=%s", (serverId,))

    row = cursor.fetchone()

    if row is None:
        cursor.execute("INSERT INTO prefixes VALUES (%s, %s)", (serverId, "?")) # default prefix
        return "?"

    return row[0]
