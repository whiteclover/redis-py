#!/usr/bin/env python


from redispy import command


class Profile(object):

    profiles = {}

    def __init__(self):
        self.commands = self.supported_commands()
        #self.processor  = None

    def supported_commands(self):

        return {

            'get': command.StringGet,
            'set': command.StringSet,
            'ping': command.ConnectionPing
        }

    def default(self):
        return self.get('default')

    def development(self):
        return self.get('dev')

    def default_profiles(self):
        pass

    def define(self, name, profile_cls):
        self.profiles[name] = profile_cls

    def get(self, version):
        pass

    def support_commands(self, *commands):
        for command in commands:
            if not self.support_command(self, command):
                return False

        return True

    def support_command(self, command):
        return command.upper() in self.commands

    def get_command_class(self, command):
        return self.commands.get(command)

    def create_command(self, method):
        method = method
        command_class = self.commands.get(method)
        if not command_class:
            raise ClientError(method + ' is not a registered Redis command')

        command = command_class()
        if hasattr(self, 'processor'):
            self.processor.processor(command)

        return command

    def define_command(self, name, command):
        self.commands[name] = command

    def set_processor(self, processor=None):
        self.processor = processor

    def get_processor(self):
        return self.processor
