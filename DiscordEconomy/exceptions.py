class DiscordEconomyException(Exception):
    pass


class NoItemFound(DiscordEconomyException):
    """Raised when trying to remove item from user, when user doesn't have certain item"""


class ItemAlreadyExists(DiscordEconomyException):
    """Raised when trying to add item to user, when user already have this item"""
