#!/usr/bin/python
# coding=utf8

from PIL import Image, ImageFont, ImageDraw
import qrcode
import pyotp
import rfc3161ng
from Stegano import cacher, recuperer

otp_id = "CTXRHFP3VSZHIZR5WOJG3RYWCGZKSLVP"
stegano_len = 83

def creerAttestation():
    print("Veuillez entrer l'OTP pour prouver que vous êtes autoriser à avoir accès à ce programme :")
    otp_value = input("- Valeur de l'OTP : ")
    otp_result = verifOtp(otp_value) or pyotp.TOTP(otp_id).now()  # REMOVE or... IN PRODUCTION
    while not otp_result: # While OTP result is False, we ask again
        print("\nOTP invalide, veuillez réessayer.")
        otp_value = input("- Valeur de l'OTP : ")
        otp_result = verifOtp(otp_value)
    print("Vous avez accès au programme.")
    print("Pour créer une attestation, il me faut les information suivantes :")
    surname = input("- Prénom de l'étudiant [Kilian] : ") or "Kilian"
    name = input("- Nom de l'étudiant [Pichard] : ") or "Pichard"
    certif_name = input("- Intitulé de la certification [Ingénieur cybersécurité] : ") or "Ingénieur cybersécurité"
    mail = input("- Adresse éléctronique de l'étudiant [pichardkil@cy-tech.fr] : ") or "pichardkil@cy-tech.fr"
    print("Veuillez patienter pendant la création de l'attestation...")

    filename = (surname + "_" + name + "_attestation.png").replace(" ", "_")
    putInfoOnCertif(name, surname, certif_name, filename)
    stegano = create_stegano(name, surname, certif_name)
    hide_stegano(filename, stegano)


def createQRCode(filename):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=25,
        border=1,
    )
    data = 'TEST QRCODE'
    qr.add_data(data)
    qr.make(fit=True)
    qr_code = qr.make_image(fill_color="black", back_color="white")
    qr_code = qr_code.resize((200, 200))
    attestation = Image.open(filename)
    attestation.paste(qr_code, (1420, 935))
    attestation.save(filename)


def putInfoOnCertif(name, surname, certif_name, filename):
    template_certificate = Image.open("template_certificate.png")
    certificate_name = "Diplôme " + certif_name
    certificate_delivery = "Ce certificat est délivré à " + surname + " " + name
    font_certificate_name = ImageFont.truetype("Almond_Cookies.ttf", 60)
    font_certificate_delivery = ImageFont.truetype("Almond_Cookies.ttf", 30)
    certificate_editable = ImageDraw.Draw(template_certificate)
    certificate_editable.text((400, 400), certificate_name, (37, 30, 10), font=font_certificate_name)
    certificate_editable.text((650, 620), certificate_delivery, (37, 30, 10), font=font_certificate_delivery)
    template_certificate.save(filename)
    createQRCode(filename)


def verifOtp(secret):
    totp = pyotp.TOTP(otp_id)
    verify = totp.verify(secret)
    return verify


def create_stegano(name, surname, certif_name):
    data_student = name+"||"+surname+"||"+certif_name
    supp_chars = "*" * ((64 - len(data_student))-4)
    data_student_64 = data_student + "||" + supp_chars + "||"
    certificate_data = open('tsa.crt', 'rb').read()  # tsa.crt downloaded from https://freetsa.org/files/tsa.crt
    rt = rfc3161ng.RemoteTimestamper('http://freetsa.org/tsr', certificate=certificate_data, hashname='sha256')
    tst = rt.timestamp(data=bytes(data_student, 'UTF-8'))
    rt.check(tst, data=bytes(data_student, 'UTF-8'))  # Need to be True, otherwise, system failure
    timestamp = rfc3161ng.get_timestamp(tst) # Conversion in datetime format
    to_hide = data_student_64 + str(timestamp)
    return to_hide

def CreerPass():
    print("CreerPass")


def ExtrairePreuve():
    print("ExtrairePreuve")


def hide_stegano(filename, stegano):
    attestation = Image.open(filename)
    cacher(attestation, stegano)
    attestation.save(filename)
    attestation = Image.open(filename)
    tmp = recuperer(attestation, stegano_len)
    student_data = tmp[0:64]
    tst = tmp[64:stegano_len]



