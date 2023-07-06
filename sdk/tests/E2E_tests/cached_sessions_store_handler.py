import json
import os
import sdk.configs.constants as constants
from sdk.configs import env


class CachedSessionsStoreHandler:
    _instance = None
    _sessions_store_filename = f"tests/E2E_tests/{env.operators_group}/sessions_store.json"
    _sessions_dict = {}
    _cached_session_idx = 0

    def __new__(cls):
        """Creates a new instance of the ScenarioPersistorSingleton class if none exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize_cached_sessions_store(self):
        if not os.path.exists(self._sessions_store_filename):
            self.create_new_cached_sessions_store()

        with open(self._sessions_store_filename) as f:
            self._sessions_dict = json.load(f)

    def create_new_cached_sessions_store(self):
        data = {}
        os.makedirs(os.path.dirname(self._sessions_store_filename), exist_ok=True)
        with open(self._sessions_store_filename, 'w') as f:
            json.dump(data, f)

    def validate_session_history_match(self, candidate_session, session, query_idx_match):
        """Validate that the session history up to the matched query is consistent,
        for any non-first matches."""
        queries_list = session.queries_list
        # Iterate through the candidate session entries, up to the query we're checking
        for query_index, query_obj in enumerate(queries_list[:query_idx_match - 1]):
            # For each query, it validates that the user_query_msg matches the corresponding session query_user_msg
            # If any queries do not match, the histories do not match, so it returns False
            if query_obj.get_user_query_msg() != candidate_session[query_index][constants.session_query_user_query_msg]:
                return False
        # If all queries match, the histories match up to that point, so it returns True
        return True

    def get_query_if_exists(self, new_query, query_idx_match, session):
        """Check if a new query matches an existing query in the sessions dictionary,
        and if so, return the corresponding query result."""
        if isinstance(new_query, dict):
            new_query = new_query[constants.session_query_user_query_msg]
        if not self._sessions_dict:
            return None
        for session_name, list_of_queries in self._sessions_dict.items():
            # Check if a new incoming query matches an existing query in the sessions dictionary
            if len(list_of_queries) > query_idx_match and list_of_queries[query_idx_match][constants.session_query_user_query_msg] == new_query:
                # Return the corresponding query result only if the session history also matches, for non-first queries
                if query_idx_match > 0:
                    if self.validate_session_history_match(self._sessions_dict[session_name], session, query_idx_match):
                        self._cached_session_idx = int(session_name)
                        return self._sessions_dict[session_name][query_idx_match]
                    else:
                        # Otherwise, ignore the match and continue
                        continue
                else:
                    self._cached_session_idx = int(session_name)
                    return self._sessions_dict[session_name][query_idx_match]
        self._cached_session_idx = 0
        return None

    def append_or_overwrite_session_to_store(self, session_queries):
        if self._cached_session_idx == 0:
            keys = list(self._sessions_dict.keys())
            if len(keys) > 0:
                last_session_name = keys[-1]
                new_session_name = str(int(last_session_name) + 1)
            else:
                new_session_name = "1"
            self._sessions_dict[new_session_name] = session_queries
        else:  # session exists, either overwrite the existing, or ignore it
            if env.overwrite_if_exists:
                self._sessions_dict[str(self._cached_session_idx)] = session_queries

    def add_session_queries_to_sessions_store(self, new_session_queries):
        """Adds a new query object to a JSON file containing a dictionary of sessions
        and their corresponding list of query objects."""
        self.append_or_overwrite_session_to_store(new_session_queries)
        with open(self._sessions_store_filename, 'w') as f:
            data = json.dumps(self._sessions_dict, indent=2)
            f.write(data)
