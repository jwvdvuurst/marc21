class MarcException(Exception):
    """
    The MarcException class is a custom exception class that is used to raise exceptions specific to the MARC (Machine-Readable Cataloging) data format.
    """
    reason: str

    def __init__(self, reason: str):
        if reason == '':
            self.reason = 'Unknown reason'
        else:
            self.reason = reason

    def __repr__(self):
        return "MarcException: %s" % self.reason

class MarcInvalidTagException(MarcException):
    """
    The MarcInvalidTagException class is a custom exception class that is used to raise exceptions specific to the MARC (Machine-Readable Cataloging) data format.
    """
    tag: str

    def __init__(self, tag: str, extra_reason: str):
        self.tag = tag
        super().__init__('Tag %s is not defined in the dictionary%s.' % (tag, ' %s' % extra_reason if extra_reason else ''))

class MarcInvalidSubfieldException(MarcException):
    """
    The MarcInvalidTagException class is a custom exception class that is used to raise exceptions specific to the MARC (Machine-Readable Cataloging) data format.
    """
    tag: str
    subfield: str

    def __init__(self, subfield: str, tag: str, extra_reason: str):
        self.tag = tag
        self.subfield = subfield
        super().__init__('Subfield %s is not defined for tag %s in the dictionary%s.' % (subfield, tag, ' %s' % extra_reason if extra_reason else ''))

class MarcSubfieldNotRepeatableException(MarcException):
    tag: str
    subfield: str

    def __init__(self, subfield: str, tag: str, extra_reason: str):
        self.tag = tag
        self.subfield = subfield
        super().__init__('Subfield %s is not repeatable for tag %s%s.' % (subfield, tag, ' %s' % extra_reason if extra_reason else ''))

class MarcSubfieldException(MarcException):
    tag: str
    subfield: str
    value: str

    def __init__(self, tag: str, subfield: str, value: str, reason: str):
        self.tag = tag
        self.subfield = subfield
        self.value = value

        if subfield == '' and value == '':
            message='Insufficient data to create subfield'
        else:
            message='Subfield without '
            if subfield == '':
                message = message + 'tag '
            else:
                message = message + 'value '

        if tag != '':
            message = message + 'for tag %s' % tag

        if reason != '':
            message = message + ': %s' % reason

        super().__init__(message)

class MarcUnknownFieldTypeException(MarcException):
    def __init__(self, tag: str, type: str, reason: str):
        super().__init__('Field \'%s\' has an unknown type \'%s\' %s' % (tag, type, reason))

class MarcFieldTypeException(Exception):
    """Exception raised for invalid MARC field types."""
    pass