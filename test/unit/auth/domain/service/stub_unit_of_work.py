class StubUnitOfWork:
    def __init__(self): 
        self.fue_llamado = False

    def __enter__(self):
        self.fue_llamado = True
        return self


    def __exit__(self, exc_type, exc, tb):
        return False