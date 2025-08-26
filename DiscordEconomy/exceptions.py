class DiscordEconomyException(Exception):
    pass


class NegativeAmountException(DiscordEconomyException):
    """Raised when trying to remove/add negative amount"""


class EnsurePositiveBalanceException(DiscordEconomyException):
    """Raised when trying to set balance to less than 0"""


class NotFoundException(DiscordEconomyException):
    """Raised when trying to remove item from user, when user doesn't have certain item"""


class ItemAlreadyExists(DiscordEconomyException):
    """Raised when trying to add item that user already has"""
