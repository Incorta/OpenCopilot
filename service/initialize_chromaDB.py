from operators.postgres.memory import metadata_context_retriever
from utils import logger

logger.print_all_colors()

results = metadata_context_retriever.get_top_relevant_tables(1, "list all the column you have under each table name")
