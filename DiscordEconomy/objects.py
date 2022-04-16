class UserObject(object):
    """
    User object, returned from a database.
    """

    def __init__(self, bank, wallet, items):
        self.bank = bank
        self.wallet = wallet
        self.items = items

    def __repr__(self):
        return f"User(bank={self.bank}, wallet={self.wallet}, items={self.items})"
