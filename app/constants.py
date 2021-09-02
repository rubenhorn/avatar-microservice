# HTTP
HTTP_STATUS_BAD_REQUEST = 400
HTTP_STATUS_UNAUTHORIZED = 401
HTTP_STATUS_FORBIDDEN = 403
HTTP_STATUS_NOT_FOUND = 404
HTTP_STATUS_LENGTH_REQUIRED = 411
HTTP_STATUS_REQUEST_ENTITY_TOO_LARGE = 413
HTTP_STATUS_UNSUPPORTED_MEDIA_TYPE = 415

# FastAPI
PATH_AVATAR = '/avatar'

# AWS S3
S3_KEY_PREFIX = 'avatars/'

# Application constants
MIME_JPEG = 'image/jpeg'

# Application parameters
# Refer to https://blog.hootsuite.com/social-media-image-sizes-guide
MIN_ASPECT_RATIO = 1
MAX_ASPECT_RATIO = 1
MAX_IMAGE_WIDTH = 512
MIN_IMAGE_WIDTH = 256
MAX_FILE_SIZE_KB = 500
OUTPUT_QUALITY = 30
MODERATION_CONFIDENCE_THRESHOLD = 0.9
# Refer to https://docs.aws.amazon.com/rekognition/latest/dg/moderation.html#moderation-api
INACCEPTABLE_CONTENT_LABELS = ['Explicit Nudity',
                               'Violence', 'Visually Disturbing', 'Hate Symbols']
