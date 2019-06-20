import io
import json
import sys
import importlib
from fdk import response

import oci.identity

sys.path.append(".")
import rp

def handler(ctx, data: io.BytesIO=None):
    provider = rp.ResourcePrincipalProvider() # initialized provider here
    resp = do(provider)
    return response.Response(
        ctx, response_data=json.dumps(resp),
        headers={"Content-Type": "application/json"}
    )


def do(provider):
    # List compartments --------------------------------------------------------------------------------
    client = oci.identity.IdentityClient(provider.config, signer=provider.signer)
    # OCI API for managing users, groups, compartments, and policies.

    try:
        # Returns a list of all compartments and subcompartments in the tenancy (root compartment)
        compartments = client.list_compartments(provider.tenancy, compartment_id_in_subtree=True, access_level='ANY')

        # Create a list that holds a list of the compartments id and name next to each other.
        # i.e. [ [1234, root], [5678, child]]
        compartments = [[c.id, c.name] for c in compartments.data]
    except Exception as e:
        compartments = str(e)

    resp = {
             "compartments": compartments,
            }

    return resp

def main():
    # If run from the command-line, fake up the provider by using stock user credentials
    provider = rp.MockResourcePrincipalProvider()
    resp = do(provider)
    print((resp))
    print(json.dumps(resp))


if __name__ == '__main__':
    main()
