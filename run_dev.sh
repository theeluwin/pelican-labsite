docker build --file ./Dockerfile.dev --tag pelican-labsite-dev .
docker run \
    --interactive \
    --tty \
    --init \
    --rm \
    --publish 8000:8000 \
    --volume ./src:/src \
    --name pelican-labsite-dev-container \
    pelican-labsite-dev
