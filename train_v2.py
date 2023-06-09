from architecture import * 
import os 
import cv2
import mtcnn
import json
import numpy as np 
from sklearn.preprocessing import Normalizer

######pathsandvairables#########
face_data = "static/images/"
required_shape = (160, 160)
face_encoder = InceptionResNetV2()
path = "weights/facenet_keras_weights.h5"
face_encoder.load_weights(path)
face_detector = cv2.FaceDetectorYN.create(
        model="weights/face_detection_yunet_2022mar.onnx",  # yunet.onnx face_detection_yunet_2022mar
        config='',
        input_size=(480, 640),
        score_threshold=0.65,
        nms_threshold=0.35,
        top_k=5000,
        backend_id=3,
        target_id=0
    )
encodes = []
encoding_dict = dict()
encode_name = ""
l2_normalizer = Normalizer('l2')
###############################


def normalize(img):
    mean, std = img.mean(), img.std()
    return (img - mean) / std


def face_encoding(image_names):
    global face_data, required_shape, face_encoder, face_detector, encodes, encoding_dict, encode_name, l2_normalizer

    for name in image_names:
        image_path = os.path.join(face_data, name)
        img_BGR = cv2.imread(image_path)
        img_RGB = cv2.cvtColor(img_BGR, cv2.COLOR_BGR2RGB)

        face_detector.setInputSize((img_RGB.shape[1], img_RGB.shape[0]))
        _, face = face_detector.detect(img_RGB)
        face = face[0][:-1].astype(np.int32)

        x1, y1, width, height = face[:4]
        x1, y1 = abs(x1), abs(y1)
        x2, y2 = x1+width, y1+height
        face = img_RGB[y1:y2, x1:x2]
        # cv2.imshow("dnm", cv2.cvtColor(face, cv2.COLOR_RGB2BGR))
        # cv2.waitKey(0)

        face = normalize(face)
        if (face.shape[0] > face.shape[1]):
            scale = face.shape[0] / 160
            width = int(face.shape[1] / scale)
            face = cv2.resize(face, (width, 160))
            padding = int((160 - face.shape[1]) / 2)

            if (160 - face.shape[1]) % 2 == 0:
                face = cv2.copyMakeBorder(face, 0, 0, padding, padding, cv2.BORDER_CONSTANT, value=(0, 0, 0))
            else:
                face = cv2.copyMakeBorder(face, 0, 0, padding, padding + 1, cv2.BORDER_CONSTANT, value=(0, 0, 0))

        else:
            scale = face.shape[1] / 160
            height = int(face.shape[0] / scale)
            face = cv2.resize(face, (160, height))
            padding = int((160 - face.shape[0]) / 2)

            if (160 - face.shape[0]) % 2 == 0:
                face = cv2.copyMakeBorder(face, padding, padding, 0, 0, cv2.BORDER_CONSTANT, value=(0, 0, 0))
            else:
                face = cv2.copyMakeBorder(face, padding, padding + 1, 0, 0, cv2.BORDER_CONSTANT, value=(0, 0, 0))

        face_d = np.expand_dims(face, axis=0)
        encode = face_encoder.predict(face_d)[0]
        encodes.append(encode)

        if encodes:
            #encode = np.sum(encodes, axis=0 )
            encode = l2_normalizer.transform(np.expand_dims(encode, axis=0))[0]
            encoding_dict[name] = encode


    for name in image_names:
        encoding_dict[name] = list(encoding_dict[name])
        encode_name += name + "_"


    with open(f"encodings/{encode_name}.json", 'w') as f:
        json.dump(str(encoding_dict), f)

    encodes.clear()
    encoding_dict.clear()
    encode_name = ""






