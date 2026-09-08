class AppError(Exception):
    """Exception nghiệp vụ, được convert thành ErrorResponse chuẩn ở exception handler."""

    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, code: str, message: str):
        super().__init__(code=code, message=message, status_code=404)


class UnauthorizedError(AppError):
    def __init__(self, code: str = "UNAUTHORIZED", message: str = "Unauthorized"):
        super().__init__(code=code, message=message, status_code=401)


class ForbiddenError(AppError):
    def __init__(self, code: str = "FORBIDDEN", message: str = "Forbidden"):
        super().__init__(code=code, message=message, status_code=403)


class ConflictError(AppError):
    def __init__(self, code: str, message: str):
        super().__init__(code=code, message=message, status_code=409)
