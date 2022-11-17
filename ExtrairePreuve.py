
import rfc3161ng
import qrcode
import smtplib

from PIL import Image, ImageFont, ImageDraw

from Stegano import cacher, recuperer

stegano_len = 64 + 2686  # 83


def extraire_preuve():
    attestation = None
    while attestation is None:
        try:
            filename = input("Veuillez saisir le nom du fichier [Kilian_Pichard_atttestation.png]: ") or "Kilian_Pichard_attestation.png"
            attestation = Image.open(filename)
        except IOError:
            print("Erreur lors de la saisie.")
        continue

    get_stegano(attestation, filename)


def get_stegano(attestation, filename):
    stegano = recuperer(attestation, stegano_len)
    data_student = stegano[0:64]
    timestamp = stegano[64:stegano_len]
    tst = bytes.fromhex(timestamp)
    certificate_data = open('tsa.crt', 'rb').read()  # tsa.crt downloaded from https://freetsa.org/files/tsa.crt
    rt = rfc3161ng.RemoteTimestamper('http://freetsa.org/tsr', certificate=certificate_data, hashname='sha256')

    try:
        rt.check(tst, data=bytes(data_student, 'UTF-8'))
        print("Le timestamp est valide.")
    except IOError:
        print("Erreur lors de la récupération des données stéganographies.")

    # TODO: verify qrcode value and check if sign is valid
    # - récupère la partie QRcode de l’image pour récupérer la signature des données :
    # - vérifie la signature de la partie informations avec la clé publique de CY TECH
    # - affiche un rapport quant au résultat de cette vérification.

