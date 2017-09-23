# pylint: skip-file

from scute import Container, \
    NotCallableExtendedServiceError, NotCallableFactoryError, NotCallableProtectError, UnknownIdentifierError
import pytest

# This is almost a copy-n-paste from Pimple 1.1 test suite (excepted that services are shared by default here).
# @link https://github.com/silexphp/Pimple/blob/1.1/tests/Pimple/Tests/PimpleTest.php

def test_with_string():
    container = Container()
    container['param'] = 'value'

    assert container['param'] == 'value'


def test_with_lambda():
    container = Container()
    container['service'] = lambda container: Service()

    assert isinstance(container['service'], Service)


def test_with_function():
    container = Container()

    def my_function(container):
        return Service()

    container['service'] = my_function

    assert isinstance(container['service'], Service)


def test_services_should_be_same_instance():
    container = Container()
    container['service'] = lambda container: Service()

    service_one = container['service']
    service_two = container['service']

    assert isinstance(service_one, Service)
    assert isinstance(service_two, Service)
    assert service_one is service_two


def test_should_pass_container_as_parameter():
    container = Container()
    container['service'] = lambda container: Service()
    container['container'] = lambda container: container

    assert container['service'] is not container
    assert container['container'] is container


def test_contains():
    container = Container()
    container['param'] = 'value'
    container['service'] = lambda container: Service()
    container['None'] = None

    assert 'param' in container
    assert 'service' in container
    assert 'None' in container
    assert 'non_existent' not in container


def test_constructor_injection():
    params = {'param': 'value'}
    container = Container(params)

    assert container['param'] == 'value'


def test_error_if_non_existent_id():
    container = Container()

    with pytest.raises(UnknownIdentifierError) as excinfo:
        a = container['foo']
    assert excinfo.value.injection_id == 'foo'


def test_del():
    container = Container()
    container['param'] = 'value'
    container['service'] = lambda container: Service()

    del container['param'], container['service']

    assert 'param' not in container
    assert 'service' not in container


def test_factory_services_should_be_different():
    container = Container()
    container['service'] = container.factory(lambda container: Service())

    service_one = container['service']
    service_two = container['service']

    assert isinstance(service_one, Service)
    assert isinstance(service_two, Service)
    assert service_one is not service_two


def test_non_callable_factory_should_raise_an_error():
    container = Container()
    with pytest.raises(NotCallableFactoryError):
        container['service'] = container.factory('not a callable')


def test_protect():
    container = Container()
    container['protected'] = container.protect(lambda: Service())

    assert callable(container['protected'])
    assert isinstance(container['protected'](), Service)


def test_non_callable_protected_should_raise_an_error():
    container = Container()
    with pytest.raises(NotCallableProtectError):
        container['protected'] = container.protect('not a callable')


def test_raw():
    container = Container()

    def my_function(container):
        return Service()

    container['service'] = my_function

    assert callable(container.raw('service'))
    assert container.raw('service') is my_function


def test_raw_error_if_non_existent_id():
    container = Container()

    with pytest.raises(UnknownIdentifierError) as excinfo:
        container.raw('foo')
    assert excinfo.value.injection_id == 'foo'


def test_extend():
    container = Container()
    container['service'] = lambda container: Service('inner')

    def service_extension(extendedServiceResult: Service, c: Container):
        assert isinstance(c, Container)
        assert c is container

        return Service('decorates ' + extendedServiceResult.value)

    container.extend('service', service_extension)

    service_one = container['service']
    assert isinstance(service_one, Service)
    assert service_one.value == 'decorates inner'

    service_two = container['service']
    assert service_one is service_two


def test_extend_error_if_non_existent_id():
    container = Container()

    with pytest.raises(UnknownIdentifierError) as excinfo:
        container.extend('foo', lambda: True)
    assert excinfo.value.injection_id == 'foo'


def test_non_callable_extended_should_raise_an_error():
    container = Container()
    container['param'] = 'value'
    with pytest.raises(NotCallableExtendedServiceError):
        container.extend('param', lambda: True)


def test_non_callable_extension_should_raise_an_error():
    container = Container()
    container['service'] = lambda container: Service()
    with pytest.raises(NotCallableFactoryError):
        container.extend('service', 'not a callable')


def test_callable_class_should_be_treated_as_a_factory():
    container = Container()

    service_factory = ServiceFactory()
    container['service'] = service_factory

    assert container.raw('service') is service_factory
    assert not callable(container['service'])
    assert isinstance(container['service'], Service)


def test_non_callable_class_should_be_treated_as_a_parameter():
    non_callable = NonCallable()

    container = Container()
    container['non_callable'] = non_callable

    non_callable_one = container['non_callable']
    assert isinstance(non_callable_one, NonCallable)
    assert non_callable_one is non_callable

    non_callable_two = container['non_callable']
    assert isinstance(non_callable_two, NonCallable)
    assert non_callable_one is non_callable_two


def test_decorator():
    container = Container()

    container['param'] = 'value'
    container['service'] = lambda container: Service()
    container['None'] = None

    test_value = 0

    @container.bind_callable(('param', 'service', 'None'))
    def decorated_service(param, service, none=True, not_injected=42):
        nonlocal test_value
        assert param == 'value'
        assert isinstance(service, Service)
        assert none is None
        assert not_injected is 42
        test_value = 1

    assert test_value == 0
    decorated_service()
    assert test_value == 1


def test_decorator_with_binded_service():
    container = Container()

    container['param'] = 'value'
    container['service'] = lambda container: Service()
    container['None'] = None

    test_value = 0

    @container.bind_callable(dependencies=('param', 'service', 'None'), injection_id='decorated')
    def decorated_service(param, service, none=True, not_injected=42):
        nonlocal test_value
        assert param == 'value'
        assert isinstance(service, Service)
        assert none is None
        assert not_injected is 42
        test_value = 1
        return Service(6)

    assert test_value == 0
    decorated_service = container['decorated']
    assert isinstance(decorated_service, Service)
    assert decorated_service.value == 6
    assert test_value == 1


class Service:
    def __init__(self, value=None):
        self.value = value


class ServiceFactory:
    def __call__(self, c: Container):
        return Service()


class NonCallable:
    pass
