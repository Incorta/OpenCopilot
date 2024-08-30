import time
from typing import Any, List, Optional, Dict, Text

from langchain_community.adapters.openai import (
    convert_message_to_dict,
)

from langchain_core.callbacks import (
    CallbackManagerForLLMRun,
)
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    BaseMessage,
)
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.messages import AIMessage, SystemMessage

from aixplain.factories import ModelFactory
from aixplain.enums import Function


class AixplainChatModel(BaseChatModel):
    """A aiXplain chat model.

    Example:

        .. code-block:: python

            model = AixplainChatModel(model_id="6414bd3cd09663e9225130e8")
            result = model.invoke([HumanMessage(content="hello")])
            result = model.batch([[HumanMessage(content="hello")],
                                 [HumanMessage(content="world")]])
    """

    model_id: str
    """The model id from aiXplain"""

    temperature: float = 0
    """The temperature to use for the model"""

    top_p: float = 0.9999
    """The top_p to use for the model"""

    max_tokens: int = 1024
    """The maximum number of tokens to generate"""

    def __run_aixplain_llm(self, data: Text, context: Optional[Text] = None,
                           history: Optional[List[Dict]] = None):
        """Run the aiXplain language model with the given turns and tools.

        Args:
            data (Union[Text, Dict]): Text to LLM or last user utterance of a conversation.
            context (Optional[Text], optional): System message. Defaults to None.
            history (Optional[List[Dict]], optional): Conversation history in OpenAI format ([{ "role": "assistant", "content": "Hello, world!"}]). Defaults to None.

        Returns:
            dict: The response from the aiXplain language model.
        """
        start = time.time()
        llm = ModelFactory.get(self.model_id)
        assert llm.function == Function.TEXT_GENERATION, "Please select a text generation model."
        response = llm.run(data={"data": data}, history=history, context=context, temperature=self.temperature, top_p=self.top_p, max_tokens=self.max_tokens)
        if response["status"] != "SUCCESS":
            response["data"] = "Sorry, I am not able to generate a response at the moment. Please try again later."
        if "runTime" not in response:
            end = time.time()
            response["runTime"] = end - start
        return response

    def _generate(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> ChatResult:
        """Override the _generate method to implement the chat model logic.

        This can be a call to an API, a call to a local model, or any other
        implementation that generates a response to the input prompt.

        Args:
            messages: the prompt composed of a list of messages.
            stop: a list of strings on which the model should stop generating.
                  If generation stops due to a stop token, the stop token itself
                  SHOULD BE INCLUDED as part of the output. This is not enforced
                  across models right now, but it's a good practice to follow since
                  it makes it much easier to parse the output of the model
                  downstream and understand why generation stopped.
            run_manager: A run manager with callbacks for the LLM.
        """
        assert len(messages) > 0, "You must provide at least one message."
        context = None
        history = []
        for idx in range(len(messages) - 1):
            message = messages[idx]
            if type(message) is SystemMessage:
                context = message.content
            else:
                history.append(message)
        data = messages[-1].content
        history = [convert_message_to_dict(m) for m in history]
        history = history if len(history) > 0 else None
        # print(f"Context: {context}")
        # print(f"History: {history}")
        # print(f"Data: {data}")
        model_response = self.__run_aixplain_llm(data=data, context=context,
                                                 history=history, **kwargs)
        # print(f"Model response: {model_response}")
        tokens = model_response['data']

        message = AIMessage(
            content=tokens,
            additional_kwargs={},  # Used to add additional payload (e.g., function calling request)
            response_metadata={}  # Use for response metadata
        )
        ##

        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model."""
        return "aiXplain-chat-model"