class ResourceAlreadyExistsError(Exception):
    def __init__(self, message="Resource already exists"):
        self.message = message
        super().__init__(self.message)
