export OPENAI_API_KEY=""
export PYTHONPATH=$PYTHONPATH:$(pwd)

export OPERATORS_GROUPS=service.operators.postgres

cd service
python3.9 -m uvicorn main:app --reload