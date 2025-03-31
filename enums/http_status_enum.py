from enum import Enum


class HttpStatusEnum(Enum):
    CONTINUE = 100
    SWITCHING_PROTOCOLS = 101
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    MOVED_PERMANENTLY = 301
    FOUND = 302
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501

    @classmethod
    def get(cls, key):
        """Usage example
        status_code = HttpStatusEnum.get('OK')
        print(status_code)  # Output: 200
        """
        return cls[key].value
