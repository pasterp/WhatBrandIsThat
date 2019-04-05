import base64
import io
from PIL import Image, ImageTk
try:
    # Python2
    import Tkinter as tk
except ImportError:
    # Python3+
    import tkinter as tk


def buildAndReturnLabel(base64i,typeimg):



    b=base64i+''                                                                                                        # nous changeons la base64 en un string
    c=b.split(",")                                                                                                      # nous separons la date des donnees qui sont separe par une virgule
    d=c[1]                                                                                                              # nous recupeons la date qui se situe apres la virgule
    received = base64.b64decode(d)                                                                                      # nous decodons l image de la base 64
    infos=typeimg                                                                                                       # la fonction typeimg renvoi le format de l image
    img = Image.open(io.BytesIO(received))                                                                              # nous ouvrons l image pour la traiter
    if "png" in infos:                                                                                                  # nous enregistrons l image au format correspondant a typeimg
        imgConstruite = "bow_retrieval/dataset-retr/imageToTest/test.png"
        img.save(imgConstruite)
    else:
        imgConstruite = "bow_retrieval/dataset-retr/imageToTest/test.jpg"
        img.save(imgConstruite)

    return imgConstruite                                                                                                # nous retournons la resultat



