
from typing import Callable

# This is almost a copy-n-paste from Pimple 1.1 (excepted that services are shared by default here).
# @link https://github.com/silexphp/Pimple/blob/1.1/lib/Pimple.php


class Container:

    def __init__(self, values = None):
        self._values = values or {}
        self._callable_results_cache = {}
        self._factories = []
        self._protected = []

    def __setitem__(self, id: str, value):
        self._values[id] = value

    def __getitem__(self, id: str):
        if id in self._callable_results_cache:
            return self._callable_results_cache[id]
        if id not in self._values:
            raise UnknownIdentifierError(id)

        is_callable: bool = callable(self._values[id])
        if is_callable:
            if self._values[id] in self._protected:
                result = self._values[id]
            else:
                result = self._values[id](self)
        else:
            result = self._values[id]

        if self._values[id] not in self._factories:
            self._callable_results_cache[id] = result

        return result

    def __contains__(self, id: str):
        return id in self._values

    def __delitem__(self, id: str):
        if id in self._values:
            del self._values[id]

    def factory(self, factory: Callable):
        if not callable(factory):
            raise NotCallableFactoryError()

        self._factories.append(factory)

        return factory

    def protect(self, protected: Callable):
        if not callable(protected):
            raise NotCallableProtectError()

        self._protected.append(protected)

        return protected

    def raw(self, id: str):
        if id not in self._values:
            raise UnknownIdentifierError(id)

        return self._values[id]

    def extend(self, id: str, factory: Callable):
        if id not in self._values:
            raise UnknownIdentifierError(id)
        if not callable(self._values[id]):
            raise NotCallableExtendedServiceError()
        if not callable(factory):
            raise NotCallableFactoryError()

        extended_factory = self._values[id]

        def service_extension(container: Container):
            return factory(extended_factory(container), container)

        self._values[id] = service_extension

        return service_extension


class UnknownIdentifierError(Exception):
    def __init__(self, id: str):
        self.id = id


class NotCallableExtendedServiceError(Exception):
    pass


class NotCallableFactoryError(Exception):
    pass


class NotCallableProtectError(Exception):
    pass
