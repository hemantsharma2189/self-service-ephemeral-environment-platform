from urllib.parse import urlparse

import yaml

from preview_env.models import (
    EnvironmentPlan,
    PreviewEnvironmentRequest,
)


def render_kubernetes_manifests(
    request: PreviewEnvironmentRequest,
    plan: EnvironmentPlan,
) -> str:
    labels = {
        "app.kubernetes.io/name": plan.environment_name,
        "preview.platform/pr": str(request.pull_request_number),
        "preview.platform/owner": request.owner,
        "preview.platform/managed-by": "preview-env-platform",
    }

    namespace = {
        "apiVersion": "v1",
        "kind": "Namespace",
        "metadata": {
            "name": plan.namespace,
            "labels": labels,
            "annotations": {
                "preview.platform/ttl-hours": str(request.ttl_hours),
                "preview.platform/commit": request.commit_sha,
            },
        },
    }

    resource_quota = {
        "apiVersion": "v1",
        "kind": "ResourceQuota",
        "metadata": {
            "name": "preview-quota",
            "namespace": plan.namespace,
        },
        "spec": {
            "hard": {
                "requests.cpu": "1",
                "requests.memory": "1Gi",
                "limits.cpu": "2",
                "limits.memory": "2Gi",
                "pods": "5",
            }
        },
    }

    deployment = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": plan.environment_name,
            "namespace": plan.namespace,
            "labels": labels,
        },
        "spec": {
            "replicas": 1,
            "selector": {"matchLabels": {"app": plan.environment_name}},
            "template": {
                "metadata": {
                    "labels": {
                        "app": plan.environment_name,
                        **labels,
                    }
                },
                "spec": {
                    "automountServiceAccountToken": False,
                    "securityContext": {
                        "runAsNonRoot": True,
                        "seccompProfile": {"type": "RuntimeDefault"},
                    },
                    "containers": [
                        {
                            "name": "application",
                            "image": request.image,
                            "imagePullPolicy": "IfNotPresent",
                            "ports": [
                                {
                                    "name": "http",
                                    "containerPort": (request.container_port),
                                }
                            ],
                            "securityContext": {
                                "allowPrivilegeEscalation": False,
                                "capabilities": {"drop": ["ALL"]},
                            },
                            "resources": {
                                "requests": {
                                    "cpu": (request.resources.cpu_request),
                                    "memory": (request.resources.memory_request),
                                },
                                "limits": {
                                    "cpu": (request.resources.cpu_limit),
                                    "memory": (request.resources.memory_limit),
                                },
                            },
                        }
                    ],
                },
            },
        },
    }

    service = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": plan.environment_name,
            "namespace": plan.namespace,
            "labels": labels,
        },
        "spec": {
            "selector": {"app": plan.environment_name},
            "ports": [
                {
                    "name": "http",
                    "port": 80,
                    "targetPort": "http",
                }
            ],
            "type": "ClusterIP",
        },
    }

    ingress = {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "Ingress",
        "metadata": {
            "name": plan.environment_name,
            "namespace": plan.namespace,
            "labels": labels,
        },
        "spec": {
            "ingressClassName": "nginx",
            "rules": [
                {
                    "host": urlparse(plan.preview_url).hostname,
                    "http": {
                        "paths": [
                            {
                                "path": "/",
                                "pathType": "Prefix",
                                "backend": {
                                    "service": {
                                        "name": (plan.environment_name),
                                        "port": {"number": 80},
                                    }
                                },
                            }
                        ]
                    },
                }
            ],
        },
    }

    return yaml.safe_dump_all(
        [
            namespace,
            resource_quota,
            deployment,
            service,
            ingress,
        ],
        sort_keys=False,
    )
