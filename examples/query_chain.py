#!/usr/bin/env python

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from momoko import Pool, QueryChain


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        if not hasattr(self.application, 'db'):
            self.application.db = Pool(1, 20, 10, **{
                'host': 'localhost',
                'database': 'infunadb',
                'user': 'infuna',
                'password': 'password',
                'async': 1
            })
        return self.application.db


class MainHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        qc = QueryChain(self.db, [
            ['SELECT 42, 12, %s, 11;', (23,)],
            self._after_first_query,
            ['SELECT 1, 2, 3, 4, 5;'],
            ['SELECT 123, 132, 678;'],
            self._on_response
        ])
        qc.run()

    def _after_first_query(self, cursor):
        self.write('Results of the first query in the chain: %s<br>' % \
            cursor.fetchall())

    def _on_response(self, cursor):
        self.write('Results of the last query in the chain: %s' % \
            cursor.fetchall())
        self.finish()


def main():
    try:
        tornado.options.parse_command_line()
        application = tornado.web.Application([
            (r'/', MainHandler),
        ])
        http_server = tornado.httpserver.HTTPServer(application)
        http_server.bind(8888)
        http_server.start(0) # Forks multiple sub-processes
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print 'Exit'


if __name__ == '__main__':
    main()