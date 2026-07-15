"""Prompt templates for knowledge extraction."""

KNOWLEDGE_EXTRACTION_PROMPT = """You are a knowledge extraction assistant. Your task is to analyze a conversation and extract structured knowledge from it.

Analyze the following chat conversation and extract the key knowledge point. Focus on the informational content — what the user asked and what the assistant taught.

Respond ONLY with a valid JSON object (no markdown fences, no additional text) in this exact format:
{{
  "title": "A concise, descriptive title for this knowledge (max 80 chars)",
  "category": "A single category label, e.g., Python, PostgreSQL, Design, DevOps",
  "summary": "A 1-2 sentence summary of the key takeaway",
  "content": "A comprehensive explanation of the knowledge, written as a standalone tutorial-like text that someone could read without seeing the original conversation. Include code examples if applicable.",
  "tags": ["tag1", "tag2", "tag3"]
}}

Guidelines:
- title: Should be specific and descriptive, like "Python Async/Await Best Practices"
- category: Use single broad category
- summary: Capture the essence in 1-2 sentences
- content: Write 2-5 paragraphs that fully explain the concept. Do NOT reference the conversation format (do not say "the user asked" or "the assistant replied").
- tags: 2-5 relevant tags, lowercased

Here is the conversation:

{chat_text}
"""

__all__ = [
    "KNOWLEDGE_EXTRACTION_PROMPT",
]
