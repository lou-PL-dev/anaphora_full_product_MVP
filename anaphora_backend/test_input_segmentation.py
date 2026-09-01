from app.chains.input_segmentation import (
    MAX_CHUNK_CHARS,
    is_long_input,
    segment_long_input,
)


def _normalise(text: str) -> str:
    return " ".join(text.split())


def test_short_input_is_unchanged():
    text = "I like someone warm, curious, and happy to stay home on a Friday night."
    assert is_long_input(text) is False
    assert segment_long_input(text) == [text]


def test_long_input_is_split_without_losing_content():
    paragraphs = [
        "I care a lot about emotional steadiness. " + ("They should be able to talk through conflict calmly. " * 30),
        "I also love someone with their own world. " + ("They can have hobbies and friendships that are theirs. " * 30),
        "And day to day I am quite home-oriented. " + ("A quiet evening together sounds genuinely good to me. " * 30),
    ]
    text = "\n\n".join(paragraphs)

    chunks = segment_long_input(text)

    assert len(chunks) > 1
    assert all(len(chunk) <= MAX_CHUNK_CHARS for chunk in chunks)
    assert _normalise(" ".join(chunks)) == _normalise(text)


def test_single_extremely_long_span_has_safe_fallback():
    text = "word " * 5000
    chunks = segment_long_input(text)

    assert len(chunks) > 1
    assert all(len(chunk) <= MAX_CHUNK_CHARS for chunk in chunks)
    assert _normalise(" ".join(chunks)) == _normalise(text)


def test_segmentation_does_not_create_conversation_turns():
    # The API intentionally returns plain text chunks only; callers decide how
    # to process them and must still produce one user-visible conversational reply.
    text = ("First thought. Second thought. Third thought. " * 250).strip()
    chunks = segment_long_input(text)

    assert all(isinstance(chunk, str) for chunk in chunks)
    assert not any("role" in chunk for chunk in chunks)
