SQL string
↓
Parser → tokenizes SQL into AST (Abstract Syntax Tree)
↓
Analyzer → validates table/column names exist
↓
Planner → figures out the cheapest execution plan
↓
Executor → actually runs the plan, reads pages, applies filters
↓
Result
