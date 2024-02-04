class UnknownCommandError(Exception):
    pass


class APIFailureException(Exception):
    pass


class IllegalArgumentException(Exception):
    pass


class UnauthorizedUserException(Exception):
    pass


class UnsupportedAIProviderException(Exception):
    pass


class NotFoundInCacheException(Exception):
    pass
