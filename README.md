# Avatar microservice
A microservice to store user profile pictures (avatars) corresponding to Firebase IdTokens in AWS S3.

## Environment variables
* **FIREBASE_PROJECT_ID** The [Firebase project id](https://firebase.google.com/docs/projects/learn-more#project-id)
* **S3_BUCKET** The name of the AWS S3 bucket to store the images

## Run locally
1. Install requirements with `pip3 install -r requirements.txt`
2. Add .env file to root of project directory
3. ([Configure aws cli](https://docs.aws.amazon.com/cli/latest/reference/configure/) to obtain credentials)
4. Run app with `uvicorn --env-file ./.env --app-dir ./app/ main:app`
5. Explore API at http://127.0.0.1:8000

## Deployment
The application can be run inside a docker container with  
`docker build -t avatar .`  
`docker run -d --env-file ./.env --name avatar -p 80:80 avatar`

## Default avatar
[Enable website hosting](https://docs.aws.amazon.com/AmazonS3/latest/userguide/EnableWebsiteHosting.html) on the S3 bucket, upload a default avatar and configure the following redirect:
```
[
    {
        "Condition": {
            "HttpErrorCodeReturnedEquals": "403",
            "KeyPrefixEquals": "avatars/"
        },
        "Redirect": {
            "ReplaceKeyWith": "placeholder.jpg"
        }
    }
]
```