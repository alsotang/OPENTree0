import web
import config



def _create_memcache_client():
    try:
        import pylibmc
        return pylibmc.Client()
    except ImportError:
        import memcache
        return memcache.Client(['127.0.0.1:11211'])

cache = _create_memcache_client()

def _create_db():
    host = config.MYSQL_HOST
    db = config.MYSQL_DB
    port = config.MYSQL_PORT
    user = config.MYSQL_USER
    pw = config.MYSQL_PASS
    try:
        import sae.const
        if sae.const.MYSQL_USER:
            db = sae.const.MYSQL_DB
            user = sae.const.MYSQL_USER
            pw = sae.const.MYSQL_PASS
            host = sae.const.MYSQL_HOST
            port = int(sae.const.MYSQL_PORT)
    except ImportError:
        pass
    return web.database(dbn='mysql', host=host, port=port, db=db, user=user, pw=pw)

db = _create_db()


if __name__ == '__main__':
    pass
