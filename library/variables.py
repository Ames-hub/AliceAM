import logging, datetime, os

os.makedirs('logs', exist_ok=True)

datenow = datetime.datetime.now().strftime("%Y-%m-%d")
logging.basicConfig(
    level=logging.INFO,
    filename=f"logs/{datenow}.log",
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logging.basicConfig(
    level=logging.ERROR,
    filename=f"logs/{datenow}.log",
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

slurs = [
    "debugslur9291293949390213924",
    "nigger",
    "nigga",
    "negro",
    "fag",
    "faggot",
]

swears = [
    "shit",
    "fuck",
    "fucking",
    "cunt",
    "cunny",
    "slut",
    "asshole",
    "bitch",
    "dick",
    "crap",
    "piss",
    "tits",
    "boobs",
    "rape",
    "cock",
    "horny",
    "cum",
    "wank",
]

domain_endings = [
    ".com",
    ".net",
    ".org",
    ".edu",
    ".uk",
    ".au",
    ".ca",
    ".cn",
    ".de",
    ".info",
    ".biz",
    ".me",
    ".tv",
    ".xyz",
    ".club",
    ".pro",
    ".name",
    ".mobi",
    ".cc",
    ".ws",
    ".travel",
    ".io",
    ".tk",
    ".gq",
    ".ml"
]
