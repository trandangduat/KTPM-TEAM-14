class DomainException(Exception):
    pass


class NotFoundException(DomainException):
    pass


class ValidationException(DomainException):
    pass


class OutOfStockException(DomainException):
    pass


class UnauthorizedException(DomainException):
    pass


class ForbiddenException(DomainException):
    pass
