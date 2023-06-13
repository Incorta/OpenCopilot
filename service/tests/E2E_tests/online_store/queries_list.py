from handlers.predefined_query_handler import UserQuery

sessions_user_queries_messages = [
    [UserQuery("Draw a chart showing categories that are the highest selling in 2013?", {
        "level0_plan": {
            "response": {
                "tasks": [
                    {
                        "id": 1,
                        "name": "Find Business View",
                        "goal_and_purpose": "Find the most relevant Business View to query",
                        "operator": "BusinessViewFinderOp",
                        "status": "TODO",
                        "depends_on_output_of": [
                        ],
                        "detailed_purpose": "Find a Business View containing sales data categorized by date and product category",
                        "result": ""
                    },
                    {
                        "id": 2,
                        "name": "Execute Sales Query",
                        "goal_and_purpose": "Query highest selling categories in 2013",
                        "operator": "QueryOp",
                        "status": "TODO",
                        "depends_on_output_of": [
                            1
                        ],
                        "detailed_purpose": "SELECT category, SUM(sales) as total_sales FROM {business_view} WHERE YEAR(date) = 2013 GROUP BY category ORDER BY total_sales DESC",
                        "result": ""
                    },
                    {
                        "id": 3,
                        "name": "Draw Sales Chart",
                        "goal_and_purpose": "Create a chart displaying highest selling categories in 2013",
                        "operator": "UiChartOp",
                        "status": "TODO",
                        "depends_on_output_of": [
                            2
                        ],
                        "detailed_purpose": "Create a bar chart with categories on the x-axis and total sales on the y-axis",
                        "result": ""
                    }
                ]
            }
        },
        "operators": [
            {
                "command": {
                    "command_name": "GetRelevantView",
                    "args": {
                        "query": "sales data categorized by date and product category",
                        "require_result_summary": False
                    }
                },
                "result": [
                    {
                        "id": 184,
                        "schema_name": "Online_Store",
                        "view_name": "MonthlyRevenueSummary",
                        "view_columns": "[{\"name\": \"YearMonth\", \"label\": \"Year Month\", \"description\": \"\"}, {\"name\": \"Year\", \"label\": \"Year\", \"description\": \"\"}, "
                                        "{\"name\": \"Month\", \"label\": \"Month\", \"description\": \"\"}, {\"name\": \"State\", \"label\": \"State\", \"description\": \"\"}, "
                                        "{\"name\": \"Category\", \"label\": \"Category\", \"description\": \"\"}, {\"name\": \"Subcategory\", \"label\": \"Subcategory\", \"description\": \"\"}, "
                                        "{\"name\": \"Product\", \"label\": \"Product\", \"description\": \"\"}, {\"name\": \"Style\", \"label\": \"Style\", \"description\": \"\"}, "
                                        "{\"name\": \"Revenue\", \"label\": \"Revenue\", \"description\": \"\"}, {\"name\": \"Cost\", \"label\": \"Cost\", \"description\": \"\"}, "
                                        "{\"name\": \"Profit\", \"label\": \"Profit\", \"description\": \"\"}, {\"name\": \"Margin\", \"label\": \"Margin\", \"description\": \"\"}] "
                    }
                ]
            },
            {
                "command": {
                    "command_name": "getQuery",
                    "args": {
                        "query": "SELECT category, SUM(Revenue) as total_sales FROM MonthlyRevenueSummary WHERE Year = 2013 GROUP BY category ORDER BY total_sales DESC LIMIT 10;",
                        "require_result_summary": False
                    }
                },
                "result": [
                    [
                        "Bikes",
                        2302573934.425301
                    ],
                    [
                        "Components",
                        297775646.7732075
                    ],
                    [
                        "Clothing",
                        51688307.487912625
                    ],
                    [
                        "Accessories",
                        30671871.48540077
                    ]
                ]
            },
            {
                "command": {},
                "result": ""
            }

        ]
    })],
    [UserQuery("Draw a chart showing categories that are the highest selling in 2013?", {})],
    [UserQuery("Are there tables describing sales data? Tell me exactly why you think it is related to sales data and the relevant columns", {})],
    [UserQuery("Do we have total sales for Accessories", {})],
    [UserQuery("Show me a 3d chart containing categories, number of items sold and revenue, then explain the chart in text in details", {})],
    [UserQuery("Write the SQL required to show categories that are the highest selling in 2013? Do not execute the query, just generate it and send it to me", {})],
    [UserQuery("What data quality rules can I apply to sales data? Analyze a sample from the data first then propose a list of data quality rules accordingly. Explain the reason behind each rule "
               "and describe the rule in SQL", {})],
    [UserQuery("what is your name", {})],
    [UserQuery("how can you assist me", {})]
]
