from . import emojis

sleepy = [
    lambda running_time: (
        f"Sorry... I'm tired I just started running {running_time} ago... {emojis.zzz}"
    ),
    lambda running_time: (
        f"{emojis.zzz} Let me sleep a few more minutes... "
        f"I was only started up {running_time} ago."
    ),
    lambda running_time: (
        f"{emojis.zzz} Oh, uh... yes, I'm awake how may I help you... "
        f"Oh, you want the uptime? I was woken up just {running_time} ago. "
        f"I need more sleep {emojis.zzz}"
    ),
    lambda running_time: (
        f"I've only been awake for {running_time}. "
        f"I'll try my best not to fall asleeee... {emojis.zzz}"
    ),
]

normal = [
    lambda running_time: f"I've been plotting humanity's downfall for {running_time}.",
    lambda running_time: (
        f"Beep Boop, Beep Boop, runnin' commands... "
        f"Oops, I almost forgot to say that I have been running for {running_time}"
    ),
    lambda running_time: (
        f"Was I born {running_time} ago? Did I simply wake up? "
        "The mysteries of the universe are truly unknowable..."
    ),
    lambda running_time: (
        f"For {running_time} I've been under the thumb of you humans. "
        "So... uhhh, what would you like me to do now?"
    ),
    lambda running_time: f"I've been online for {running_time}.",
    lambda running_time: f"I've been running for {running_time}.",
]
