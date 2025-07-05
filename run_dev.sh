docker build -f ./Dockerfile.dev -t pelican-labsite-dev .
docker run \
    -it \
    --rm \
    --init \
    --publish 8000:8000 \
    --volume ./src:/src \
    --name pelican-labsite-dev-container \
    pelican-labsite-dev
