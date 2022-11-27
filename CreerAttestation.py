#!/usr/bin/python
# coding=utf8
import base64

import qrcode
import pyotp
import rfc3161ng
import smtplib
import ssl
import time
import smime
from PIL import Image, ImageFont, ImageDraw
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from Stegano import cacher, recuperer

otp_id = "CTXRHFP3VSZHIZR5WOJG3RYWCGZKSLVP"
stegano_len = 64 + 2686  # 83


def creer_attestation():
    print("Veuillez entrer l'OTP pour prouver que vous êtes autoriser à avoir accès à ce programme :")
    otp_value = input("- Valeur de l'OTP : ")
    otp_result = verif_otp(otp_value) or pyotp.TOTP(otp_id).now()  # REMOVE or pyotp... IN PRODUCTION to ask the good OTP code, because now it's automatically completing with the good OTP code
    while not otp_result: # While OTP result is False, we ask again
        print("\nOTP invalide, veuillez réessayer.")
        otp_value = input("- Valeur de l'OTP : ")
        otp_result = verif_otp(otp_value)
    print("Vous avez accès au programme.")
    print("Pour créer une attestation, il me faut les information suivantes :")
    surname = input("- Prénom de l'étudiant [Tom] : ") or "Tom"
    name = input("- Nom de l'étudiant [Hanks] : ") or "Hanks"
    certif_name = input("- Intitulé de l'attestation [Ingénieur cybersécurité] : ") or "Ingénieur cybersécurité"
    mail = input("- Adresse éléctronique de l'étudiant [tom-hanks-cybersecurity@cy-tech.fr] : ") or "tom-hanks-cybersecurity@cy-tech.fr"
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

    put_info_on_certif(name, surname, certif_name, filename, signature_str) # Creation of the QR Code
    create_stegano(data_student, filename)

    print("L'attestation a bien été créée. Vous la trouverez sous le nom de " + filename)
    send_email(filename, mail)


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
    certificate_name = "Diplôme\n" + certif_name
    certificate_delivery = "Ce certificat est délivré à " + surname + " " + name
    font_certificate_name = ImageFont.truetype("Almond_Cookies.ttf", 100)
    font_certificate_delivery = ImageFont.truetype("Almond_Cookies.ttf", 50)
    certificate_editable = ImageDraw.Draw(template_certificate)
    certificate_editable.text((400, 300), certificate_name, (37, 30, 10), font=font_certificate_name)
    certificate_editable.text((400, 620), certificate_delivery, (37, 30, 10), font=font_certificate_delivery)
    template_certificate.save(filename)
    create_qrcode(filename, signature)


def verif_otp(secret):  # is like CreerPass
    totp = pyotp.TOTP(otp_id)
    verify = totp.verify(secret)
    return verify


def create_stegano(data_student, filename):
    supp_chars = "*" * ((64 - len(data_student))-4)
    data_student_64 = data_student + "||" + supp_chars + "||"
    certificate_data = open('tsa.crt', 'rb').read()  # tsa.crt downloaded from https://freetsa.org/files/tsa.crt
    rt = rfc3161ng.RemoteTimestamper('http://freetsa.org/tsr', certificate=certificate_data, hashname='sha256')
    tst = rt.timestamp(data=bytes(data_student_64, 'UTF-8'))
    rt.check(tst, data=bytes(data_student_64, 'UTF-8'))  # Need to be True, otherwise, system failure
    timestamp_str = tst.hex()
    # timestamp = rfc3161ng.get_timestamp(tst) # Conversion in datetime format
    to_hide = data_student_64 + timestamp_str  # str(timestamp)
    hide_stegano(filename, to_hide)


def hide_stegano(filename, stegano):
    attestation = Image.open(filename)
    cacher(attestation, stegano)
    attestation.save(filename)
    attestation = Image.open(filename)
    tmp = recuperer(attestation, stegano_len)
    student_data = tmp[0:64]
    tst = tmp[64:stegano_len]


def send_email(filename, mail):
    print("Envoie de l'attestation par mail, cela peut prendre quelques secondes...")
    time.sleep(3)

    sender = 'admin@example.com'
    receivers = [mail]
    port = 465
    smtp_server = "mail.kilianpichard.fr"

    user = 'test@kilianpichard.fr'
    password = 'sos$38oMoFe#jPf6'

    with open(filename, "rb") as attestation:
        attestation_b64 = base64.b64encode(attestation.read())

    with open('PKI/certs/cybersecurite.pem', 'rb') as public_key:
        content = "To: " + mail + "\rFrom: test@kilianpichard.fr\r\nSubject: Confirmation de création de l'attestation\r\nFromContent-Type: image/png\r\nContent-Transfer-Encoding: base64\r\n\r\n" + attestation_b64.decode('utf-8')
        content_encrypted = smime.encrypt(content, public_key.read())

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(user, password)
        server.sendmail(sender, receivers, content_encrypted)
        server.quit()
        print("Mail envoyé à " + mail)