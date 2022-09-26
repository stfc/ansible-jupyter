
# Ansible JupyterHub Server with Prometheus Stacks for STFC cloud Openstacks
Provides a JupyterHub Service on an existing Openstack Cluster. This uses the helm chart provided by [ZeroToJupyterHub](https://github.com/jupyterhub/zero-to-jupyterhub-k8s).
## Contents
- [Features](#features)
- [Limitations](#limitations)
- [Requirements](#requirements)
  * [Local Environment Setup](#local-environment-setup)
- [GPU](#gpu)
- [Kubectl Namespaces](#kubectl-namespaces)
- [JupyterHub Config](#jupyterhub-config)
  * [HTTPS Config](#https-config)
    + [Setting up DNS for Lets Encrypt](#setting-up-dns-for-lets-encrypt)
    + [Using existing TLS Certificate](#using-existing-tls-certificate)
  * [Using LDAP Sign In (`config-ldap.yaml.template`)](#Using-LDAP-Sign-In-config-ldapyamltemplate)
    + [Setting up LDAP Authentication](#setting-up-ldap-authentication)
    + [Creating FreeIPA accounts](#creating-freeipa-accounts)
  * [Training Materials](#Training-materials)
- [Deploying JupyterHub](#deploying-jupyterhub)
  * [Variables (`/playbooks/deploy_jhub.yml`)](#variables-playbooksdeploy_jhubyml)
  * [Instructions](#instructions)
  * [SSL Setup](#ssl-setup)
  * [Note on Renewal Limits](#note-on-renewal-limits)
- [Prometheus Stack](#prometheus-stack)
  * [Accessing Grafana and Prometheus dashboard](#accessing-grafana-and-prometheus-dashboard)
- [Virtual Desktop](#virtual-desktop)
- [Enabling sudo for user](#enabling-sudo-for-user)
- [Maintenance and Notes](#maintenance-and-notes)
  * [Single hub instance](#single-hub-instance)
  * [Autoscaler](#autoscaler)
  * [Proxy_public service notes](#proxy_public-service-notes)
- [Related repositories](#related-repositories)

## Features

- **(New) LDAP authentication**
- **(New) Deploy Prometheus stack to monitor the cluster**
- **(New) Deploy a pre-configured Grafana dashboard for monitoring GPU and JupyterHub**
- **(New) Deploy Virtual Desktop environment**
- **(New) Allow GPU worker for lower Kubernetes version**
- Oauth2 or Local Authentication
- Multiple profiles for different resources limits
- Placeholder support for the default profile, allowing users to get a Jupyter server in <3 minutes
- Ability to use mixed node sizes
- Nvidia GPU Support
- Cinder support
- Automatic HTTPS support, can have a instance up in <1 hour (with pre-requisites in place)

## Limitations

- Existing Cinder volumes cannot be re-attached/transferred on cluster re-creation
- The primary worker/master flavour cannot be changed after creation
- Cannot use placeholders for optional profiles (e.g. GPU placeholder)
- Some metrics can't be selected by node name in Grafana dashboard as it requires a reverse DNS.

## Requirements

- Ansible ([Installing Ansible — Ansible Documentation](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html))
- Helm 3 ([Installing Helm](https://helm.sh/docs/intro/install/))
- kubectl ([Install Tools | Kubernetes](https://kubernetes.io/docs/tasks/tools/))
- Python 3
  - `ansible, kubernetes`
### Local Environment Setup
- Upgrade pip3 as the default version is too old to handle the required deps: `pip3 install pip --upgrade`
- Activate .venv if present then install pip deps: `pip3 install ansible setuptools setuptools-rust pyyaml kubernetes`
- Clone the repository and cd into it
- Install requirements `ansible-galaxy collection install -r requirements.yml`

## GPU

- GPU drivers will automatically be pulled from the Nvidia NGC catalogue
- Driver version is defined in playbooks/deploy_jhub.yml


## Kubectl Namespaces

All components are installed in the user-selected namespace and the Prometheus-stack is deployed to the `prometheus` namespace. This means every command must:

- Include `-n <namespace>` on every command
- (Preferred) use [Kubectx and kubens](https://github.com/ahmetb/kubectx) and set the namespace for this session with `kubectl ns jhub`

All subsequent Kubernetes commands will omit the namespace for brevity.

## JupyterHub Config

- Ensure that the terminal Ansible will run in can access the correct cluster (`kubectl get no`).
- Check the config in `playbooks/deploy_jhub.yml`.
- Copy the content of `config.yaml.template`(in `/roles/deploy_jhub/files/`) to create a `config.yaml` in the same directory and ensure the various secrets and fields marked:
- Go through each line checking the config values are as expected. Additional guidance is provided below:

### HTTPS Config

#### Setting up DNS for Lets Encrypt

Lets Encrypt is used to handle HTTPS certificates automatically. Jupyterhub can have unusual problems in HTTP mode only, so I would strongly strongly advice you run it with some level of TLS.

Simply ensure you have:
- An external IP address
- A internet routable domain name
- A (optionally/and/or) AAAA record(s) pointing to the IP address

Update the config file with the domain name, by default it's set to `jupyter.stfc.ac.uk`.

#### Using existing TLS Certificate 

Alternatively, if you already have an existing certificate and don't want to expose the service externally you can manually provide a certificate.

The primary disadvantage of this, is both remembering to renew the certificate annually and the associated downtime compared to the automatic Lets Encrypt method.

A Kubernetes secret is used, instructions can be found [here](https://zero-to-jupyterhub.readthedocs.io/en/latest/administrator/security.html#specify-certificate-through-secret-resource)

### Using LDAP Sign In (`config-ldap.yaml.template`)

For short-term deployments, where a list of authorized users is suitable, simply use the native authenticator (see `config.yaml.template`).

#### Setting up LDAP Authentication

- The LDAP authenticator uses a server, such as a FreeIPA server, for authentication
- Copy config-ldap.yaml.template to config.yaml and populate the file with the details described below
- Enter your LDAP server address in `<server address>`
- Enter the user search base in `<search base>`
  * For FreeIPA, the form of this is based on the initial domain that IPA was configured with
  * For example, a domain of stfc.ac.uk would require `user_search_base: "cn=users,cn=accounts,dc=stfc,dc=ac,dc=uk"`
- Enter any admin users
  * Further admins can be promoted by editing users on JupyterHub

Notes:

- Users cannot login to JupyterHub without an account on the LDAP server
- Users must be managed on both JupyterHub and the LDAP server separately. For example:
  * Creating an account on the LDAP server does not create a JupyterHub account, and vice versa (`open_signup` and `allowed_users` are therefore invalid options)
  * Similarly, deleting users on the LDAP server does not delete JupyterHub users, and vice versa
  * Admin privileges on the LDAP server are unrelated to JupyterHub admin privileges
- Secondary LDAP servers are not currently supported

#### Creating FreeIPA accounts

Scripts are avaiable in `/scripts` to create (`create_users.py`) and delete (`delete_users.py`) groups of FreeIPA users. The configuration for your FreeIPA server must be entered in `freeipa_config.yml` within the same directory, and the `python_freeipa` package must be installed.

For example, to create 20 users of the form `jupyter-user-x` and save the usernames and passwords in a text file, run:

`python3 scripts/create_users.py --basename "jupyter-user" --first_index 1 --last_index 20 > users.txt`

### Training Materials

The NFS server IP address must be entered in `/roles/deploy_jhub/files/nfs-pv.yaml`


## Deploying JupyterHub
### Variables (`/playbooks/deploy_jhub.yml`)
| Variable | Description | Default |
| --------- | ---------- | ---------|
| `jhub_deployed_name` | Helm name of JupyterHub. | `jupyterhub` |
| `jhub_namespace` | Kubernetes Namespace for JupyterHub | `jupyterhub` |
| `jhub_version` | Helm chart version for JupyterHub (Newer versions may require a more recent kubernetes version)  | `"1.2.0"` |
| `jhub_config_file` | Name of helm values file of JupyterHub (place the file in `/roles/deploy_jhub/files/`) | `"config.yaml"` |
| `prometheus_deployed_name` | Helm name of Prometheus Stack | `prometheus` |
| `prometheus_namespace` | Kubernetes Namespace for Prometheus Stack | `prometheus` |
| `grafana_password` | Admin Password for Grafana. | `"temp_password"` |
| `NVIDIA_DRIVER_VERSION` | Image tag from the Nvidia NGC catalogue | `515.48.07` |

### Instructions

- Login to the openstack GUI before deploying, as this saves a step later...
- Deploy the jupyterhub instance with `ansible-playbook playbooks/deploy_jhub.yml`
- Whilst it's deploying go to Network -> Load Balancers, look for one labelled with `proxy_public`for JHub, it may take a minute to appear as images are pulled.
- Take note of the 10.0.x.x IP, go to Floating IPs (FIP).
- Associate your prepared FIP with matching DNS records to that whilst the load balancer is being created.
- If you do not associate a prepared FIP, Cluster API will associate a random FIP as the final step of creating the load balancer, which must be disassociated and released before your FIP can be associated.

### SSL Setup

The Lets Encrypt (LE) certificate will have failed to issue, as the LB takes longer to create than the first issue. To issue your first certificate and enable automatic renewal:

As there are a limited number of attempts we can do (see [rate limit](https://letsencrypt.org/docs/rate-limits/)) some sanity checks help ensure we don't run out of attempts:

- Check deployed `config.yaml` for the domain name
- Test that the domain is using the correct external IP **from an external server** with `dig`. E.g. `dig example.com @1.1.1.1`
- Test that the HTTP server is serving with `telnet example.com 80`

We need to force the HTTPS issuer to retry:
- `kubectl get pods` and take note of the pod name with `autohttps`
- Delete the auto HTTPS pod like so: `k delete pod/autohttps-f954bb4d9-p2hnd` with the unique suffix varying on your cluster
- Wait 1 minute. The logs can be monitored with: `watch kubectl logs service/proxy-public -n jupyterhub -c traefik`
- Warnings about implicit names can be ignored. If successful there will be *no* error printed after a minute.
- Go to `https://<domain>.com` and it should be encrypted.

### Note on Renewal Limits

A maximum of 5 certificates will be issued to a set of domain names per week (on a 7 day rolling basis). Updating a deployment does not count towards this as Kubernetes holds the TLS secret. 

However, `helm uninstall jhub` will delete the certificate counting towards another when redeployed.

The currently issued certificate(s) can be viewed at: https://crt.sh/

## Prometheus Stack
The Prometheus-Grafana stack is deployed automatically when deploying JupyterHub. user can set password using the `grafana_password` variable.
The service monitors are pre-configured to monitor the Kubernetes cluster, JupyterHub and GPU-Operator.
The default dashboard is located in the STFC folder which contains a comprehensive set of information.

### Accessing Grafana and Prometheus dashboard
User `kubectl get service -A` to check the IP of grafana and prometheus.

## Virtual Desktop
In `/role/deploy_jhub/files/config.yaml` uncomment the part in profile list.
```yaml
singleuser:
  ...
  profilelist:
    ...
    # - display_name: "VDI-testing"
    #   description: |
    #     Deploy image with vitual desktop 4 CPUs, 4GB RAM
    #   kubespawner_override:
    #     image: harbor.stfc.ac.uk/stfc-cloud/jupyterhub-desktop-development:latest
    #     cpu_limit: 4
    #     cpu_guarantee: 0.05
    #     mem_limit: "4G"
    #     mem_guarantee: "4G"
    #     extra_resource_limits: {}
```

## Enabling sudo for user
If you want to enable sudoer for users you can uncomment this block as well. However, this 
would only work for images originated from [jupyter/docker-stack](https://github.com/jupyter/docker-stacks) and allow sudoer for all images.
```yaml
singleuser:
  ...
  # extraEnv:
  #   GRANT_SUDO: "yes"
  #   NOTEBOOK_ARGS: "--allow-root"
  # uid: 0
  # cmd: start-singleuser.sh
```


## Maintenance and Notes

If your are maintaining the service there are a couple of important things to note:

### Single hub instance

Jupyterhub is not designed for high availability, this means only a single pod can ever exist. Any upgrades or modifications to the service will incur a user downtime of a few minutes.

Any existing Pods containing user work will not be shutdown or restarted unless the profiles have changed. To be clear, hub redeploying will have a minor outage but without clearing existing work.

### Autoscaler

The autoscaler is the most "brittle" part of the deployment as it has to work with heat. The logs can be monitored with:

- `kubectl logs deployment/cluster-autoscaler --follow -n kube-system`

The maximum number of nodes can be changed with:

- `kubectl edit deployment/cluster-autoscaler -n kube-system`
- Under image arguments the max number of instances can be changed
- Saving the file will redeploy the auto scaler with the new settings immediately.

### Proxy_public service notes

Deleting the public service endpoint does not delete the load balancer associated. **You must delete the load balancer** to prevent problems, as any redeployment of the service uses the existing LB without updating the members inside. This will cause the failover to stop working as well.

The following symptoms of this happening are:
- `kubectl get all -n kube-system` shows everything but the external service as completed
- The external service will be pending, but on the openstack GUI the LB will be active (not updating / creating)
- The service is not accessible as the old pod is still referred to.

To fix this:
- Delete the service in Kubernetes and load balancer in openstack
- Re-run the ansible deployment script (see deploy Jupyterhub), this will recreate the service.
- Associate the desired floating IP as described above

## Related repositories
- [Kubernetes-GPU-Jupyterhub-Dashboard](https://github.com/stfc/Kubernetes-GPU-Jupyterhub-Dashboard)
- JupyterDesktop Bundle Images (Docker build instructions for JupyterHub Image) (STFC GitLab Link)
