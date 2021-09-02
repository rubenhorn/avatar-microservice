import boto3
from constants import MODERATION_CONFIDENCE_THRESHOLD, INACCEPTABLE_CONTENT_LABELS


class ContentException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
    pass


class Moderation:
    def __init__(self, ) -> None:
        self.rekognition = boto3.client('rekognition')

    def check_image(self, image_bytes: bytes) -> None:
        response = self.rekognition.detect_moderation_labels(
            Image={
                'Bytes': image_bytes
            }
        )
        confident_labels = []
        for label in [label for label in response['ModerationLabels']
                      if label['Confidence'] >= MODERATION_CONFIDENCE_THRESHOLD]:
            if label['Name'] not in confident_labels:
                confident_labels.append(label['Name'])
            if label['Name'] not in confident_labels:
                confident_labels.append(label['Name'])
        inacceptable_labels = [
            label for label in confident_labels if label in INACCEPTABLE_CONTENT_LABELS]
        if(len(inacceptable_labels) > 0):
            raise ContentException(
                "Image rejected due to {}".format(', '.join(inacceptable_labels)))
