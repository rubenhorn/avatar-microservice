import re
from starlette.requests import Request
from auth import FirebaseAuth, AuthException
import boto3
from constants import *
from fastapi import FastAPI, File, UploadFile
from fastapi.param_functions import Depends
from fastapi.security import HTTPBearer
import io
from moderation import ContentException, Moderation
import os
from PIL import Image
from starlette.responses import JSONResponse, Response


app = FastAPI()
s3 = boto3.client('s3')
bucket = os.environ.get('S3_BUCKET')
assert(bucket is not None and bucket != '')
security = HTTPBearer()
firebaseAuth = FirebaseAuth(os.environ.get('FIREBASE_PROJECT_ID'))
moderation = Moderation()


class InputFileException(Exception):
    def __init__(self, message) -> None:
        self.message = message
    pass


@app.exception_handler(AuthException)
async def file_exception_handler(request, exc):
    return JSONResponse(
        status_code=HTTP_STATUS_UNAUTHORIZED,
        headers={'WWW-Authenticate': 'Bearer'},
        content={'message': 'Could not authenticate user'},
    )


@app.exception_handler(InputFileException)
async def file_exception_handler(request, exc):
    return JSONResponse(
        status_code=HTTP_STATUS_BAD_REQUEST,
        content={'message': exc.message},
    )


@app.exception_handler(ContentException)
async def file_exception_handler(request, exc):
    return JSONResponse(
        status_code=HTTP_STATUS_BAD_REQUEST,
        content={'message': exc.message},
    )


def _get_avatar_file_name(user_id: str) -> str:
    return S3_KEY_PREFIX + user_id + '.jpg'


@app.get(PATH_AVATAR)
def fetch_avatar(httpCreds=Depends(security)):
    filename = _get_avatar_file_name(
        firebaseAuth.get_user_id_from_id_token(httpCreds.credentials))
    try:
        s3.head_object(Bucket=bucket, Key=filename)
        url = f'https://{bucket}.s3.amazonaws.com/{filename}'
        return {'message': f'Avatar hosted at {url}', 'photoURL': url}
    except:
        return JSONResponse(
            status_code=HTTP_STATUS_NOT_FOUND,
            content={'message': 'Could not find avatar'},
        )


@app.post(PATH_AVATAR)
async def upload_avater(request: Request, uploadFile: UploadFile = File(..., media_type=MIME_JPEG), httpCreds=Depends(security)):
    filename = _get_avatar_file_name(
        firebaseAuth.get_user_id_from_id_token(httpCreds.credentials))
    if(uploadFile.content_type != MIME_JPEG):
        return JSONResponse(
            status_code=HTTP_STATUS_UNSUPPORTED_MEDIA_TYPE,
            content={'message': f'Invalid file type (Expected { MIME_JPEG })'},
        )
    if 'content-length' not in request.headers:
        return JSONResponse(
            status_code=HTTP_STATUS_LENGTH_REQUIRED,
            content={'message': 'Content-Length header required'},
        )
    content_length = int(request.headers['content-length'])
    max_file_size = MAX_FILE_SIZE_KB * 1024
    if content_length >= max_file_size:
        return JSONResponse(
            status_code=HTTP_STATUS_REQUEST_ENTITY_TOO_LARGE,
            content={'message': f'File must be less than { max_file_size } bytes'},
        )
    input_image_bytes = await uploadFile.read(content_length)
    try:
        image = Image.open(io.BytesIO(input_image_bytes))
    except:
        raise InputFileException('Could not load image')
    if(
        (image.width / image.height < MIN_ASPECT_RATIO) or
        (image.width / image.height > MAX_ASPECT_RATIO) or
        (image.width < MIN_IMAGE_WIDTH) or
        (image.width > MAX_IMAGE_WIDTH)
    ):
        raise InputFileException('Invalid image size')
    image.thumbnail((MIN_IMAGE_WIDTH, MIN_IMAGE_WIDTH), Image.ANTIALIAS)
    output_image_bytes = io.BytesIO()
    image.save(output_image_bytes, format='JPEG',
               optimize=True, quality=OUTPUT_QUALITY)
    output_image_bytes.seek(0)
    moderation.check_image(output_image_bytes.read())
    output_image_bytes.seek(0)
    s3.put_object(
        Bucket=bucket,
        Key=filename,
        Body=output_image_bytes,
        ContentType=MIME_JPEG,
        ContentDisposition='inline',
        ACL='public-read'
    )
    url = f'https://{bucket}.s3.amazonaws.com/{filename}'
    return {'message': f'Uploaded avatar to {url}', 'photoURL': url}


@app.delete(PATH_AVATAR)
def delete_avatar(httpCreds=Depends(security)):
    filename = _get_avatar_file_name(
        firebaseAuth.get_user_id_from_id_token(httpCreds.credentials))
    s3.delete_object(
        Bucket=bucket,
        Key=filename
    )
    return {'message': 'Deleted avatar'}
