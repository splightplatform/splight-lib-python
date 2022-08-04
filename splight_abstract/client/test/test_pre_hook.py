from unittest import TestCase
from splight_abstract.client.pre_hook import PreHookMixin


class ForTest(PreHookMixin):
    def test(self, a, b, **kwargs):
        return a, b, kwargs


class TestVariable(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.instance = ForTest()

    @staticmethod
    def a_plus(*args, **kwargs):
        kwargs['a'] += 1
        return args, kwargs

    @staticmethod
    def b_minus(*args, **kwargs):
        kwargs['b'] -= 1
        return args, kwargs

    def test_1_hook(self):
        self.instance.add_pre_hook('test', self.a_plus)

        a, b, kwargs = self.instance.test(1, 2)
        self.assertEqual(a, 2)
        self.assertEqual(b, 2)
        self.assertEqual(kwargs, {})

    def test_2_hook(self):
        self.instance.add_pre_hook('test', self.a_plus)
        self.instance.add_pre_hook('test', self.b_minus)

        a, b, kwargs = self.instance.test(1, 2)
        self.assertEqual(a, 2)
        self.assertEqual(b, 1)
        self.assertEqual(kwargs, {})

    def test_kwargs(self):
        self.instance.add_pre_hook('test', self.a_plus)

        a, b, kwargs = self.instance.test(1, 2, p=3, q=4)
        self.assertEqual(a, 2)
        self.assertEqual(kwargs, {'p': 3, 'q': 4})
