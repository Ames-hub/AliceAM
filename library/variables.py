import logging, datetime
datenow = datetime.datetime.now().strftime("%Y-%m-%d %I%p")
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
    "debugslur9291293949390213924382398283754675986238645789236458723",
    "nigger",
    "nigga",
    "negro",
    "fag",
    "faggot",
    "tranny",
    "Baiano",
]

swears = [
    "shit",
    "fuck",
    "cunt",
    "cunny",
    "pussy",
    "vagina",
    "slut",
    "asshole",
    "bitch",
    "dick",
    "crap",
    "piss",
    "wang",
    "tits",
    "rape",
    "cock",
    "horny",
    "cum",
    "sperm",
    "wank",
    "masturbate",
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