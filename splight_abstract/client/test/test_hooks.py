from unittest import TestCase
from splight_abstract.client.hooks import HooksMixin


class ForTest(HooksMixin):
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

    @staticmethod
    def join_return_values(result):
        a, b, kwargs = result
        return_value = {
            "a": a,
            "b": b,
        }
        return_value.update(**kwargs)
        return return_value

    def test_post_hook(self):
        self.instance.add_post_hook('test', self.join_return_values)
        return_value = self.instance.test(1, 2, c=3)
        self.assertEqual(return_value, {"a": 1, "b":2 , "c":3})

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
