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
