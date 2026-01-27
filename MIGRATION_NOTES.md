# Model Architecture Migration Notes

## Overview
Migrated from generic model naming (CHAT_MODEL/MINI_MODEL) to purpose-based naming (WRITING_MODEL/DEDUCE_MODEL) to better reflect the functional responsibilities of each model.

## Changes Summary

### Environment Variables
**Old:**
- `CHAT_MODEL_NAME` / `CHAT_MODEL_TEMPERATURE`
- `MINI_MODEL_NAME` / `MINI_MODEL_TEMPERATURE`

**New:**
- `WRITING_MODEL_NAME` / `WRITING_MODEL_TEMPERATURE` - for text generation, summarization, report writing
- `DEDUCE_MODEL_NAME` / `DEDUCE_MODEL_TEMPERATURE` - for reasoning, judgment, math understanding

### Default Model Values
- `WRITING_MODEL_NAME`: `gpt-4o` (temperature: 0.2)
- `DEDUCE_MODEL_NAME`: `o3-mini` (temperature: 0)

### Function Names
**Old:**
- `get_write_model()` / `get_llm_model()`

**New:**
- `get_writing_model()` - returns writing model instance
- `get_deduce_model()` - returns deduce model instance

### Model Usage by Node

#### Agent Graph Nodes (server/chatbox/chat_agents/nodes.py)

| Node | Model Used | Reason |
|------|------------|--------|
| `route_question` | **deduce_model** | Logical judgment: route to vectorstore or web search |
| `grade_documents` | **deduce_model** | Reasoning: assess document relevance to question |
| `transform_question` | **deduce_model** | Math reasoning: align query with paper terminology (HyDE) |
| `summarize_conversation` | **writing_model** | Text generation: create conversation summary |
| `generate` | **writing_model** | Text generation: produce final answer with LaTeX formatting |

#### Report Pipeline (server/report_pipeline/weekly_report_agent.py)

| Function | Model Used | Reason |
|----------|------------|--------|
| `generate_ai_summary` | **writing_model** | Generate paper summaries |
| `generate_report` | **writing_model** | Create weekly report synthesis |

## Files Modified

1. `.env` - Updated environment variable names and added comments
2. `.env.example` - Updated environment variable names and added comments
3. `server/config.py` - Renamed model configuration and getter functions
4. `server/chatbox/core/config.py` - Renamed model configuration and getter functions
5. `server/chatbox/chat_agents/nodes.py` - Updated imports and model usage in all nodes
6. `server/chatbox/chat_agents/graph.py` - Removed unused import
7. `server/report_pipeline/weekly_report_agent.py` - Updated function calls
8. `server/tests/test_persistence.py` - Removed unused import
9. `CONFIG_GUIDE.md` - Updated documentation

## Migration Checklist

If you have an existing `.env` file:
- [ ] Rename `CHAT_MODEL_NAME` to `WRITING_MODEL_NAME`
- [ ] Rename `CHAT_MODEL_TEMPERATURE` to `WRITING_MODEL_TEMPERATURE`
- [ ] Rename `MINI_MODEL_NAME` to `DEDUCE_MODEL_NAME`
- [ ] Rename `MINI_MODEL_TEMPERATURE` to `DEDUCE_MODEL_TEMPERATURE`
- [ ] Update model values if desired (e.g., `DEDUCE_MODEL_NAME=o3-mini`)

## Architecture Benefits

1. **Clear Separation of Concerns**: Each model is optimized for its specific task type
2. **Better Cost Management**: Use powerful reasoning model (o3-mini) only where needed
3. **Improved Performance**: Writing tasks benefit from gpt-4o's superior language generation
4. **Self-Documenting Code**: Function and variable names clearly indicate purpose

## Recommended Configuration

```env
# Writing model - for text generation, summarization, report writing
WRITING_MODEL_NAME=gpt-4o
WRITING_MODEL_TEMPERATURE=0.2

# Deduce model - for reasoning, judgment, math understanding
DEDUCE_MODEL_NAME=o3-mini
DEDUCE_MODEL_TEMPERATURE=0
```

This configuration leverages:
- **o3-mini's strengths**: Mathematical reasoning, logical judgment, semantic understanding
- **gpt-4o's strengths**: Fluent text generation, LaTeX formatting, clear explanations
