def paginate(items, page: int = 1, size: int = 50):
    start = (page-1) * size
    end = start + size
    return items[start:end]
