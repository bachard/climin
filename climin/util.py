# -*- coding: utf-8 -*-


import inspect
import random

from asgd import Asgd
from gd import GradientDescent
from ksd import KrylovSubspaceDescent
from lbfgs import Lbfgs
from ncg import NonlinearConjugateGradient
from rprop import Rprop
from smd import Smd


def coroutine(f):
    """Turn a generator function into a coroutine by calling .next() once."""
    def started(*args, **kwargs):
        cr = f(*args, **kwargs)
        cr.next()
        return cr
    return started


def aslist(item):
    if not isinstance(item, (list, tuple)):
        item = [item]
    return item


def mini_slices(n_samples, batch_size):
    """Yield slices of size `batch_size` that work with a container of length
    `n_samples`."""
    n_batches, rest = divmod(n_samples, batch_size)
    if rest != 0:
        n_batches += 1

    return [slice(i * batch_size, (i + 1) * batch_size) for i in range(n_batches)]


def draw_mini_slices(n_samples, batch_size, with_replacement=False):
    slices = mini_slices(n_samples, batch_size)
    idxs = range(len(slices))

    if with_replacement:
        yield random.choice(slices)
    else:
        while True:
            random.shuffle(idxs)
            for i in idxs:
                yield slices[i]


def optimizer(identifier, wrt, *args, **kwargs):
    """Return an optimizer with the desired configuration.

    This is a convenience function if one wants to try out different optimizers
    but wants to change as little code as possible.

    Additional arguments and keyword arguments will be passed to the constructor
    of the class. If the found class does not take the arguments supplied, this
    will `not` throw an error, but pass silently.

    :param identifier: String identifying the optimizer to use. Can be either
        ``asgd``, ``ksd``, ``gd``, ``lbfgs``, ``ncg``, ``rprop`` or  ``smd``.
    :param wrt: Numpy array pointing to the data to optimize.
    """
    klass_map = {
        'asgd': Asgd,
        'ksd': KrylovSubspaceDescent,
        'gd': GradientDescent,
        'lbfgs': Lbfgs,
        'ncg': NonlinearConjugateGradient,
        'rprop': Rprop,
        'smd': Smd,
        }
    # Find out which arguments to pass on.
    klass = klass_map[identifier]
    argspec = inspect.getargspec(klass.__init__)
    if argspec.keywords is None:
        # We need to filter stuff out.
        kwargs = dict((k, v) for k, v in kwargs.items()
                      if k in argspec.args)

    try:
        opt = klass(wrt, *args, **kwargs)
    except TypeError:
        raise TypeError('required arguments for %s: %s' % (klass, argspec.args))

    return opt

