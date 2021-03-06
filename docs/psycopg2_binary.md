# psycopg2 binary

`psycopg2` requires additional packaging requirements to be deployed via Chalice demonstrated in
[this post](https://github.com/jamesls/chalice/blob/5a5fb0d83132d3c9e2e8d71aa9fac80fbecfec7f/docs/source/topics/packaging.rst#psycopg2-example).
We can get around building our own binaries by using `psycopg2_binary`.

## Troubleshooting

If you run into issues using the prebuilt packages, you may need to follow the repo instructions to compile the binary
from scratch. I recommend compiling the binary in a Docker container using the `lambci/lambda:build-python3.6` image
([source](https://hub.docker.com/r/lambci/lambda/)) in order to replicate the Lambda environment.
