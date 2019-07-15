# Resource Principal function for returning the compartments of a User's Tenancy.

This function uses Resource Principles to securely receive information about the user's information from OCI and returns a list of all compartments within the tenancy regardless of region.

  Uses the [OCI Python SDK](https://oracle-cloud-infrastructure-python-sdk.readthedocs.io/en/latest/index.html) to create a client that receive user information when called in the OCI or a valid config file exists.

  As you make your way through this tutorial, look out for this icon. ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-list-compartments/master/images/userinput.png) Whenever you see it, it's time for you to perform an action.


Pre-requisites:
---------------
  1. Start by making sure all of your policies are correct from this [guide](https://preview.oci.oraclecorp.com/iaas/Content/Functions/Tasks/functionscreatingpolicies.htm?tocpath=Services%7CFunctions%7CPreparing%20for%20Oracle%20Functions%7CConfiguring%20Your%20Tenancy%20for%20Function%20Development%7C_____4)

  2. Download [rp.py](https://github.com/arodri202/oci-rp-list-compartments/blob/master/rp.py) and move it into your working directory.

  3. Have [Fn CLI setup with Oracle Functions](https://preview.oci.oraclecorp.com/iaas/Content/Functions/Tasks/functionsconfiguringclient.htm?tocpath=Services%7CFunctions%7CPreparing%20for%20Oracle%20Functions%7CConfiguring%20Your%20Client%20Environment%20for%20Function%20Development%7C_____0)

### Switch to the correct context
  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-list-compartments/master/images/userinput.png)
  ```
  fn use context <your context name>
  ```
  Check using
  ```
  fn ls apps
  ```

### (Optional) Have a config file in the ~/.oci directory
  If you would like to call the function from the command line you will need a valid config file.

  If you do not have one, go [here](https://preview.oci.oraclecorp.com/iaas/Content/Functions/Tasks/functionsconfigureocicli.htm?tocpath=Services%7CFunctions%7CPreparing%20for%20Oracle%20Functions%7CConfiguring%20Your%20Client%20Environment%20for%20Function%20Development%7C_____2)

Create application
------------------
  Get the python boilerplate by running:

  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-list-compartments/master/images/userinput.png)
  ```
  fn init --runtime python <function-name>
  ```
  e.g.
  ```
  fn init --runtime python list-compartments
  ```
  Enter the directory, create a new `__init__.py` file so the directory can be recognized as a package by Python.

  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-list-compartments/master/images/userinput.png)
  ```
  cd list-compartments
  touch __init__.py
  ```

### Create an Application that is connected to Oracle Functions
  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-list-compartments/master/images/userinput.png)
  ```
  fn create app <app-name> --annotation oracle.com/oci/subnetIds='["<subnet-ocid>"]'
  ```
  You can find the subnet-ocid by logging on to [cloud.oracle.com](https://cloud.oracle.com/en_US/sign-in), navigating to Core Infrastructure > Networking > Virtual Cloud Networks. Make sure you are in the correct Region and Compartment, click on your VNC and select the subnet you wish to use.

  e.g.
  ```
  fn create app resource-principal --annotation oracle.com/oci/subnetIds='["ocid1.subnet.oc1.phx.aaaaaaaacnh..."]'
  ```

Writing the Function
------------------
### Requirements
  Update your requirements.txt file to contain the following:

  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-list-compartments/master/images/userinput.png)
  ```
  fdk
  oci-cli
  ```

### Open func.py
  Update the imports so that you contain the following.

  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-list-compartments/master/images/userinput.png)
  ```python
  import io
  import json
  import sys

  from fdk import response
  import oci.identity

  sys.path.append(".")
  import rp
  ```

  By calling `sys.path.append(".")` the Python interpreter is able to import the rp.py Python module in your directory that you downloaded earlier.

### The Handler method
  This is what is called when the function is invoked by Oracle Functions, delete what is given from the boilerplate and update it to contain the following:

  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-list-compartments/master/images/userinput.png)
  ```python
  def handler(ctx, data: io.BytesIO=None):
      provider = rp.ResourcePrincipalProvider()
      resp = do(provider)
      return response.Response(
          ctx, response_data=json.dumps(resp),
          headers={"Content-Type": "application/json"}
      )
  ```

### The do method
  Create the following method.

  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-list-compartments/master/images/userinput.png)
  ```python
  def do(provider):
  ```
  This is where we'll put the bulk of our code that will connect to OCI and return the list of compartments in our tenancy.

  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-list-compartments/master/images/userinput.png)
  ```python
    client = oci.identity.IdentityClient(provider.config, signer=provider.signer)
    # OCI API for managing users, groups, compartments, and policies.

    try:
        # Returns a list of all compartments and subcompartments in the tenancy (root compartment)
        compartments = client.list_compartments(provider.tenancy, compartment_id_in_subtree=True, access_level='ANY')

        # Create a list that holds a list of the compartments id and name next to each other.
        compartments = [[c.id, c.name] for c in compartments.data]
    except Exception as e:
        compartments = str(e)

    resp = {
             "compartments": compartments,
            }

    return resp
  ```
  Here we are creating an [IdentityClient](https://oracle-cloud-infrastructure-python-sdk.readthedocs.io/en/latest/api/identity/client/oci.identity.IdentityClient.html) from the [OCI Python SDK](https://oracle-cloud-infrastructure-python-sdk.readthedocs.io/en/latest/index.html), which allows us to connect to OCI with the provider's data we get from Resource Principles and it allows us to make a call to identity services for information on our compartments.

### Command Line Usage
  If you want to be able to invoke this function from the command line, copy and paste this at the bottom of your code.

  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-list-compartments/master/images/userinput.png)
  ```python
  def main():
      # If run from the command-line, fake up the provider by using stock user credentials
      provider = rp.MockResourcePrincipalProvider()
      resp = do(provider)
      print((resp))
      print(json.dumps(resp))


  if __name__ == '__main__':
      main()

  ```
Test
----
### Deploy the function

  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-list-compartments/master/images/userinput.png)
  ```
  fn -v deploy --app <your app name>
  ```

  e.g.

  ```
  fn -v deploy --app resource-principles
  ```

### Invoke the function

  ![user input icon](https://raw.githubusercontent.com/arodri202/oci-rp-list-compartments/master/images/userinput.png)
  ```
  fn invoke <your app name> <your function name>
  ```

  e.g.

  ```
  fn invoke resource-principles list-compartments
  ```
  Upon success, you should see all of the compartments in your tenancy appear in your terminal.
