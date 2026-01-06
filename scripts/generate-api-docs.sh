#!/bin/bash
# Generate static Redoc API documentation from OpenAPI specs
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$ROOT_DIR/docs/api"

mkdir -p "$OUTPUT_DIR/specs"

echo "Exporting OpenAPI specs..."

# Export specs from each service
PYTHONPATH="$ROOT_DIR/services/orchestrator" uv run python -c \
  "from src.main import app; import json; print(json.dumps(app.openapi(), indent=2))" \
  > "$OUTPUT_DIR/specs/orchestrator.json"

PYTHONPATH="$ROOT_DIR/services/agent-hub" uv run python -c \
  "from src.main import app; import json; print(json.dumps(app.openapi(), indent=2))" \
  > "$OUTPUT_DIR/specs/agent-hub.json"

for agent in baron duc marie; do
  PYTHONPATH="$ROOT_DIR/services/agents/$agent" uv run python -c \
    "from src.main import app; import json; print(json.dumps(app.openapi(), indent=2))" \
    > "$OUTPUT_DIR/specs/$agent.json"
done

echo "Generating Redoc HTML..."

# Generate static HTML for each spec
redocly build-docs "$OUTPUT_DIR/specs/orchestrator.json" -o "$OUTPUT_DIR/orchestrator.html" --title "Orchestrator API"
redocly build-docs "$OUTPUT_DIR/specs/agent-hub.json" -o "$OUTPUT_DIR/agent-hub.html" --title "Agent Hub API"
redocly build-docs "$OUTPUT_DIR/specs/baron.json" -o "$OUTPUT_DIR/baron.html" --title "Baron API"
redocly build-docs "$OUTPUT_DIR/specs/duc.json" -o "$OUTPUT_DIR/duc.html" --title "Duc API"
redocly build-docs "$OUTPUT_DIR/specs/marie.json" -o "$OUTPUT_DIR/marie.html" --title "Marie API"

# Note: index.html is not generated - MkDocs provides the index via index.md

echo "Done! API docs generated in $OUTPUT_DIR"
echo "Run 'uv run mkdocs serve' to view"
