def topic_matches(pattern: str, routing_key: str) -> bool:
    """Match RabbitMQ topic words where * is one word and # is zero or more."""
    pattern_words = pattern.split(".")
    key_words = routing_key.split(".")

    def match(pattern_index: int, key_index: int) -> bool:
        if pattern_index == len(pattern_words):
            return key_index == len(key_words)
        word = pattern_words[pattern_index]
        if word == "#":
            return any(
                match(pattern_index + 1, next_key)
                for next_key in range(key_index, len(key_words) + 1)
            )
        if key_index == len(key_words):
            return False
        return (word == "*" or word == key_words[key_index]) and match(
            pattern_index + 1, key_index + 1
        )

    return match(0, 0)