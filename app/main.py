from auth import FirebaseAuth, AuthException
import boto3
from constants import *
from fastapi import FastAPI, File, UploadFile
from fastapi.param_functions import Depends
from fastapi.security import HTTPBearer
import io
import os
from PIL import Image
from starlette.responses import JSONResponse


app = FastAPI()
s3 = boto3.client('s3')
bucket = os.environ.get('S3_BUCKET')
assert(bucket is not None and bucket != '')
security = HTTPBearer()
firebaseAuth = FirebaseAuth(os.environ.get('FIREBASE_PROJECT_ID'))


class FileException(Exception):
    def __init__(self, message) -> None:
        self.message = message
    pass


@app.exception_handler(FileException)
async def file_exception_handler(request, exc):
    return JSONResponse(
        status_code=HTTP_STATUS_BAD_REQUEST,
        content={'message': exc.message},
    )


@app.exception_handler(AuthException)
async def file_exception_handler(request, exc):
    return JSONResponse(
        status_code=HTTP_STATUS_UNAUTHORIZED,
        headers={'WWW-Authenticate': 'Bearer'},
        content={'message': 'Could not authenticate user'},
    )


def _get_avatar_file_name(user_id):
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
async def upload_avater(uploadFile: UploadFile = File(..., media_type=MIME_JPEG), httpCreds=Depends(security)):
    filename = _get_avatar_file_name(
        firebaseAuth.get_user_id_from_id_token(httpCreds.credentials))
    if(uploadFile.content_type != MIME_JPEG):
        raise FileException(f'Invalid file type (Expected { MIME_JPEG })')
    input_image_bytes = await uploadFile.read(MAX_FILE_SIZE_KB * 1024)
    try:
        image = Image.open(io.BytesIO(input_image_bytes))
    except:
        raise FileException('Could not load image')
    if(
        (image.width / image.height < MIN_ASPECT_RATIO) or
        (image.width / image.height > MAX_ASPECT_RATIO) or
        (image.width < MIN_IMAGE_WIDTH) or
        (image.width > MAX_IMAGE_WIDTH)
    ):
        raise FileException('Invalid image size')
    image.thumbnail((MIN_IMAGE_WIDTH, MIN_IMAGE_WIDTH), Image.ANTIALIAS)
    output_image_bytes = io.BytesIO()
    image.save(output_image_bytes, format='JPEG',
               optimize=True, quality=OUTPUT_QUALITY)
    output_image_bytes.seek(0)

    # TODO check if image content is safe

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
