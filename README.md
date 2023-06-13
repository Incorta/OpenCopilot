
To get started:
* `cd service && pip3 install -r requirements.txt`

To run it:
* `cd service && python3 -m uvicorn main:app --reload`
* Check tests.E2E_tests.scenarios folder for full samples with expected prompts from GPT-4

To run test web chatbot:
* `cd chat-fe`
* `npm install --legacy-peer-deps`
* `npm start`

To build meta database:
* `cd service && python3 test_schemas.py`

To run in Testing mode
* Set the sessions queries in tests.E2E_tests.scenarios/USED_INCORTA_ENV/queries_list.py
* `cd service && python3 main_testing.py`

