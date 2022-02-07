import json
from unittest import TestCase
from unittest.mock import patch
from splight_deployment.kubernetes import KubernetesClient, MissingTemplate
from splight_deployment.models import Deployment, DeploymentInfo


class TestKubernetesClient(TestCase):
    def setUp(self) -> None:
        self.client = KubernetesClient()
        self.instance = Deployment(
            id='1',
            type='Network',
            subtype='openvpn',
            version="0_1_0"
        )
        return super().setUp()

    def test_create_deployment_without_template_raises(self):
        self.instance.type = "MissingClass"
        with self.assertRaises(MissingTemplate):
            self.client.create(self.instance)

    def test_create_deployment(self):
        deployment = self.client.create(self.instance)
        self.assertIsInstance(deployment, DeploymentInfo)
        self.assertIsNotNone(deployment.spec)
        self.assertEqual(deployment.namespace, self.client.namespace)
        self.assertEqual(deployment.service, self.client._get_service_name(self.instance))
        self.assertEqual(deployment.name, self.client._get_deployment_name(self.instance))

    def test_apply_deployment(self):
        info = self.client.create(self.instance)
        with patch("os.system") as os:
            _ = self.client.apply(info)
            os.assert_called_once()
            args, _ = os.call_args_list[0]
            self.assertIn('kubectl apply -f', args[0])

    def test_delete_deployment(self):
        deployment = self.client.create(self.instance)
        with patch("os.system") as os:
            _ = self.client.apply(deployment)
            self.client.delete(id=self.instance.id)
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
            self.assertEqual(self.client.get(), expected_result)
            sp.assert_called_once()

    def test_namespace_name_tuned(self):
        self.client = KubernetesClient(namespace='UPPER_WITH_UNDERSCOReee')
        self.assertEqual(self.client.namespace, 'upperwithunderscoreee')

    def test_startup(self):
        # TODO
        pass
