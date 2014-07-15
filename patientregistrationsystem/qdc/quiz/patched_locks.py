from django.core.files import locks


def ignore(*args):
    pass


def patch(f, Error=IOError, errno=45, fallback=ignore):

    def g(*args):
        try:
            f(*args)
        except Error, e:
            if e.errno == errno:
                fallback(*args)
            else:
                raise
    g.__name__ = f.__name__
    g.__doc__ = g.__doc__
    return g

lock = patch(locks.lock)
unlock = patch(locks.unlock)

LOCK_EX = locks.LOCK_EX
LOCK_SH = locks.LOCK_SH
LOCK_NB = locks.LOCK_NB
