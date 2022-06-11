from warnings import warn

__all__ = ["Economy"]


class Economy:
    def __init__(self, *_, **__):
        """
        Deprecated
        """

        warn("This class is deprecated, use 'from DiscordEconomy.Sqlite import Economy' instead!", DeprecationWarning,
             stacklevel=2)
