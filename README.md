# IXU

### Running server locally

We recommend you to create a new python virtual environment before running the following commands

```bash
$ make setup
$ make run
```

Also, you can run with docker by building or downloading the image before, then running

```bash
docker run --rm --name ixu -p 8080:8080 luanguimaraesla/ixu:latest
```

### Running the whole stack

For a better visualization of the data collected we have a `docker-compose.yml` file that starts Prometheus and Grafana along with Ixu server. You should create an `.env` file with the necessary confiration and then run

```bash
docker-compose up --build
```

Ixu server will run in the port `8000`, Prometheus in `9090`, and Grafana in `3000`. Grafana's testing username is `admin` and the password is `ixu`.

### Building docker image

To create a docker image run
```bash
$ make docker-build
```

To push this image to the registry
```bash
$ make docker-push
```

### Running tests

```bash
make test
```

### Configuration

You should define the following environment variables

* `IXU_GITLAB_URL`: Gitlab URL (default "http://gitlab.com")
* `IXU_GITLAB_TOKEN`: User token to access the Gitlab API
* `IXU_HOST`: Host binding (default "0.0.0.0")
* `IXU_PORT`: Server port (default 8080)
* `IXU_GITLAB_PROJECT_ID`: Project ID from the Gitlab project where IXU shoul extract information
