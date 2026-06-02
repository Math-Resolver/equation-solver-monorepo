async def create_indexes(collection) -> None:
    await collection.create_index(
        [("username", 1), ("equation", 1), ("createdAt", 1)],
        unique=True,
    )