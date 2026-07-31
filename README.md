# infra-k8s Python reference

A deliberately small, dependency-free HTTP service used to prove that an
ordinary application repository can own its source, tests, Dockerfile, local
development workflow, and one provider-neutral `App` contract without owning
deployment machinery.

Run locally:

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
docker compose up --build
curl --fail http://127.0.0.1:8080/health
```

`compose.yaml` is local-development convenience only. Production intent is the
single `.infra-k8s/app.yaml`, selected at an exact commit by a fleet-owned
`AppRelease` in the separate `infra-k8s` repository.

## infra-k8s development session

The same App contract declares the two safe inner-loop mappings used by the
framework: Python source and ordinary JSON configuration. From the root of
this checkout, with an eligible development Target owned by the cockpit repo:

```sh
infra-k8s dev start \
  --app .infra-k8s/app.yaml \
  --target /absolute/path/to/infra-k8s/examples/development/minikube.target.yaml \
  --session my-reference-session
```

The command prints a loopback URL when the isolated session is ready and stays
attached while source changes are synchronized or rebuilt. In another shell:

```sh
infra-k8s dev status \
  --target /absolute/path/to/infra-k8s/examples/development/minikube.target.yaml \
  --session my-reference-session
infra-k8s dev stop \
  --target /absolute/path/to/infra-k8s/examples/development/minikube.target.yaml \
  --session my-reference-session
```

This development lane accepts a dirty checkout. It cannot publish or promote
anything: persistent delivery still requires a committed source revision and
the fleet repository's Git-to-Flux path.
