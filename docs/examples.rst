Examples
========

Examples for each functionality in callback and blocking style.

See the :ref:`api` for a more detailed decription of all methods.


Connecting
----------

Connecting to a database server is very simple::

    db = momoko.Client({
        'host': 'localhost',
        'database': 'mydatabsename',
        'user': 'myusername',
        'password': 'mypassword',
        'min_conn': 1,
        'max_conn': 20,
        'cleanup_timeout': 10
    })

The above code can be integrated into a request handler. The following code
creates a database object in the application object if there isn't one yet::

    import momoko

    class BaseHandler(tornado.web.RequestHandler):
        @property
        def db(self):
            if not hasattr(self.application, 'db'):
                self.application.db = momoko.Client({
                    'host': 'localhost',
                    'database': 'mydatabsename',
                    'user': 'myusername',
                    'password': 'mypassword',
                    'min_conn': 1,
                    'max_conn': 20,
                    'cleanup_timeout': 10
                })
            return self.application.db

When you want to use the blocking style API the ``AdispClient`` class needs to
be used instead if the ``Client`` class.


Queries
-------

A single query::

    class MainHandler(BaseHandler):
        @tornado.web.asynchronous
        def get(self):
            self.db.execute('SELECT 42, 12, 40, 11;', callback=self._on_response)

        def _on_response(self, cursor):
            self.write('Query results: %s' % cursor.fetchall())
            self.finish()

And in blocking style::

    class MainHandler(BaseHandler):
        @tornado.web.asynchronous
        @momoko.process
        def get(self):
            cursor = yield self.db.execute('SELECT 42, 12, 40, 11;')
            self.write('Query results: %s' % cursor.fetchall())
            self.finish()


Batch queries
-------------

A batch of queries::

    class MainHandler(BaseHandler):
        @tornado.web.asynchronous
        def get(self):
            self.db.batch({
                'query1': ['SELECT 42, 12, %s, 11;', (23,)],
                'query2': ['SELECT 1, 2, 3, 4, 5;'],
                'query3': ['SELECT 465767, 4567, 3454;']
            }, self._on_response).run()

        def _on_response(self, cursors):
            for key, cursor in cursors.items():
                self.write('Query results: %s = %s<br>' % (key, cursor.fetchall()))
            self.write('Done')
            self.finish()

Blocking style::

    class BatchHandler(BaseHandler):
        @tornado.web.asynchronous
        @momoko.process
        def get(self):
            cursors = yield self.db.batch([
                'SELECT 42, 12, 40, 11;',
                ['SELECT %s, %s;', (45, 14)]
            ])
            for cursor in cursors:
                self.write('Query results: %s<br>' % cursor.fetchall())
            self.finish()


Query chains
------------

A query chain::

    class MainHandler(BaseHandler):
        @tornado.web.asynchronous
        def get(self):
            self.db.chain([
                ['SELECT 42, 12, %s, 11;', (23,)],
                self._after_first_query,
                self._after_first_callable,
                ['SELECT 1, 2, 3, 4, 5;'],
                self._before_last_query,
                ['SELECT %s, %s, %s, %s, %s;'],
                self._on_response
            ]).run()

        def _after_first_query(self, cursor):
            results = cursor.fetchall()
            return {
                'p1': results[0][0],
                'p2': results[0][1],
                'p3': results[0][2],
                'p4': results[0][3]
            }

        def _after_first_callable(self, p1, p2, p3, p4):
            self.write('Results of the first query in the chain: %s, %s, %s, %s<br>' % \
                (p1, p2, p3, p4))

        def _before_last_query(self, cursor):
            results = cursor.fetchall()
            return [i*16 for i in results[0]]

        def _on_response(self, cursor):
            self.write('Results of the last query in the chain: %s' % \
                cursor.fetchall())
            self.finish()

Blocking style::

    class ChainHandler(BaseHandler):
        @tornado.web.asynchronous
        @momoko.process
        def get(self):
            cursors = yield self.db.chain((
                'SELECT 22, 44, 55, 11;',
                self._chain_link_1,
                ['SELECT %s, %s, %s, %s;']
            ))
            for cursor in cursors:
                self.write('Query results: %s<br>' % cursor.fetchall())
            self.finish()

        def _chain_link_1(self, cursor):
            return [i*2 for i in cursor.fetchall()[0]]
