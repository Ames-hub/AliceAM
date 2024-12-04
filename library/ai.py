from transformers import AutoModelForImageClassification, ViTImageProcessor, pipeline
from library.storage import PostgreSQL
from library.variables import logging
from io import BytesIO
from PIL import Image
import imagehash
import requests
import torch

# Load beforehand
offensive_classifier = pipeline("text-classification", model="Falconsai/offensive_speech_detection")
nsfw_scan_model = AutoModelForImageClassification.from_pretrained("Falconsai/nsfw_image_detection")
nsfw_scan_processor = ViTImageProcessor.from_pretrained('Falconsai/nsfw_image_detection')

class AliceIntel:
    class NsfwImagePredictor:
        @staticmethod
        def predict(img_url, return_img_from_url=False, check_history=True):
            """
            Predict the content of an image.
            :param img_url: The URL of the image to predict.
            :param return_img_from_url: Whether to return the image or not.
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
                    inputs = nsfw_scan_processor(images=img, return_tensors="pt")
                except ValueError as err:
                    logging.error(f"Invalid Image (SRC: {img_url}):", exc_info=err)
                    print("An error occurred while processing an image. Please check logs.")
                    return "normal"  # Hide the error from the user to prevent an exploit being found.
                outputs = nsfw_scan_model(**inputs)
                logits = outputs.logits

            predicted_label = logits.argmax(-1).item()
            result = nsfw_scan_model.config.id2label[predicted_label]
            if return_img_from_url:
                return {'result': result, 'img': img}
            else:
                return result

    class InsultPredictor:
        @staticmethod
        def predict(text, consider_trust: tuple = (False, None)):
            """
            Predict the offensiveness of a text.
            :param text: The text to predict.
            :param consider_trust: Whether to consider the trust of the user or not. (bool, uuid)
            :return: The prediction of the text. (dict, see below)

            The dictionary returned will contain the following
            {
                'label': 'OFFENSIVE' or 'SAFE',
                'score': float,
                'trust_score': float
            }
            """
            result = offensive_classifier(text)[0]
            if consider_trust[0]:
                return AliceIntel.InsultPredictor.consider_trust(result, consider_trust[1])

            # I noticed a very weird bug with this AI. With certain messages, even if they're happy like "You look quite happy! :3"
            # It will still return "OFFENSIVE" with a score of 0.99999... . I'm not sure why this happens.
            # But since testing shows most actually offensive messages return about 0.9996-0.99998, we're going to work around it.

            if result['score'] > 0.99999:
                result['label'] = 'SAFE'

            return result

        @staticmethod
        def consider_trust(predicted_result, uuid):
            """
            Consider the trust of the prediction.
            :param predicted_result: The result of the prediction.
            :param uuid: The UUID of the user to consider the trust of.

            :return: The trust of the prediction.
            """
            trust = PostgreSQL.users(uuid).get_trust() # Value between 0-100
            score = predicted_result['score']
            total_infractions = PostgreSQL.users(uuid).get_infraction_count()

            # Uses math with the trust to determine the final score.
            # The lower the score, the more offensive it is likely to be.
            # Example: 0.9 (score) * 0.5 (trust) = 0.45
            final_score = score * (trust / 100)

            # If the user has more than 7 infractions in the last 2 weeks, the trust is reduced.
            if total_infractions > 7:
                final_score *= 0.9

            # Set the final score
            predicted_result['trust_score'] = final_score

            return predicted_result