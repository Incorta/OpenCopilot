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


class ProviderNotFoundException(Exception):
    pass

class LLMException(Exception):
    """Base class for exceptions related to LLM operations."""
    pass
    
