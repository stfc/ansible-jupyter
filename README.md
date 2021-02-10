Ansible Jupyter Server for STFC Cloud
=====================================

Local Environment Setup
-----------------------

- Activate .venv if present then install pip deps: `pip3 install ansible openstacksdk openshift`
- Install requirements `ansible-galaxy collection install -r requirements.yml`
- Obtain a copy of clouds.yaml for your project, place it in `~/.configs/openstack/clouds.yaml` and rename `openstack` to `jupyter-development`
- Test using `openstack --os-cloud=jupyter-development coe cluster template list`, which will always return built-in templates


SSL Setup
- `k delete pod/autohttps-f954bb4d9-p2hnd`
- `watch kubectl logs service/proxy-public -n jhub -c traefik`

- Add https://jhub.davidsnet.work/hub/spawn
- Enable name scope

Maint
- `k logs deployment/cluster-autoscaler --follow -n kube-system`
- Delete LB to recreate / redeploy, associate fast
- Single hub instance