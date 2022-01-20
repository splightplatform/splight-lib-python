import json
from unittest import TestCase
from unittest.mock import patch
from splight_deployment.kubernetes import KubernetesClient, MissingTemplate


class Clazz():
    id = 1


class TestKubernetesClient(TestCase):
    def setUp(self) -> None:
        self.client = KubernetesClient()
        self.instance = Clazz()
        return super().setUp()

    def test_get_deployment_name(self):
        self.assertEqual(self.client.get_deployment_name(self.instance),  f"deployment-clazz-1")

    def test_get_service_name(self):
        self.assertEqual(self.client.get_service_name(self.instance),  f"service-clazz-1")

    def test_get_deployment_yaml_without_template_raises(self):
        with self.assertRaises(MissingTemplate):
            self.client.get_deployment_yaml(self.instance)

    # TODO https://splight.atlassian.net/browse/FAC-223
    # def test_get_deployment_yaml_with_template(self):
    #     pass

    def test_apply_deployment(self):
        with patch("splight_deployment.kubernetes.KubernetesClient.get_deployment_yaml", return_value=""):
            with patch("os.system") as os:
                self.client.apply_deployment(self.instance)
                os.assert_called_once()
                args, _ = os.call_args_list[0]
                self.assertIn('kubectl apply -f', args[0])

    def test_delete_deployment(self):
        with patch("splight_deployment.kubernetes.KubernetesClient.get_deployment_yaml", return_value=""):
            with patch("os.system") as os:
                self.client.delete_deployment(self.instance)
                os.assert_any_call(f"kubectl delete deployment {self.client.get_deployment_name(self.instance)} -n {self.client.namespace}")
                os.assert_any_call(f"kubectl delete service {self.client.get_deployment_name(self.instance)} -n {self.client.namespace}")

    def test_get_info(self):
        return_value = {"key": "value"}
        with patch("subprocess.getoutput", return_value=json.dumps(return_value)) as sp:
            self.assertDictEqual(self.client.get_info(self.instance, 'pod'), return_value)
            sp.assert_called_once()

    # TODO https://splight.atlassian.net/browse/FAC-223
    # def test_get_status(self):
    #     pass

    # TODO https://splight.atlassian.net/browse/FAC-223
    # def test_get_logs(self):
    #     pass
