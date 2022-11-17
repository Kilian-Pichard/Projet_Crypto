#!/usr/bin/python
# coding=utf8

import qrcode
import pyotp
import rfc3161ng
import smtplib
from PIL import Image, ImageFont, ImageDraw
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

from Stegano import cacher, recuperer

otp_id = "CTXRHFP3VSZHIZR5WOJG3RYWCGZKSLVP"
stegano_len = 64 + 2686  # 83


def creer_attestation():
    print("Veuillez entrer l'OTP pour prouver que vous êtes autoriser à avoir accès à ce programme :")
    otp_value = input("- Valeur de l'OTP : ")
    otp_result = verif_otp(otp_value) or pyotp.TOTP(otp_id).now()  # REMOVE or... IN PRODUCTION
    while not otp_result: # While OTP result is False, we ask again
        print("\nOTP invalide, veuillez réessayer.")
        otp_value = input("- Valeur de l'OTP : ")
        otp_result = verif_otp(otp_value)
    print("Vous avez accès au programme.")
    print("Pour créer une attestation, il me faut les information suivantes :")
    surname = input("- Prénom de l'étudiant [Kilian] : ") or "Kilian"
    name = input("- Nom de l'étudiant [Pichard] : ") or "Pichard"
    certif_name = input("- Intitulé de la certification [Ingénieur cybersécurité] : ") or "Ingénieur cybersécurité"
    mail = input("- Adresse éléctronique de l'étudiant [pichardkil@cy-tech.fr] : ") or "pichardkil@cy-tech.fr"
    print("Veuillez patienter pendant la création de l'attestation...")

    filename = (surname + "_" + name + "_attestation.png").replace(" ", "_")

    with open("PKI/private/cybersecurite.key", 'rb') as private_file:
        private_key = serialization.load_pem_private_key(
            private_file.read(),
            password=b'passphrase',
        )

    data_student = name+"||"+surname+"||"+certif_name
    signature = private_key.sign(
        data_student.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    signature_str = signature.hex()  # .isascii() return True

    put_info_on_certif(name, surname, certif_name, filename, signature_str)
    stegano = create_stegano(data_student)
    hide_stegano(filename, stegano)

    with open("PKI/public/public.pem", 'rb') as public_file:
        public_key = serialization.load_pem_public_key(
            public_file.read(),
            backend=default_backend()
        )
    # public_key = private_key.public_key() #Other way to get public key from private key
    # My solution : openssl rsa -in ../private/cybersecurite.key -outform PEM -pubout -out public.pem
    try:
        public_key.verify(
            signature,
            data_student.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        print('valid!')
    except InvalidSignature:
        print('invalid!')

    print("L'attestation a bien été créée. Vous la trouverez sous la forme de Prenom_Nom_attestation.png")
    send_email()


def create_qrcode(filename, signature):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=25,
        border=1,
    )
    qr.add_data(signature)
    qr.make(fit=True)
    qr_code = qr.make_image(fill_color="black", back_color="white")
    qr_code = qr_code.resize((200, 200))
    attestation = Image.open(filename)
    attestation.paste(qr_code, (1420, 935))
    attestation.save(filename)


def put_info_on_certif(name, surname, certif_name, filename, signature):
    template_certificate = Image.open("template_certificate.png")
    certificate_name = "Diplôme " + certif_name
    certificate_delivery = "Ce certificat est délivré à " + surname + " " + name
    font_certificate_name = ImageFont.truetype("Almond_Cookies.ttf", 60)
    font_certificate_delivery = ImageFont.truetype("Almond_Cookies.ttf", 30)
    certificate_editable = ImageDraw.Draw(template_certificate)
    certificate_editable.text((400, 400), certificate_name, (37, 30, 10), font=font_certificate_name)
    certificate_editable.text((650, 620), certificate_delivery, (37, 30, 10), font=font_certificate_delivery)
    template_certificate.save(filename)
    create_qrcode(filename, signature)


def verif_otp(secret):  # is like CreerPass
    totp = pyotp.TOTP(otp_id)
    verify = totp.verify(secret)
    return verify


def create_stegano(data_student):
    supp_chars = "*" * ((64 - len(data_student))-4)
    data_student_64 = data_student + "||" + supp_chars + "||"
    certificate_data = open('tsa.crt', 'rb').read()  # tsa.crt downloaded from https://freetsa.org/files/tsa.crt
    rt = rfc3161ng.RemoteTimestamper('http://freetsa.org/tsr', certificate=certificate_data, hashname='sha256')
    tst = rt.timestamp(data=bytes(data_student_64, 'UTF-8'))
    rt.check(tst, data=bytes(data_student_64, 'UTF-8'))  # Need to be True, otherwise, system failure
    timestamp_str = tst.hex()
    # timestamp = rfc3161ng.get_timestamp(tst) # Conversion in datetime format
    to_hide = data_student_64 + timestamp_str  # str(timestamp)
    return to_hide


def hide_stegano(filename, stegano):
    attestation = Image.open(filename)
    cacher(attestation, stegano)
    attestation.save(filename)
    attestation = Image.open(filename)
    tmp = recuperer(attestation, stegano_len)
    student_data = tmp[0:64]
    tst = tmp[64:stegano_len]


def send_email():
    print("Envoie de l'attestation par mail...")
    sender = "Private Person <pichardkil@cy-tech.fr>"
    receiver = "A Test User <to@example.com>"

    message = f"""\
    Subject: Hi Mailtrap
    To: {receiver}
    From: {sender}

    This is a test e-mail message."""

    with smtplib.SMTP("smtp.mailtrap.io", 2525) as server:
        server.starttls()
        server.login("9dd8c806d7594a", "31db9d53493130")
        server.sendmail(sender, receiver, message)
        print("Mail envoyé")



