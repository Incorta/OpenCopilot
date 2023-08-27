from abc import ABC


class LLMConfigurations(ABC):
    @classmethod
    def get_configurations(cls):
        # Any subclass derived from LLMConfigurations must implement it
        pass

    @classmethod
    def register_callback(cls, cb):
        global callback
        callback = cb

    @classmethod
    def execute_callback(cls):
        if callback is not None:
            return callback()
        else:
            raise NotImplementedError("Callback is not registered!")
