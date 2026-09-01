# projeto-gitops

Projeto de portfólio que demonstra provisionamento de infraestrutura com **Terraform**,
orquestração com **Kubernetes local (kind)** e entrega contínua via **GitOps (ArgoCD)**,
com pipelines de **CI/CD no GitHub Actions**.

## Arquitetura

```
Terraform
  ├─ cria o cluster Kubernetes local (kind)
  └─ instala o ArgoCD no cluster (via Helm) + cria o Application do ArgoCD

ArgoCD (rodando no cluster)
  └─ observa a pasta manifests/ do repositório e sincroniza sozinho (GitOps "pull")

GitHub Actions
  ├─ terraform.yaml → valida o Terraform (fmt/validate/plan) a cada Pull Request
  └─ build.yaml      → builda a imagem da app, publica no Docker Hub, atualiza a
                        tag da imagem em manifests/deployment.yml e comita de volta
                        (o ArgoCD detecta essa mudança e sincroniza sozinho)
```

O CI **nunca acessa o cluster diretamente** — ele só publica a imagem e atualiza o
manifest no Git. É o ArgoCD, rodando dentro do cluster local, quem puxa as mudanças
(deploy "pull", não "push"). Isso resolve o problema de o runner do GitHub Actions
(que roda na nuvem) não conseguir alcançar um cluster que existe só na máquina local.

## Estrutura do projeto

```
app/              # código da aplicação (Flask) + Dockerfile
argocd/           # definição do Application do ArgoCD (bootstrap, aplicado uma vez)
manifests/        # Deployment/Service da aplicação — é isso que o ArgoCD observa
modules/
  ├─ kind/        # módulo Terraform que cria o cluster kind
  └─ helm/        # módulo Terraform que instala um chart Helm (usado para o ArgoCD)
project/          # root module do Terraform (providers, backend, chama os módulos)
.github/workflows/
  ├─ terraform.yaml  # CI: fmt/validate/plan do Terraform a cada PR
  └─ build.yaml       # build + push da imagem + atualização do manifest
```

## Como rodar do zero

Pré-requisitos: [Docker](https://docs.docker.com/get-docker/),
[kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation),
[kubectl](https://kubernetes.io/docs/tasks/tools/) e
[Terraform](https://developer.hashicorp.com/terraform/install) instalados.

```bash
cd project
terraform init
terraform apply -target=module.k8s   # cria o cluster primeiro
terraform apply                      # instala o ArgoCD no cluster já existente
kubectl apply -f ../argocd/application.yaml
```

Depois disso, o ArgoCD assume a sincronização da aplicação a partir da pasta
`manifests/` automaticamente.

## Documentações usadas

**Terraform**
- [Terraform Language](https://developer.hashicorp.com/terraform/language)
- [Provider tehcyx/kind](https://registry.terraform.io/providers/tehcyx/kind/latest/docs)
- [Provider hashicorp/kubernetes](https://registry.terraform.io/providers/hashicorp/kubernetes/latest/docs)
- [Provider hashicorp/helm](https://registry.terraform.io/providers/hashicorp/helm/latest/docs)

**Kubernetes / kind**
- [kind — Quick Start](https://kind.sigs.k8s.io/docs/user/quick-start/)
- [kubectl reference](https://kubernetes.io/docs/reference/kubectl/)
- [Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Service](https://kubernetes.io/docs/concepts/services-networking/service/)

**ArgoCD**
- [Getting Started](https://argo-cd.readthedocs.io/en/stable/getting_started/)
- [Declarative Setup — Applications](https://argo-cd.readthedocs.io/en/stable/operator-manual/declarative-setup/#applications)
- [Chart argo-cd (argo-helm)](https://github.com/argoproj/argo-helm/tree/main/charts/argo-cd)

**Aplicação (Flask/Docker)**
- [Flask — Quickstart](https://flask.palletsprojects.com/en/latest/quickstart/)
- [Docker — Containerize a Python app](https://docs.docker.com/guides/python/containerize/)
- [Docker — Building best practices](https://docs.docker.com/build/building/best-practices/)

**CI/CD (GitHub Actions)**
- [GitHub Actions — Quickstart](https://docs.github.com/en/actions/writing-workflows/quickstart)
- [Terraform + GitHub Actions (tutorial HashiCorp)](https://developer.hashicorp.com/terraform/tutorials/automation/github-actions)
- [Docker — Build with GitHub Actions](https://docs.docker.com/build/ci/github-actions/)

## GitHub Actions utilizadas

| Action | Uso no projeto |
|---|---|
| [actions/checkout@v4](https://github.com/actions/checkout) | Clona o repositório dentro do runner |
| [hashicorp/setup-terraform@v4](https://github.com/hashicorp/setup-terraform) | Instala o binário do Terraform no runner |
| [docker/setup-buildx-action@v4](https://github.com/docker/setup-buildx-action) | Configura o Buildx para build da imagem Docker |
| [docker/login-action@v4](https://github.com/docker/login-action) | Autentica no Docker Hub usando secrets do repositório |
| [docker/build-push-action@v7](https://github.com/docker/build-push-action) | Builda a imagem da aplicação e publica no Docker Hub |
| [EndBug/add-and-commit@v10](https://github.com/EndBug/add-and-commit) | Comita e publica a atualização da tag da imagem em `manifests/deployment.yml` |

## Decisões de arquitetura

- **Cluster único e persistente** (não efêmero por execução de pipeline) — permite
  usar GitOps de verdade (reconciliação contínua), o que não faria sentido num
  cluster que nasce e morre a cada job de CI.
- **CI/CD sem acesso de rede ao cluster local** — resolvido usando o próprio ArgoCD
  como mecanismo de entrega (pull), em vez de dar ao runner do GitHub Actions
  qualquer forma de alcançar a máquina local (self-hosted runner ou similar).
- **Tag de imagem baseada no SHA do commit** (não `:latest`) — necessário para o
  ArgoCD detectar que existe uma versão nova a sincronizar a cada build.
