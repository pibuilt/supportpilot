import hashlib


def generate_fake_embedding(text: str, dimensions: int = 768) -> list[float]:
    seed = hashlib.sha256(text.encode()).digest()

    values = []
    for i in range(dimensions):
        byte = seed[i % len(seed)]
        values.append((byte / 255.0) * 2 - 1)

    return values