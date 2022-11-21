
import rfc3161ng

from pyzbar.pyzbar import decode
from PIL import Image, ImageFont, ImageDraw
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

from Stegano import cacher, recuperer

stegano_len = 64 + 2686  # 83


def extraire_preuve():
    attestation = None
    filename = ""
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
    data_student_64 = stegano[0:64]
    timestamp = stegano[64:stegano_len]
    tst = bytes.fromhex(timestamp)
    certificate_data = open('tsa.crt', 'rb').read()  # tsa.crt downloaded from https://freetsa.org/files/tsa.crt
    rt = rfc3161ng.RemoteTimestamper('http://freetsa.org/tsr', certificate=certificate_data, hashname='sha256')

    try:
        rt.check(tst, data=bytes(data_student_64, 'UTF-8'))
        print("Le timestamp est valide.")
    except IOError:
        print("Erreur lors de la récupération des données stéganographies.")

    decoded_list = decode(attestation)
    signature = decoded_list[0].data

    with open("PKI/private/cybersecurite.key", 'rb') as private_file:
        private_key = serialization.load_pem_private_key(
            private_file.read(),
            password=b'passphrase',
        )

    with open("PKI/public/public.pem", 'rb') as public_file:
        public_key = serialization.load_pem_public_key(
            public_file.read(),
            backend=default_backend()
        )

    name = data_student_64.split("||")[0]
    surname = data_student_64.split("||")[1]
    certif_name = data_student_64.split("||")[2]
    data_student = name+"||"+surname+"||"+certif_name
    signature = bytes.fromhex(signature.decode())

    # public_key = private_key.public_key() #Other way to get public key from private key
    # My solution : openssl rsa -in ../private/cybersecurite.key -outform PEM -pubout -out public.pem
    try:
        public_key.verify(
            signature,
            data_student.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        print('La signature est valide.')
    except InvalidSignature:
        print('La signature est invalide.')
        exit(-1)

    print("\nRapport de vérification de l'attestation :")
    print(" - Le timestamp ainsi que la signature de l'attestation sont valides et officiels.")
    print(" - L'attestation est donc bien valide.")
    print(" - Cette attestaton a été attribué à " + surname + " " + name + " pour la formation suivante : " + certif_name)
    print(" - L'attestation a été validé et signé à cette date : " + str(rfc3161ng.get_timestamp(tst)))

