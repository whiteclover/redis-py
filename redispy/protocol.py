#!/usr/bin/env python


class ResponseReaderTrait(object):

    def read(self, connection):
        pass


class ResponseHandleTrait(object):

    def handle(self, connection, payload):
        pass


class AbstractProtocol(ResponseReaderTrait):

    def write(self, connection, command):
        pass

    def set_option(self, option, value):
        pass


class CommandSerializerTrait(object):

    def serialize(self, command):
        pass


class ComposableProtocolTrait(AbstractProtocol):

    def set_serializer(self, serializer):
        pass

    def get_serializer(self):
        pass

    def get_reader(self):
        pass

    def set_reader(self, reader):
        pass


class ComposableTextProtocol(ComposableProtocolTrait):

    def __init__(self, options={}):
        self._serializer = None
        self._reader = None

        self.set_serializer(TextCommandSerializer())
        self.set_reader(TextResponseReader())
        if options:
            self.initialize_options(options)

    def initialize_options(self, options):
        for k, v in options.items():
            self.set_option(k, v)

    def set_option(self, key, value):
        if key == 'iterable_multibulk':
            handler = ResponseMultiBulkStreamHandler(
            ) if value else ResponseMultiBulkHandler()
            return
        raise Exception(
            '"The option $option is not supported by the current protocol"')

    def serialize(self, command):
        self._serializer.serialize(command)

    def write(self, connection, command):
        connection.write_bytes(self.serializer.serialize(command))

    def read(self, connection):
        return self._reader.read(connection)

    def set_serializer(self, serializer):
        self._serializer = serializer

    def get_serializer(self):
        return self._serializer

    def get_reader(self, reader):
        return self._reader

    def set_reader(self, reader):
        self._reader = reader


class ResponseMultiBulkHandler(ResponseHandleTrait):

    def handle(self, connection, data):
        length = int(lengthString)
        if length >= 0:
            return connection.read_bytes(length + 2)[:-2]
        else:
            return ''


class ResponseErrorHandler(ResponseHandleTrait):

    def handle(self, connection, err_msg):
        return ResponseError(err_msg)


class ResponseIntegerHandler(ResponseHandleTrait):

    def handle(self, connection, number):
        if number.isdigit():
            return int(number)

        if number:
            return CommunicationException.handle(ProtocolException(
                connection, "Cannot parse '$number' as numeric response"))

        return None


class ResponseMultiBulkHandler(ResponseHandleTrait):

    def handle(self, connection, data):
        length = len(data)
        l = []
        if length > 0:
            cache = {}
            reader = connection, get_protocol().get_reader()
            for i in range(length):
                header = connection.readline()
                prefix = header[0]
                if cache[prefix]:
                    handler = reader.get_handler()
                else:
                    handler = reader.get_handler(prefix)
                    cache[prefix] = handler
                l.append(handler.handle(connection, header[1:]))
        return l


class ResponseMultiBulkStreamHandler(ResponseHandleTrait):

    def handle(self, connection, data):
        length = len(data)
        return MultiBulkResponseSimple(connection, length)


class ResponseStatusHandler(ResponseHandleTrait):

    def handle(self, connection, status):
        if status == 'OK':
            return True

        if status == 'QUEUED':
            return ResponseQueued()

        return status


class TextCommandSerializer(CommandSerializerTrait):

    def handle(self, command):
        command_id = command.get_id()
        arguments = command.get_arguments()
        cmdlen = len(command_id)
        req_len = len(arguments)

        buffer = str(req_len) + '\n' + str(cmdlen) + '\n' + command_id + '\n'
        i = 0
        while i < req_len:
            argument = arguments[i]
            arglen = len(argument)
            buffer += '$' + str(arglen) + '\n' + argument + '\n'

        return buffer


class TextProtocol(AbstractProtocol):
    NEWLINE = '\r\n'
    OK = 'OK'
    ERROR = 'ERR'
    QUEUED = 'QUEUED'
    NONE = 'None'

    PREFIX_STATUS = '+'
    PREFIX_ERROR = '-'
    PREFIX_INTEGER = ':'
    PREFIX_BULK = '$'
    PREFIX_MULTI_BULK = '*'

    BUFFER_SIZE = 4096

    def __init__(self):
        self._mbiterable = False
        self._serializer = TextCommandSerializer()

    def write(self, connection, command):
        connection.writebytes(self._serializer.serialize(command))

    def read(self, connection):
        chunk = connection.readline()
        prefix = chunk[0]
        payload = chunk[1:]
        if prefix == '+':
            if payload == 'OK':
                return True
            if payload == 'QUEUED':
                return ResponseQueued()
            return payload

        if prefix == '$':
            size = len(payload)
            if size == 0:
                return ''
            return connection.read_bytes(size + 2)[0:-2]

        if prefix == '*':
            length = int(payload)
            if length == -1:
                return ''

            if self._mbiterable:
                return MultiBulkResponseSimple(connection, length)
            multibulk = []
            for i in range(length):
                multibulk.append(self.read(connection))
            return multibulk

        if prefix == ':':
            return int(payload)

        if prefix == '-':
            return ResponseError(payload)

        return CommunicationError.handle(ProtocolError(
            connection, "Unknown prefix: '$prefix'"))

    def set_option(self, key, value):
        if key == 'iterable_multibulk':
            return self._mbiterable(bool(value))


class TextResponseReader(ResponseReaderTrait):

    def __init__(self):
        self._handlers = self.defaulthandlers()

    def default_handlers(self):
        return {
            TextProtocol.PREFIX_STATUS: ResponseStatusHandler(),
            TextProtocol.PREFIX_ERROR: ResponseErrorHandler(),
            TextProtocol.PREFIX_INTEGER: ResponseIntegerHandler(),
            TextProtocol.PREFIX_BULK: ResponseBulkHandler(),
            TextProtocol.PREFIX_MULTI_BULK: ResponseMultiBulkHandler()
        }

    def get_handler(self, prefix):
        return self._handlers.get(prefix)

    def set_handler(self, prefix, handler):
        self._handlers[prefix] = handler

    def read(self, connection):
        line = connection.readline()
        if line == '':
            self.protocol_error(connection, 'Unexpected empty line')
        prefix = line[0]
        if not self._handlers.get(prefix):
            self.protocol_error(connection, 'Unknown prefix: ' + prefix)

        handler = self._handlers[prefix]
        return handler.handle(connection, line[1:])

    def protocol_error(self, connection, msg):
        CommunicationError.handle(ProtocolError(connection, msg))
