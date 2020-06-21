# Makefile for igreja
# Builds, tests, lints and runs code coverage for gameserverproxy.
# Defaults to the CI target, which mimics the behavior of Gitlabs' CI pipeline.

# Include .env if the file exists
-include .env
export $(shell sed 's/=.*//' ".env" 2> /dev/null)

# Install Prototool
SHELL := /bin/bash -o pipefail
VENV ?= ixu

# Docker setup
DOCKER_IMAGE_REGISTRY ?= luanguimaraesla/ixu
DOCKER_IMAGE_NAME ?= ixu
DOCKER_IMAGE_TAG ?= dev


docker-build:
	@docker build -t ${DOCKER_IMAGE_REGISTRY}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG} . -f Dockerfile

docker-push:
	@docker push ${DOCKER_IMAGE_REGISTRY}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}

docker-release: docker-build docker-push

setup:
	@python3 setup.py develop

install:
	@python3 -m pip install setuptools
	@python3 setup.py clean
	@python3 setup.py bdist_wheel
	@python3 setup.py install

run:
	@echo "  > running server"
	@python3 -m ixu server up

test:
	@echo "  > running tests"

configure:
	@echo "  > configuring development environment"
	@source ~/.venv/${VENV}/bin/activate
