export OPENAI_GPT35_API_KEY="YOUR_KEY"
export PYTHONPATH=$PYTHONPATH:$(pwd)

export OPERATORS_GROUPS=service.operators.postgres

uvicorn main:app --reload