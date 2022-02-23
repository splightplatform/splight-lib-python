import json
from unittest import TestCase
from unittest.mock import patch
from splight_deployment.kubernetes import KubernetesClient, MissingTemplate
from splight_models import Deployment, Namespace


class TestKubernetesClient(TestCase):
    def setUp(self) -> None:
        self.client = KubernetesClient()
        self.instance = Deployment(
            id='1',
            type='Network',
            subtype='openvpn',
            version="0_1_0"
        )
        self.namespace = Namespace(
            id='anothernamespace',
            environment={
                'key': 'value'
            }
        )
        return super().setUp()

    def test_create_deployment_without_template_raises(self):
        self.instance.type = "MissingClass"
        with self.assertRaises(MissingTemplate):
            self.client.save(self.instance)

    def test_create_deployment(self):
        with patch("os.system") as os:
            self.client.save(self.instance)
            os.assert_called_once()
            args, _ = os.call_args_list[0]
            self.assertIn('kubectl apply -f', args[0])

    def test_delete_deployment(self):
        with patch("os.system") as os:
            self.client.delete(resource_type=Namespace, resource_id=self.instance.id)
            os.assert_any_call(f"kubectl delete deployment --selector=id={self.instance.id} -n {self.client.namespace}")
            os.assert_any_call(f"kubectl delete service --selector=id={self.instance.id} -n {self.client.namespace}")

    def test_get_deployment(self):
        return_value = json.dumps({
            "metadata": {
                "labels": self.instance.dict()
            }
        })
        expected_result = [Deployment(**self.instance.dict())]
        with patch("subprocess.getoutput", return_value=return_value) as sp:
            self.assertEqual(self.client.get(resource_type=Deployment), expected_result)
            sp.assert_called_once()

    def test_client_namespace_tuned(self):
        self.client = KubernetesClient(namespace='UPPER_WITH_UNDERSCOReee')
        self.assertEqual(self.client.namespace, 'upperwithunderscoreee')

    def test_create_namespace(self):
        with patch("os.system") as os:
            self.client.save(self.namespace)
            os.assert_called_once()
            args, _ = os.call_args_list[0]
            self.assertIn('kubectl apply -f', args[0])

    def test_delete_deployment(self):
        with patch("os.system") as os:
            self.client.delete(resource_type=Namespace, id=self.namespace.id)
            os.assert_any_call(f"kubectl delete namespace --selector=id={self.namespace.id}")

    def test_get_namespace(self):
        return_value = json.dumps({
            "metadata": {
                "labels": {
                    "id": self.namespace.id
                }
            }
        })
        expected_result = [Namespace(id=self.namespace.id)]
        with patch("subprocess.getoutput", return_value=return_value) as sp:
            self.assertEqual(self.client.get(resource_type=Namespace), expected_result)
            sp.assert_called_once()
