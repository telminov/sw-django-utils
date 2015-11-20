from __future__ import print_function
from django.conf import settings
from django.test.runner import DiscoverRunner


class TestRunnerWithMongo(DiscoverRunner):
    mongodb_name = 'test_%s' % (settings.MONGODB['NAME'], )

    def get_addition_mongodb_aliases(self):

        return tuple()

    def _get_params(self):
        params = {
            'host': settings.MONGODB.get('HOST'),
        }
        if settings.MONGODB.get('PORT'):
            params['port'] = settings.MONGODB['PORT']
        if settings.MONGODB.get('USER'):
            params['username'] = settings.MONGODB['USER']
        if settings.MONGODB.get('PASSWORD'):
            params['password'] = settings.MONGODB['PASSWORD']
        return params

    def setup_databases(self, **kwargs):
        from mongoengine.connection import connect, disconnect, register_connection

        # main mongo database
        # disconnect()
        connect(self.mongodb_name, **self._get_params())
        print('Creating mongo test database %s for alias \'default\'' % self.mongodb_name)

        # additional databases
        addition_aliases = self.get_addition_mongodb_aliases()
        for alias in addition_aliases:
            print('Creating mongo test database %s for alias \'%s\'' % (self.mongodb_name, alias))
            disconnect(alias=alias)
            register_connection(alias, self.mongodb_name, **self._get_params())

        return super(TestRunnerWithMongo, self).setup_databases(**kwargs)

    def teardown_databases(self, old_config, **kwargs):
        from mongoengine.connection import connect, get_connection, disconnect, register_connection

        # main mongo database
        connection = get_connection()
        try:
            connection.drop_database(self.mongodb_name)
            print('Dropping mongo test database %s for alias \'default\'' % self.mongodb_name)
        except Exception as ex:
            print('Can not to drop mongo test database %s for alias \'default\': %s' % (self.mongodb_name, ex))
        # disconnect()

        # additional databases
        addition_aliases = self.get_addition_mongodb_aliases()
        for alias in addition_aliases:
            connection = get_connection(alias=alias)
            try:
                connection.drop_database(self.mongodb_name)
                print('Dropping mongo test database %s for alias \'%s\'' % (self.mongodb_name, alias))
            except Exception as ex:
                print('Can not to drop mongo test database %s for alias \'%s\': %s' % (self.mongodb_name, alias, ex))
            disconnect()

        super(TestRunnerWithMongo, self).teardown_databases(old_config, **kwargs)



class TearDownTestCaseMixin(object):

    def tearDownMongo(self):
        from mongoengine.connection import get_db

        db = get_db()
        collections = db.collection_names()
        for col in collections:
            if col == 'system.indexes':
                continue
            db[col].drop()

