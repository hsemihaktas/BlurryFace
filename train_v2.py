from architecture import * 
import os 
import cv2
import mtcnn
import json
import numpy as np 
from sklearn.preprocessing import Normalizer

######pathsandvairables#########
face_data = "Faces/"
required_shape = (160, 160)
face_encoder = InceptionResNetV2()
path = "facenet_keras_weights.h5"
face_encoder.load_weights(path)
face_detector = mtcnn.MTCNN()
encodes = []
encoding_dict = dict()
l2_normalizer = Normalizer('l2')
###############################


def normalize(img):
    mean, std = img.mean(), img.std()
    return (img - mean) / std


def face_encoding(photo):

    # img_BGR = cv2.imread(image_path)
    img_RGB = cv2.cvtColor(photo, cv2.COLOR_BGR2RGB)

    x = face_detector.detect_faces(img_RGB)
    x1, y1, width, height = x[0]['box']
    x1, y1 = abs(x1), abs(y1)
    x2, y2 = x1+width, y1+height
    face = img_RGB[y1:y2, x1:x2]

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

    # face = cv2.resize(face, required_shape)
    face_d = np.expand_dims(face, axis=0)
    encode = face_encoder.predict(face_d)[0]
    encodes.append(encode)

    if encodes:
        encode = np.sum(encodes, axis=0 )
        encode = l2_normalizer.transform(np.expand_dims(encode, axis=0))[0]
        encoding_dict["rdj"] = encode

    with open("encodings/rdj.json", 'w') as f:
        json.dump(str(encoding_dict), f)
    #with open(path, 'wb') as file:
        #pickle.dump(encoding_dict, file)






