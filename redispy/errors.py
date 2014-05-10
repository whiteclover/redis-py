#!/usr/bin/env python


class RedisError(Exception):
    pass


class AuthenticationError(RedisError):
    pass


class CommandError(RedisError):
    pass


class ProtocolError(RedisError):
    pass


class ServerError(RedisError):
    pass


class CannotConnectError(RedisError):
    pass


class ConnectionError(ServerError):
    pass


class TimeoutError(ServerError):
    pass


class ResponseError(RedisError):
    pass
