#
# Copyright 2018 Quantopian, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from functools import partial

from zipline.finance.blotter.blotter import Blotter
from zipline.utils.compat import mappingproxy


def _make_blotters_core():
    """Create a family of blotter classes that read from the same mapping.

    Returns
    -------
    blotters : mappingproxy
        The mapping of blotter names to blotter objects.
    register : callable
        The function which registers new blotters in the ``blotters``
        mapping.
    unregister : callable
        The function which deregisters blotters from the ``blotters``
        mapping.
    load : callable
        The function which loads the blotters back into memory.
    """
    _blotters = {}  # set of all registered blotters
    # Expose _blotters through a proxy so that users cannot mutate this
    # accidentally. Users may go through `register` to update this which will
    # warn when trampling another blotter class.
    blotters = mappingproxy(_blotters)

    def register(name, blotter_class=None):
        """Register a new blotter class.

        Parameters
        ----------
        name : str
            The name of the blotter class
        blotter_class : type
            A fully implemented subclass of the abstract Blotter class

        Notes
        -----
        This may be used as a decorator if only ``name`` is passed.

        """
        if blotter_class is None:
            # allow as decorator with just name.
            return partial(register, name)

        if name in _blotters:
            raise ValueError('blotter class %r is already registered' % name)

        if not issubclass(blotter_class, Blotter):
            raise TypeError("The class specified is not a subclass of Blotter")

        _blotters[name] = blotter_class

        return blotter_class

    def unregister(name):
        """Unregister an existing blotter class.

        Parameters
        ----------
        name : str
            The name of the blotter class

        Raises
        ------
        ValueError
            Raised when no blotter class is registered to ``name``
        """
        try:
            del _blotters[name]
        except KeyError:
            raise ValueError(
                'blotter class %r was not already registered' % name,
            )

    def load(name):
        """Return the blotter class registered with the given name.

        Returns
        -------
        blotter class : type
            A blotter class.

        Raises
        ------
        ValueError
            Raised when no blotter class is registered to ``name``
        """
        try:
            blotter_class = _blotters[name]
        except KeyError:
            raise ValueError(
                'no blotter class registered as %r, options are: %r' % (
                    name,
                    sorted(_blotters),
                ),
            )

        return blotter_class

    return blotters, register, unregister, load


blotters, register, unregister, load = _make_blotters_core()
