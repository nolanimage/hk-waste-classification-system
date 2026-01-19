# How RAG Examples Help VLM/LLM Recognition

## Yes, They Directly Help Recognition!

The items stored in the vector database (ChromaDB) are **actively used** to help the VLM/LLM recognize and classify items. They are NOT just stored for other purposes.

## How It Works: RAG (Retrieval-Augmented Generation)

### Step-by-Step Process

1. **User Input** (text or image)
   ```
   User: "a crumpled aluminum can"
   ```

2. **Generate Embedding**
   - System creates a vector embedding of the input text
   - Uses `sentence-transformers` model locally

3. **Retrieve Similar Examples** (Vector Similarity Search)
   - Queries ChromaDB vector database
   - Finds top-K most similar examples (default: 5)
   - Uses cosine similarity to match embeddings
   ```
   Found similar examples:
   - "Aluminum soda can" (similarity: 0.92)
   - "Metal can (food)" (similarity: 0.85)
   - "Aluminum foil" (similarity: 0.78)
   ```

4. **Include Examples in LLM Prompt**
   - Examples are added to the system prompt
   - LLM sees both:
     - General rules (Hong Kong EPD guidelines)
     - Specific similar examples from database
   
   Example prompt structure:
   ```
   System: "You are a waste classification assistant...
   
   [Hong Kong rules and guidelines...]
   
   Similar examples from our database:
   
   Example 1:
     Item: Aluminum soda can
     Description: a crumpled aluminum soda can
     Category: metal
     Bin: Yellow bin (aluminum/metal cans) (yellow)
     Note: Must be empty and clean. Remove any labels if possible.
   
   Example 2:
     Item: Metal can (food)
     Description: empty metal food can
     Category: metal
     Bin: Yellow bin (aluminum/metal cans) (yellow)
     Note: Must be empty and clean. Rinse if necessary.
   
   Now classify the user's item based on these rules and examples."
   ```

5. **LLM Classification**
   - LLM uses the examples as **context** and **reference**
   - Helps LLM understand:
     - How similar items were classified
     - What bin to use
     - What rules apply
     - Format/structure to follow

## Benefits of Using RAG Examples

### 1. **Context-Aware Classification**
- LLM sees real examples, not just abstract rules
- Better understanding of edge cases
- Consistent formatting

### 2. **Domain-Specific Knowledge**
- Examples are specific to Hong Kong waste management
- Captures local nuances and rules
- Learns from past successful classifications

### 3. **Few-Shot Learning**
- Provides concrete examples in the prompt
- LLM learns patterns from examples
- Better accuracy for similar items

### 4. **Self-Improvement**
- Auto-enrichment adds new high-confidence items
- Database grows over time
- System gets better at recognizing more items

## Code Flow

```python
# 1. Generate embedding for user input
text_embedding = embedding_service.generate_text_embedding("a crumpled aluminum can")

# 2. Retrieve similar examples from vector DB
similar_examples = rag_service.retrieve_similar(
    text="a crumpled aluminum can",
    text_embedding=text_embedding
)
# Returns: Top 5 most similar examples from database

# 3. Build prompt with examples
prompt = _build_system_prompt(examples=similar_examples)
# Includes: Rules + Similar examples

# 4. Send to LLM with examples in context
classification = await openrouter_service.classify_item(
    text="a crumpled aluminum can",
    examples=similar_examples  # These are included in the prompt!
)
```

## Example: How Examples Help

**Without RAG Examples:**
- LLM only sees general rules
- May not understand specific item variations
- Less consistent formatting
- Lower accuracy for edge cases

**With RAG Examples:**
- LLM sees: "Aluminum soda can" → Yellow bin
- LLM sees: "Metal can (food)" → Yellow bin  
- LLM sees: "Aluminum foil" → Yellow bin (if clean)
- **Result**: LLM correctly classifies "crumpled aluminum can" → Yellow bin
- **Reasoning**: Similar examples show aluminum items go to yellow bin

## Vector Database Purpose

The vector database serves as:
1. **Knowledge Base**: Stores classification examples
2. **Similarity Search**: Finds relevant examples quickly
3. **Context Provider**: Supplies examples to LLM prompts
4. **Learning System**: Grows with auto-enrichment

## Summary

✅ **YES** - Items in vector DB directly help VLM/LLM recognize items
✅ **YES** - They are included in every classification prompt
✅ **YES** - They improve accuracy and consistency
✅ **YES** - They enable few-shot learning
✅ **YES** - They provide domain-specific context

The vector database is the **core intelligence** of the RAG system - it's what makes the LLM smarter about waste classification!
