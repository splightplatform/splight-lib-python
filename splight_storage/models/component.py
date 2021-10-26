from django.db import models
from jinja2 import Template
from splight_storage.models.tag import Tag
from splight_storage.models.tenant import TenantAwareModel


class DigitalOfferComponent(models.Model):
    name = models.CharField(max_length=100)

    @property
    def container_name(self):
        return self.name.lower()

    def __str__(self):
        return self.name


class DigitalOffer(models.Model):
    name = models.CharField(max_length=100)
    components = models.ManyToManyField(
        DigitalOfferComponent, related_name='digital_offers')

    @property
    def template_yaml(self):
        # TODO read this from self._template_yaml FileField
        return f"""
        apiVersion: apps/v1
        kind: Deployment
        metadata:
            namespace: {{{{ rdo.namespace_name }}}}
            name: {{{{rdo.deployment_name}}}}
            labels:
                app: {{{{rdo.deployment_name}}}}
        spec:
            replicas: 1
            selector:
                matchLabels:
                    app: {{{{rdo.deployment_name}}}}
            template:
                metadata:
                    labels:
                        app: {{{{rdo.deployment_name}}}}
                spec:
                    containers:
                        {{% for component in rdo.digital_offer.components.all() %}}
                        - name: {{{{component.container_name}}}}
                          image: splight-components
                          command: ["python", 'runner.py']
                          args: ['-c', '{{{{ component.name }}}}', '-n', '{{{{ rdo.network_name }}}}']
                          imagePullPolicy: "IfNotPresent"
                          tty: true
                        {{% endfor %}}
            """

    def __str__(self):
        return self.name


class RunningDigitalOffer(TenantAwareModel):
    tag = models.ForeignKey(Tag, related_name="digital_offers", on_delete=models.CASCADE, null=True)
    digital_offer = models.ForeignKey(DigitalOffer, related_name='running', on_delete=models.CASCADE)

    @property
    def namespace_name(self):
        return self.tenant.org_id.lower()

    @property
    def deployment_name(self):
        return f"{self.namespace_name}-{self.id}"

    @property
    def deployment_yaml(self):
        template = Template(self.digital_offer.template_yaml)
        return template.render(rdo=self)

    def __str__(self):
        return f"{self.digital_offer}@{self.tag}-{self.tenant.org_id}"