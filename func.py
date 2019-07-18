# Copyright (c) 2016, 2018, Oracle and/or its affiliates.  All rights reserved.
import io
import json

from fdk import response
import oci.identity

def handler(ctx, data: io.BytesIO=None):
    signer = oci.auth.signers.get_resource_principals_signer()
    resp = do(signer)
    return response.Response(
        ctx, response_data=json.dumps(resp),
        headers={"Content-Type": "application/json"}
    )


def do(signer):
    # List compartments --------------------------------------------------------------------------------
    client = oci.identity.IdentityClient(config={}, signer=signer)
    # OCI API for managing users, groups, compartments, and policies.

    try:
        # Returns a list of all compartments and subcompartments in the tenancy (root compartment)
        compartments = client.list_compartments(signer.tenancy_id, compartment_id_in_subtree=True, access_level='ANY')

        # Create a list that holds a list of the compartments id and name next to each other.
        compartments = [[c.id, c.name] for c in compartments.data]
    except Exception as e:
        compartments = str(e)

    resp = {
             "compartments": compartments,
            }

    return resp
