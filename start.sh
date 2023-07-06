if [ -z "$OPENAI_API_KEY" ]; then
  echo "OPENAI_API_KEY is not set or is an empty string"
  exit 1
fi
export PYTHONPATH=$PYTHONPATH:$(pwd)

export OPERATORS_GROUPS=service.operators.postgres

cd service
python3.9 -m uvicorn main:app --host 0.0.0.0 --reload