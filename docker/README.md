# CI/CD Pipeline for Docker Image Deployment

This project uses a CI/CD pipeline to automate the creation, testing, static analysis, and deployment of Docker images for the geocontrib application. The pipeline is designed to build and push Docker images to a repository, which are then deployed to the client site through a deployment script in a separate Git repository https://git.neogeo.fr/geocontrib/geocontrib-docker.

The docker-compose files in this repository 

## Pipeline Stages
The pipeline consists of the following stages:

1. **Test**: Executes unit tests to validate the application code.  
2. **Static** Analysis: Performs a static code analysis using SonarQube to check for code quality issues.
3. **Build**: Builds Docker images for different branches or tags.
4. **Deploy**: Triggers a deployment for the develop branch using a remote deployment script.

## Variables
**GIT_DEPTH**: Set to 0 to ensure the full Git history is available during the pipeline execution.  
**POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD**: Environment variables for configuring the PostgreSQL database used in tests.  
**POSTGRES_HOST_AUTH_METHOD**: Set to trust to allow simplified authentication during the CI process.

## Stages in Detail
### Build Testing Docker Image
This job is triggered on the `develop` branch. It builds a Docker image with the tag `testing` and pushes it to the Docker registry.

```yaml
stage: build
only: develop
tags: build_docker
script:
  - docker-compose build geocontrib
  - docker-compose push geocontrib
  - echo "Docker image neogeo/geocontrib:testing delivered"
```
### Deploy Testing Docker Image
After building the testing Docker image, this job triggers the deployment pipeline for the `develop` branch.

```yaml
stage: deploy
only: develop
tags: build
script:
  - curl -X POST -F token=$TRIGGER_TOKEN -F ref=main https://git.neogeo.fr/api/v4/projects/226/trigger/pipeline
```

### Build Stable Docker Image
This job builds the Docker image with the `latest` tag for the `master` branch.

```yaml
stage: build
only: master
tags: build_docker
script:
  - docker-compose build geocontrib
  - docker-compose push geocontrib
  - echo "Docker image neogeo/geocontrib:latest delivered"
```
### Build Tagged Docker Image
When a tag is pushed, this job builds and pushes the Docker image using the tag as the version.

```yaml
stage: build
only: tags
tags: build_docker
script:
  - docker-compose build geocontrib
  - docker-compose push geocontrib
  - echo "Docker image neogeo/geocontrib:$CI_COMMIT_TAG delivered"
```

### SonarQube Static Analysis
This stage runs static analysis on the codebase using SonarQube and provides a report of code quality.

```yaml
stage: Static analysis
image: sonarsource/sonar-scanner-cli:latest
script:
  - sonar-scanner -Dsonar.qualitygate.wait=true -Dsonar.projectKey=id-$CI_PROJECT_ID
```

### Test
The test stage uses `pytest` to run unit tests on the application.

```yaml
stage: test
image: python:3.7
services:
  - redis
  - postgis/postgis
script:
  - pytest --cov .
```

## Deployment Flow
1. Push to develop branch: Triggers the build and deploy process for the testing environment.
2. Push to master branch: Builds the stable image with the latest tag.
3. Tag creation: Builds a versioned Docker image corresponding to the Git tag.

## Deployment in a Separate Git Repository
The deployment is handled by a separate Git repository that contains the `docker-compose.yml` file used for production deployment. This `docker-compose.yml` file orchestrates the running of the application containers in the production environment, ensuring that the application is correctly configured and services like the database are properly linked.

Additionally, the same directory in the separate Git repository contains a `docker-compose` file that is used only for local testing. This local `docker-compose.yml` is useful for quickly setting up a clean PostgreSQL database dedicated to `geocontrib` on your local machine, without needing to install PostgreSQL manually. It's ideal for running tests or spinning up the application in a local environment for development purposes.

## Artifacts
Test and coverage reports are saved as artifacts for future reference and stored for one week.