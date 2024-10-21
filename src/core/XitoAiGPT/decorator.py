
def single_create(cls):
    """單例創建"""
    _instance:dict = {}
    def warpper(*args, **kwargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)

        return _instance[cls]

    return warpper
