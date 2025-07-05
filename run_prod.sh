docker build -f ./Dockerfile.prod -t pelican-labsite .
docker stop pelican-labsite-container 2>/dev/null || true
docker rm pelican-labsite-container 2>/dev/null || true
docker run \
    -d \
    --init \
    --publish 80:80 \
    --volume ./shared:/shared \
    --name pelican-labsite-container \
    pelican-labsite
