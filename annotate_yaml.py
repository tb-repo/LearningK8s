from pathlib import Path
import re
import shutil

root = Path('D:/HeroVired/Kubernetes/Projects/LearningK8s')
backup_root = root / 'yaml-backup'
backup_root.mkdir(exist_ok=True)

comments = {
    'apiVersion': 'API version of this Kubernetes object',
    'kind': 'Type of Kubernetes resource',
    'metadata': 'Object metadata: name, namespace, labels, annotations',
    'name': 'Name of the object or container',
    'namespace': 'Namespace in which the object is created',
    'labels': 'Labels used for grouping and selecting objects',
    'annotations': 'Annotations for non-identifying metadata',
    'spec': 'Desired state of this object',
    'selector': 'Selector used to choose matching pods or objects',
    'matchLabels': 'Label matching rules for selectors',
    'template': 'Pod template for controllers like Deployment/StatefulSet',
    'containers': 'Container definitions in the pod',
    'image': 'Container image to run',
    'imagePullPolicy': 'When Kubernetes pulls the container image',
    'ports': 'Ports exposed by this object or container',
    'protocol': 'Network protocol for the port',
    'port': 'Port exposed by the Service or container',
    'targetPort': 'Destination port on the container for Service traffic',
    'containerPort': 'Port exposed by the container',
    'resources': 'CPU/memory requests and limits or other resource settings',
    'requests': 'Guaranteed resources requested for scheduling',
    'limits': 'Maximum resources the container may use',
    'command': 'Container startup command',
    'args': 'Arguments passed to the command',
    'environment': 'Environment variables for the container or service',
    'env': 'Environment variables for the container',
    'envFrom': 'Import environment variables from ConfigMap or Secret',
    'volumeMounts': 'Mount points for volumes inside the container',
    'volumes': 'Volumes available to the pod',
    'clusterIP': 'Cluster IP for Services; None means headless',
    'serviceName': 'Headless service used by StatefulSet for stable pod DNS',
    'replicas': 'Desired number of pod replicas',
    'minReplicas': 'Minimum pods allowed by HPA',
    'maxReplicas': 'Maximum pods allowed by HPA',
    'metrics': 'Metrics the HPA uses to scale',
    'behavior': 'Scaling rules for HPA behavior',
    'scaleUp': 'Rules for scaling up pods',
    'scaleDown': 'Rules for scaling down pods',
    'stabilizationWindowSeconds': 'Delay window to stabilize before scaling changes',
    'policies': 'Allowed scaling increments and rates',
    'target': 'Target value for a metric',
    'targetRef': 'Object referenced by autoscaler',
    'scaleTargetRef': 'Target Deployment/StatefulSet for this HPA',
    'volumeClaimTemplates': 'PVC templates each StatefulSet pod creates',
    'storageClassName': 'StorageClass used for dynamic provisioning',
    'accessModes': 'Allowed access mode(s) for the volume',
    'resourcePolicy': 'Resource constraints for VPA-managed containers',
    'updatePolicy': 'How the VPA should apply recommended changes',
    'services': 'Compose services and Kubernetes service definitions',
    'volumes': 'Persistent volumes or Compose volumes',
    'networks': 'Compose networks or Kubernetes network names',
    'build': 'Build settings for the container image',
    'depends_on': 'Service startup ordering in Compose',
    'deploy': 'Deployment settings in Compose',
    'restart': 'Restart policy for containers',
    'imagePullSecrets': 'Secrets used to pull container images',
    'data': 'Data entries for ConfigMaps or Secrets',
    'stringData': 'String data for Secrets',
    'app': 'Application label',
    'tier': 'Tier label for grouping related components',
    'session': 'Session label for a learning scenario',
    'accessModes': 'Volume access mode(s)',
    'hostPath': 'Host path volume source',
    'path': 'Filesystem path for a volume',
    'target': 'Target object or metric',
    'selector': 'Selector used to choose matching objects',
}

for path in sorted(root.rglob('*')):
    if path.is_file() and path.suffix.lower() in {'.yml', '.yaml'}:
        # Backup original file before annotation
        backup_path = backup_root / path.relative_to(root)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_path)

        lines = path.read_text(encoding='utf-8').splitlines(True)
        stack = []
        out_lines = []
        for line in lines:
            stripped = line.lstrip()
            if stripped.startswith('#') or stripped.strip() == '':
                out_lines.append(line)
                continue
            indent = len(line) - len(stripped)
            while stack and stack[-1][0] >= indent:
                stack.pop()
            key_match = re.match(r'^([\w-]+):(?:\s*(.*))?$', stripped)
            comment = None
            if key_match:
                key = key_match.group(1)
                comment = comments.get(key)
                if comment:
                    # Avoid duplicate comment if already present above
                    previous = out_lines[-1] if out_lines else ''
                    if not (isinstance(previous, str) and previous.strip().startswith('#')):
                        out_lines.append(' ' * indent + '# ' + comment + '\n')
            if key_match and stripped.endswith(':'):
                stack.append((indent, key_match.group(1)))
            out_lines.append(line)
        path.write_text(''.join(out_lines), encoding='utf-8')

print('Annotated YAML files in place with backups in yaml-backup/')
