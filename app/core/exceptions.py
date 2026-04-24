class AppError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    pass


class BadRequestError(AppError):
    pass