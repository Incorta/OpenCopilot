import logging
from unittest.mock import MagicMock

import pytest
import requests

from operators.incorta.api_helpers.post import run_paginated_get_all


class TestRunPaginatedGetAll:
    @pytest.fixture(autouse=True)
    def custom_logger(self, caplog):
        caplog.set_level(logging.ERROR)
        return caplog

    def test_successful_pagination(self, monkeypatch):
        url = "https://example.com/api"
        token = "fake_token"
        def res_transformer(x):
            return x["results"]

        responses = [
            {"results": list(range(100))},
            {"results": list(range(100, 200))},
            {"results": list(range(200, 250))}
        ]

        mock_post = MagicMock(side_effect=lambda *args, **kwargs: MagicMock(status_code=200, json=lambda: responses.pop(0)))
        monkeypatch.setattr(requests, "post", mock_post)

        result = run_paginated_get_all(url, token, res_transformer)

        assert result == list(range(250))
        assert mock_post.call_count == 3

    def test_unsuccessful_request(self, monkeypatch, custom_logger):
        url = "https://example.com/api"
        token = "fake_token"
        def res_transformer(x):
            return x["results"]

        mock_post = MagicMock(return_value=MagicMock(status_code=400, text="Bad request"))
        monkeypatch.setattr(requests, "post", mock_post)

        result = run_paginated_get_all(url, token, res_transformer)

        assert result == []
        assert mock_post.call_count == 1
        assert len(custom_logger.records) == 1
        assert "Failed to get results from incorta" in custom_logger.records[0].message

    def test_partial_pagination(self, monkeypatch):
        url = "https://example.com/api"
        token = "fake_token"
        def res_transformer(x):
            return x["results"]

        responses = [
            {"results": list(range(100))},
            {"results": list(range(100, 150))}
        ]

        mock_post = MagicMock(side_effect=lambda *args, **kwargs: MagicMock(status_code=200, json=lambda: responses.pop(0)))
        monkeypatch.setattr(requests, "post", mock_post)

        result = run_paginated_get_all(url, token, res_transformer)

        assert result == list(range(150))
        assert mock_post.call_count == 2
