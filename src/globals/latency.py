from . import emojis

fast_latency = [
    lambda latency: (
        "Pong! "
        f"I hit the ball you sent me all the way back to you in {latency} seconds. "
    )
    + (
        (
            "I guess that means I just broke the world record for fastest table tennis "
            "smash speed!"
        )
        if latency < 0.0876853425
        else "Oh we're not actually playing table tennis are we..."
    ),
    lambda latency: f"Hmm I have a latency of {latency}, "
    + "I'm faster at responding to visual stimuli than humans!"
    if latency < 0.25
    else (
        "I'm slower at responding to visual stimuli than humans... "
        "I shouldn't expect to be able to be good at everything."
    ),
    lambda latency: (
        f"I bet it didn't actually seem like it took me {latency} seconds to respond"
        "because websockets delays may make it longer... but I did!"
    ),
    lambda latency: (
        f"{latency} seconds ago you requested me to send this message,"
        "and here it is now."
    ),
    lambda latency: f"It took me {latency} seconds to respond"
    + ", literally faster than you can blink!"
    if latency < 0.3
    else ".",
]

slow_latency = [
    lambda latency: (
        f"{emojis.cog} I seem to be taking a while—"
        f"{latency} seconds, to be exact to respond, sorry!"
    ),
    lambda latency: f"It's took me {latency} seconds long to respond... sorry!",
    lambda latency: (
        f"I guess I must be popular if it's taking me {latency} seconds to respond."
    ),
    lambda latency: (
        "Calculating latency... one-one-mississippi-thousand, "
        "two-two-mississippi-thousand... Wait I think I lost count. "
        "Oh wait the dev just *gives* it to me. "
        f"Well... *now*, my latency is {latency} seconds {emojis.sweat_smile}... "
        "maybe I shouldn't have counted it out.",
    ),
    lambda latency: (
        f"My latency is {latency} seconds... "
        "Why don't *you* have to say your latency..."
    ),
]
