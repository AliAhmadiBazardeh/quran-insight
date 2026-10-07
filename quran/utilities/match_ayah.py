
from difflib import SequenceMatcher

from quran.helper import normalize_persian_with_mapping, normalize_persian


def find_best_match(
    query: str,
    normalized_text: str,
) -> tuple[int, int] | None:
    """
    Find the best matching region of query inside normalized_text.

    Returns:
        (start_index, end_index)

    or:
        None
    """

    if not query or not normalized_text:
        return None

    query_length = len(query)

    # Try windows around the query length.
    min_window = max(1, query_length - 3)
    max_window = min(
        len(normalized_text),
        query_length + 5,
    )

    best_ratio = 0.0
    best_match = None

    for window_size in range(min_window, max_window + 1):
        for start in range(
            0,
            len(normalized_text) - window_size + 1,
        ):
            end = start + window_size

            candidate = normalized_text[start:end]

            ratio = SequenceMatcher(
                None,
                query,
                candidate,
            ).ratio()

            if ratio > best_ratio:
                best_ratio = ratio
                best_match = (start, end)

    return best_match

def map_match_to_original(
    match: tuple[int, int],
    mapping: list[tuple[int, int]],
) -> tuple[int, int] | None:
    """
    Convert normalized text indexes to original text indexes.
    """

    if not match:
        return None

    start, end = match

    if (
        start < 0
        or end > len(mapping)
        or start >= end
    ):
        return None

    original_start = mapping[start][0]
    original_end = mapping[end - 1][1]

    return original_start, original_end

def build_text_context(
    text: str,
    start: int,
    end: int,
    context_size: int = 30,
) -> tuple[str, int, int]:
    """
    Build a context window around the matched region.

    Returns:
        (context_text, highlight_start, highlight_end)
    """

    context_start = max(
        0,
        start - context_size,
    )

    context_end = min(
        len(text),
        end + context_size,
    )

    context_text = text[
        context_start:context_end
    ]

    highlight_start = start - context_start
    highlight_end = end - context_start

    return (
        context_text,
        highlight_start,
        highlight_end,
    )

def find_match_context(
    query: str,
    original_text: str,
    text_type: str = "ayah",
    context_size: int = 30,
) -> dict | None:
    """
    Find the best matching region in the original text
    and return a context window with highlight offsets.
    """

    normalized_query = normalize_persian(
        text_type,
        query,
    )

    normalized_text, mapping = (
        normalize_persian_with_mapping(
            text_type,
            original_text,
        )
    )

    if not normalized_query or not normalized_text:
        return None

    normalized_match = find_best_match(
        normalized_query,
        normalized_text,
    )

    if not normalized_match:
        return None

    original_match = map_match_to_original(
        normalized_match,
        mapping,
    )

    if not original_match:
        return None

    start, end = original_match

    context_text, highlight_start, highlight_end = (
        build_text_context(
            original_text,
            start,
            end,
            context_size,
        )
    )

    return {
        "text": context_text,
        "highlight_start": highlight_start,
        "highlight_end": highlight_end,
    }