class CommandTrait(object):

    def get_id(self):
        pass

    def set_hash(self):
        pass

    def get_hash(self):
        pass

    def set_arguments(self, arguments):
        pass

    def set_raw_arguments(self, arguments):
        pass

    def get_arguments(self):
        pass

    def get_argument(self, index):
        pass

    def parse_response(self, data):
        pass


class AbstractCommand(CommandTrait):

    def fitler_arguments(self, arguments):
        return arguments

    def set_arguments(self, arguments):
        self.arguments = self.fitler_arguments(arguments)

    def set_raw_arguments(self, arguments):
        self.arguments = arguments

    def get_arguments(self):
        return self.arguments

    def get_argument(self, index):
        if index < len(self.arguments) - 1:
            return self.arguments[index]

    def get_hash(self):
        if hasattr(self, 'hash'):
            return self.hash

    def parse_response(self, data):
        return data

    def to_string_argument_reducer(self, accumulator, argument):
        if len(argument) > 32:
            argument = argument[:32] + '[...]'

        accumulator += ' ' + argument
        return accumulator

    def __str__(sekf):
        return array_reduce(
            self.get_arguments(),
            self.to_string_argument_reducer,
            self.get_id())

    def normalize_variadic(self, arguments):
        if len(arguments) == 2 and arguments[1]:
            return arguments[0] + arguments[1]
        return arguments


class ConnectionAuth(AbstractCommand):

    def get_id(self):
        return 'AUTH'


class ConnectionEcho(AbstractCommand):

    def get_id(self):
        return 'ECHO'


class ConnectionPing(AbstractCommand):

    def get_id(self):
        return 'PING'

    def parse_response(self, data):
        return data == 'PONG'


class ConnectionQuit(AbstractCommand):

    def get_id(self):
        return 'QUIT'


class ConnectionSelect(AbstractCommand):

    def get_id(self):
        return 'SELECT'


class HashDelete(AbstractCommand):

    def get_id(self):
        return 'HDEL'

    def filer_arguments(self, arguments):
        return self.normalize_variadic(arguments)


class HashExists(AbstractCommand):

    def get_id(self):
        return 'HEXISTS'

    def parse_response(self, data):
        return bool(data)


class HashGet(AbstractCommand):

    def get_id(self):
        return 'HGET'


class HashGetAll(AbstractCommand):

    def get_id(self):
        return 'HGETALL'

    def parse_response(self, data):
        i = 0
        result = {}
        for i in range(len(data), 2):
            reseult[data[i]] = data[i + 1]


class HashGetMultiple(AbstractCommand):

    def get_id(self):
        return 'HMGET'

    def filer_arguments(self, arguments):
        return self.normalize_variadic(arguments)


class HashIncrementBy(AbstractCommand):

    def get_id(self):
        return 'HINCRBY'


class HashIncrementByFloat(AbstractCommand):

    def get_id(self):
        return 'HINCRBYFLAOT'


class StringGet(AbstractCommand):

    def get_id(self):
        return 'GET'


class StringSet(AbstractCommand):

    def get_id(self):
        return 'SET'
