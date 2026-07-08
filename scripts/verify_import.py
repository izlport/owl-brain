"""Verify imported data in the database."""

from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql+psycopg://owl:owl_password@postgres:5432/owl_brain"
)

with engine.connect() as conn:
    # Check source
    result = conn.execute(text("SELECT id, source_type, name FROM knowledge_source"))
    sources = result.all()
    print(f"Sources ({len(sources)}):")
    for s in sources:
        print(f"  - {s.id}: {s.source_type} - {s.name}")

    # Check conversations
    result = conn.execute(
        text(
            "SELECT c.id, c.title, c.source_id, "
            "(SELECT COUNT(*) FROM message m WHERE m.conversation_id = c.id) AS msg_count "
            "FROM conversation c ORDER BY c.created_at"
        )
    )
    convs = result.all()
    print(f"\nConversations ({len(convs)}):")
    for c in convs:
        print(f"  - {c.id}: '{c.title}' ({c.msg_count} messages)")

    # Check messages
    result = conn.execute(
        text(
            "SELECT m.id, m.role, LEFT(m.content, 50) AS content_preview, "
            "m.sequence, m.conversation_id "
            "FROM message m ORDER BY m.conversation_id, m.sequence"
        )
    )
    msgs = result.all()
    print(f"\nMessages ({len(msgs)}):")
    for m in msgs:
        print(f"  - [{m.sequence}] {m.role}: {m.content_preview}...")

print("\nVerification complete!")
