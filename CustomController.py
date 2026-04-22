from flask import Flask, jsonify
from kubernetes import client, config, watch
import threading


app = Flask(__name__)


@app.route("/")
def home():
    return "Controller is running"


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy"
    })


class WatchDeployments:
    def __init__(self):
        config.load_incluster_config()
        self.v1 = client.CoreV1Api()
        self.api = client.AppsV1Api()
        self.w = watch.Watch()

    def watch_deployments(self):
        try:
            for event in self.w.stream(
                self.api.list_namespaced_deployment,
                namespace="default"
            ):
                deployment_name = event["object"].metadata.name
                event_type = event["type"]

                print(
                    f"Event: {event_type} "
                    f"{event['object'].kind} "
                    f"{deployment_name}"
                )

                service_name = f"{deployment_name}-lbservice"

                if event_type == "ADDED":
                    self.create_service(deployment_name, service_name)

                elif event_type == "DELETED":
                    self.delete_service(service_name)

        except Exception as e:
            print(f"Controller error: {str(e)}")

    def create_service(self, deployment_name, service_name):
        obj_meta = client.V1ObjectMeta(
            name=service_name
        )

        ports = [
            client.V1ServicePort(
                port=5000,
                target_port=5000
            )
        ]

        spec = client.V1ServiceSpec(
            selector={"app": deployment_name},
            type="LoadBalancer",
            ports=ports
        )

        body = client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=obj_meta,
            spec=spec
        )

        try:
            self.v1.create_namespaced_service(
                namespace="default",
                body=body
            )
            print(f"Service created: {service_name}")

        except Exception:
            print(f"Service already exists: {service_name}")

    def delete_service(self, service_name):
        try:
            self.v1.delete_namespaced_service(
                namespace="default",
                name=service_name
            )
            print(f"Service deleted: {service_name}")

        except Exception as e:
            print(f"Delete failed: {str(e)}")


if __name__ == "__main__":
    watcher = WatchDeployments()

    watcher_thread = threading.Thread(
        target=watcher.watch_deployments
    )
    watcher_thread.start()

    app.run(host="0.0.0.0", port=5000)