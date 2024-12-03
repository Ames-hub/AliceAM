from transformers import AutoModelForImageClassification, ViTImageProcessor
from library.storage import PostgreSQL
from library.variables import logging
from io import BytesIO
from PIL import Image
import imagehash
import requests
import torch


class AliceIntel:
    def __init__(self):
        self.model = AutoModelForImageClassification.from_pretrained("Falconsai/nsfw_image_detection")
        self.processor = ViTImageProcessor.from_pretrained('Falconsai/nsfw_image_detection')

    def predict_image(self, img_url, return_img=False, check_history=True):
        """
        Predict the content of an image.
        :param img_url: The URL of the image to predict.
        :param return_img: Whether to return the image or not.
        :param check_history: Whether to check if the image has been scanned before and return the past result.
        :return: The prediction of the image. If return_img is True, it will return the image as well in a dictionary.
        """
        response = requests.get(img_url)
        img = Image.open(BytesIO(response.content))

        if check_history:
            img_hash = str(imagehash.average_hash(img))
            # Check if the image hash is in the DB and return the result if it is. (resource saver)
            result = PostgreSQL().img_scan_history(img_hash)
            if result is not None:
                bytes_data = result['bytedata']
                case_id = result['case_id']
                # If it's in the DB, it's NSFW. SFW images are not stored in the DB.
                return {'result': 'nsfw-history', 'img_bytes': bytes_data, 'case_id': case_id}

        with torch.no_grad():
            try:
                inputs = self.processor(images=img, return_tensors="pt")
            except ValueError as err:
                logging.error(f"Invalid Image (SRC: {img_url}):", exc_info=err)
                print("An error occurred while processing an image. Please check logs.")
                return "normal"  # Hide the error from the user to prevent an exploit being found.
            outputs = self.model(**inputs)
            logits = outputs.logits

        predicted_label = logits.argmax(-1).item()
        result = self.model.config.id2label[predicted_label]
        if return_img:
            return {'result': result, 'img': img}
        else:
            return result