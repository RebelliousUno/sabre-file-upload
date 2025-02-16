
# FastAPI + CDK
## Endpoints
- /uploads 
  - given a user-id in the header, returns a list of the user's shortened urls
- /upload 
  - given a file and user-id uploads a file to S3 and returns the shortened slug for that file
- /shorten
  - given a url and user-id shortens a url and returns the shortened slug

## Future expansions

- Authentication for the APIs so that user-id isn't just given in the header. Authentication could put this into a JWT
- Using Signed URLs rather than the S3 bucket being open to public read.
- Allow users the delete files/urls
- Allow users to set expiry on files/urls
- Scanning of files going into S3 to detect malware/other harmful material
- File size limits per user/per request



# Welcome to your CDK Python project!

This is a blank project for CDK development with Python.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
