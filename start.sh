export PYTHONPATH=$PYTHONPATH:$(pwd)

export OPERATORS_GROUPS=service.operators.postgres

cd service
python3 -m uvicorn main:app --host 0.0.0.0 --reload
