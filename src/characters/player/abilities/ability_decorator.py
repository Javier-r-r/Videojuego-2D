from .component import Component

class AbilityDecorator(Component):
    """
    The base Decorator class follows the same interface as Component.
    Defines the wrapping interface for all concrete decorators.
    """

    def __init__(self, component: Component):
        self._component = component

    @property
    def component(self) -> Component:
        """The Decorator delegates all work to the wrapped component"""
        return self._component

    def get_stats(self) -> dict:
        return self.component.get_stats()