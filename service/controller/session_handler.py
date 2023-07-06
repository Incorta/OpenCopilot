import copy
import sdk.configs.constants as constants
from sdk.utils import logger

sessions = {}


def get_or_create_session(chat_id):
    if chat_id is None:
        return None

    if chat_id not in sessions:
        sessions[chat_id] = Session()
    return sessions[chat_id]


class Session:
    def __init__(self):
        self.queries_list = []

    def update_session(self, query):
        if query.get_tasks:
            self.queries_list.append(copy.deepcopy(query))

    def get_queries_list(self):
        return self.queries_list

    class Query:
        _tasks = []
        _store = ""  # To be changed
        _user_query_msg = ""
        _cached_agent_communications = {}
        _pending_agent_communications = {}

        def __init__(self):
            self._tasks = []
            self._store = ""  # To be changed
            self._user_query_msg = ""
            self._cached_agent_communications = {}
            self._pending_agent_communications = {}

        def set_user_query_msg(self, user_query_msg):
            self._user_query_msg = user_query_msg

        def get_user_query_msg(self):
            return self._user_query_msg

        def set_store(self, store):
            self._store = store

        def set_tasks(self, tasks):
            self._tasks = tasks

        def get_tasks(self):
            return self._tasks

        # For getting from cached sessions store purpose
        def set_cached_agent_communications(self, cached_query_object):
            self._cached_agent_communications = cached_query_object

        def get_cached_agent_communications(self, component, sub_component):
            if not self._cached_agent_communications:
                return None
            if component == constants.session_query_user_query_msg:
                cached_result = self._cached_agent_communications[constants.session_query_user_query_msg]
            elif component == constants.session_query_leve0_plan:
                cached_result = self._cached_agent_communications[constants.session_query_leve0_plan][sub_component]
            elif component < len(self._cached_agent_communications[constants.session_query_operators]):
                cached_result = self._cached_agent_communications[constants.session_query_operators][component][sub_component]
            else:
                logger.predefined_message(f"Can't find cached operator of index: {component} of {sub_component} for query: '{self._user_query_msg}'")
                return None

            if cached_result:
                logger.predefined_message(f"Using cached component of index: {component} {sub_component} for query: '{self._user_query_msg}'")
                return cached_result

            logger.predefined_message(f"No cached result found for component of index: {component} {sub_component} for query: '{self._user_query_msg}'")
            return None

        def get_operator_from_task_index(self, task_index):
            if self._cached_agent_communications:
                try:
                    return self._cached_agent_communications[constants.session_query_leve0_plan][constants.Response][constants.Tasks][task_index][constants.Operator]
                except Exception as e:
                    print(e)
                    return None
            return None

        # ----------------------------------------------------------------------------------------------------------------------------------------

        # For setting to sessions store purpose
        def set_pending_agent_communications(self, component, sub_component, value):
            if component == constants.session_query_user_query_msg:
                self._pending_agent_communications[component] = value

            elif component == constants.session_query_leve0_plan:
                if component not in self._pending_agent_communications:
                    self._pending_agent_communications[constants.session_query_leve0_plan] = {}
                if sub_component == constants.Request:
                    self._pending_agent_communications[constants.session_query_leve0_plan][constants.Request] = value
                    self._pending_agent_communications[constants.session_query_leve0_plan][constants.RequestText] = format_request_object(value)
                elif sub_component == constants.Response:
                    self._pending_agent_communications[constants.session_query_leve0_plan][constants.Response] = copy.deepcopy(value)

            else:
                # Checks if the key "operators" exists in the dictionary.
                # If not, it adds an empty list of size equal to tasks count
                if constants.session_query_operators not in self._pending_agent_communications:
                    operators_list_size = len(self._pending_agent_communications[constants.session_query_leve0_plan][constants.Response][constants.Tasks])
                    self._pending_agent_communications[constants.session_query_operators] = [{} for _ in range(operators_list_size)]

                if sub_component == constants.Request:
                    self._pending_agent_communications[constants.session_query_operators][component][constants.Request] = value
                    self._pending_agent_communications[constants.session_query_operators][component][constants.RequestText] = format_request_object(value)

                elif sub_component == constants.Command:
                    self._pending_agent_communications[constants.session_query_operators][component][constants.Command] = value

                elif sub_component == constants.Result or sub_component == constants.EnhancedResult:
                    self._pending_agent_communications[constants.session_query_operators][component][sub_component] = copy.deepcopy(value)

        def get_pending_agent_communications(self):
            return self._pending_agent_communications

        def get_modified_pending_agent_communications(self):
            modified_pending_agent_communications = copy.deepcopy(self._pending_agent_communications)
            for task in modified_pending_agent_communications[constants.session_query_leve0_plan][constants.Response][constants.Tasks]:
                task[constants.Status] = constants.TODO
                task[constants.Result] = ""
            return modified_pending_agent_communications


def format_request_object(request):
    formatted_request = ""
    for message in request:
        role = message['role']
        content = message['content']
        formatted_request += f"{role}: {content}"
    return formatted_request
