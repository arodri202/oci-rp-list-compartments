import io
import json
import sys
import importlib
from fdk import response

import oci.identity


def handler(ctx, data: io.BytesIO=None):
    provider = None
    resp = do(provider)
    return response.Response(
        ctx, response_data=json.dumps(resp),
        headers={"Content-Type": "application/json"}
    )


def do(provider):
    compartments = None
    resp = {
             "compartments": compartments,
            }

    return resp

def main():
    # If run from the command-line, fake up the provider by using stock user credentials
    provider = None
    resp = do(provider)
    print((resp))
    print(json.dumps(resp))


if __name__ == '__main__':
    main()
