import copy
import os
from redispy.errors import (
    TimeoutError,
    ClientNotSupportedError
    )


# def io(func):
#     def _(*args):
#         try:
#             func(*args)
#         except TimeoutError:
#             pass
#     return _


# class Client(object):

#     """docstring for Client"""
#     DEFAULTS = {


#     }

#     @property
#     def options():
#         return copy.deepcopy(self.options)

#     @property
#     def scheme(self):
#         return self.options['scheme']

#     @property
#     def host(self):
#         return self.options['host']

#     @property
#     def port(self):
#         return self.options['port']

#     def __init__(self, **kwargs):
#         self.options = kwargs
#         self.reconnect = True
#         self.connection = None
#         self.command_map = {}
#         self.proile = profile.autoload(self.kwargs['redis_ver'])

#     def connect(self):
#         self.pid = os.getpid()

#         self.connection = self.adapter(self.options['adapter'])

#     def adapter(self, adapter):
#         pass

#     def disconnect(self):
#         if self.connected:
#             self.connection.disconnect()

#     def __getattr__(self, cmd):
#         def _(*args, **kwargs):
#             _.__name__ = cmd
#             return self.execute(cmd, args, kwargs)
#         return _


#     def execute(self, cmd, args, kwargs):
#         cmd = self.proile.get(cmd)
#         cmd.bind(args, kwargs)
#         self.write(cmd)
#         self.read(cmd)
#         return cmd.response()

#     @io
#     def read(self, command):
#         self.connection.read(cmd)

#     @io
#     def write(self, command):
#         self.connection.write(command)


class ClientTrait(object):

    def get_profile(self):
        pass

    def get_options(self):
        pass

    def disconnect(self):
        pass

    def connect(self):
        pass

    def get_connection(self):
        pass

    def create_command(self, method, arguments={}):
        pass


from redispy.connection import StreamConnection
from redispy.profile import Profile


class Client(ClientTrait):

    def __init__(self, parameters=None, options=None):
        self._options = options
        self._profile = Profile()
        self.connection = StreamConnection()

    def filter_options(self, options):
        if not options:
            return ClientOptions()
        if isinstance(options, dict):
            return ClientOptions(options)
        if isinstance(options, ClientOptions):
            return options
        raise Exception("Invalid type for client options")

    def initialize_connection(self, parameters):
        if isinstance(parameters, ConnectionTrait):
            return parameters

        if isinstance(parameters, list) and parameters:
            options = self._options
            replication = options.replication or None
            connection = 'replication' if replication else 'cluster'
            return options.connections.create_aggregated(connection, parameters)

        if callable(parameters):
            connection = parameters(self._options)
            if isinstance(connection, ConnectionTrait):
                raise Exception(
                    'Callable parameters must return instances of Predis\Connection\ConnectionInterface')
            return connection

        return self.options.connections.create(parameters)

    def get_profile(self):
        return self._profile

    def get_options(self,):
        return self._options

    def get_connection_factory(self):
        return self._options.connections

    def get_client_for(self, connection_id):
        connection = self.get_connection_by_id(connection_id)
        if not connection:
            return Exception('Invalid connection ID: ' + str(connection_id))

        return Client(connection, self._options)

    def connect(self):
        self.connection.connect()

    def disconnect(self):
        return self.connection.disconnect()

    def quit(self):
        self.disconnect()

    def is_connected(self):
        return self.connection.is_connected()

    def get_connection(self):
        return self.connection

    def get_connection_by_id(self, connection_id):
        if isinstance(self.connection, AggregatedConnectionTrait):
            raise ClientNotSupportedError(
                'Retrieving connections by ID is supported only when using aggregated connections')
        return self.connection.get_connection_by_id(connection_id)

    def __getattr__(self, cmd):
        return self.execute(cmd)

    def execute(self, cmd):
        def _(*args, **kwargs):
            command = self.create_command(cmd)
            command.arguments = args
            return self.execute_command(command)
        return _

    def create_command(self, command):
        return self._profile.create_command(command)

    def execute_command(self, command):
        response = self.connection.execute_command(command)
        # if  isinstance(response, ResponseObjectTrait):
        #     if isinstance(response, ResponseError):
        #         response = self.on_response_error(command, response)
        #     return response
        return command.parse_response(response)

    def on_response_error(self, command, response):
        if isinstance(command, ScriptedCommand) and response.error_type == 'NOSCRIPT':
            cmd = self.create_command('eval')
            cmd.set_raw_arguments(cmd.get_eval_arguments())
            response = self.execute_command(cmd)

            if not isinstance(ResponseObjectTrait):
                response = cmd.parse_response(response)
            return response

        if self._options.exceptions:
            raise ServerError(response.get_message())

        return response
