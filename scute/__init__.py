# pylint: disable=missing-docstring

from typing import Callable

# This is almost a copy-n-paste from Pimple 1.1 (excepted that services are shared by default here).
# @link https://github.com/silexphp/Pimple/blob/1.1/lib/Pimple.php


class Container:

    def __init__(self, values=None):
        self._values = values or {}
        self._callable_results_cache = {}
        self._factories = []
        self._protected = []

    def __setitem__(self, injection_id: str, value):
        self._values[injection_id] = value

    def __getitem__(self, injection_id: str):
        if injection_id in self._callable_results_cache:
            return self._callable_results_cache[injection_id]
        if injection_id not in self._values:
            raise UnknownIdentifierError(injection_id)

        is_callable: bool = callable(self._values[injection_id])
        if is_callable:
            if self._values[injection_id] in self._protected:
                result = self._values[injection_id]
            else:
                result = self._values[injection_id](self)
        else:
            result = self._values[injection_id]

        if self._values[injection_id] not in self._factories:
            self._callable_results_cache[injection_id] = result

        return result

    def __contains__(self, injection_id: str):
        return injection_id in self._values

    def __delitem__(self, injection_id: str):
        if injection_id in self._values:
            del self._values[injection_id]

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

    def raw(self, injection_id: str):
        if injection_id not in self._values:
            raise UnknownIdentifierError(injection_id)

        return self._values[injection_id]

    def extend(self, injection_id: str, factory: Callable):
        if injection_id not in self._values:
            raise UnknownIdentifierError(injection_id)
        if not callable(self._values[injection_id]):
            raise NotCallableExtendedServiceError()
        if not callable(factory):
            raise NotCallableFactoryError()

        extended_factory = self._values[injection_id]

        def service_extension(container: Container):
            return factory(extended_factory(container), container)

        self._values[injection_id] = service_extension

        return service_extension


    def bind_callable(self, dependencies: tuple, injection_id: str = None):
        def decorator(injections_target: Callable):
            if not callable(injections_target):
                raise NotCallableError()

            def callable_wrapped(container=None): # pylint: disable=unused-argument
                resolved_dependencies = (self[injection_id] for injection_id in dependencies)
                return injections_target(*resolved_dependencies)

            if injection_id is not None:
                self._values[injection_id] = callable_wrapped

            return callable_wrapped

        return decorator


class UnknownIdentifierError(Exception):
    def __init__(self, injection_id: str, *args, **kwargs):
        super(UnknownIdentifierError, self).__init__(*args, **kwargs)
        self.injection_id = injection_id


class NotCallableError(Exception):
    pass


class NotCallableExtendedServiceError(NotCallableError):
    pass


class NotCallableFactoryError(NotCallableError):
    pass


class NotCallableProtectError(NotCallableError):
    pass
