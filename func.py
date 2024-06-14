import oci
import json

def handler(ctx, data: str = None):
    config = oci.config.from_file()

    organizations_client = oci.organizations.OrganizationsClient(config)

    body = json.loads(data)
    
    create_child_tenancy_details = oci.organizations.models.CreateChildTenancyDetails(
        compartment_id=body["compartment_id"],
        tenancy_name=body["tenancy_name"],
        tenancy_description=body["tenancy_description"],
        home_region=body["home_region"],
        admin_email=body["admin_email"]
    )

    response = organizations_client.create_child_tenancy(create_child_tenancy_details)
    
    return json.dumps({"tenancy_id": response.data.tenancy_id})
