class DiscordEconomyException(Exception):
    pass


class NoItemFound(DiscordEconomyException):
    pass


class ItemAlreadyExists(DiscordEconomyException):
    pass
