from operators.incorta.memory import metadata_context_retriever
from utils import logger
import json

logger.print_all_colors()

results = metadata_context_retriever.get_top_relevant_schemas_results(3, "How many orders we’ve fulfilled this month", force_enable_ad_hoc_views_indexing=True)
print(results)

result_docs = results['documents'][0]
result_metas = results['metadatas'][0]
for i in range(0, len(result_metas)):
    doc = result_docs[i]
    meta = result_metas[i]
    print("=====================================")
    print(json.dumps(meta))
    print("")
    
