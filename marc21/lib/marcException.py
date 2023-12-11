class MarcException(Exception):
    """
    The MarcException class is a custom exception class that is used to raise exceptions specific to the MARC (Machine-Readable Cataloging) data format.
    """
    reason: str

    def __init__(self, reason: str):
        if str == '':
            self.reason = 'Unknown reason'
        else:
            self.reason = reason

    def __repr__(self):
        return "MarcException: %s" % self.reason

    def __del__(self):
        del self.reason
