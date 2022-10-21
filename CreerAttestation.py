from PIL import Image, ImageFont, ImageDraw
import qrcode
import pyotp


#my_image = Image.open("template_certificate.png")
#title_text = "Certificat délivré à Prénom Nom"
#font = ImageFont.truetype("Almond_Cookies.ttf", 50)
#image_editable = ImageDraw.Draw(my_image)
#image_editable.text((875,620), title_text, (37, 30, 10), font=font)
#my_image.save("result.png")

#img = qrcode.make('Some data here')
#type(img)  # qrcode.image.pil.PilImage
#img.save("some_file.png")

otp_id = "CTXRHFP3VSZHIZR5WOJG3RYWCGZKSLVP"

def creerAttestation():
    print("Pour créer une attestation, il me faut les information suivantes :")
    surname = input("- Prénom de l'étudiant : ") or "Prénom"
    name = input("- Nom de l'étudiant : ") or "Nom"
    certif_name = input("- Intitulé de la certification : ") or "Ingénieur Informatique"
    mail = input("- Adresse éléctronique de l'étudiant : ") or "pichardkil@cy-tech.fr"
    otp_value = input("- Valeur de l'OTP : ")
    otp_result = verifOtp(otp_value) or pyotp.TOTP(otp_id).now()
    print(surname)
    print(name)
    print(certif_name)
    print(mail)

    # Verification de l'OTP, tant que faux, on redemande
    while not otp_result:
        print("\nOTP invalide, veuillez réessayer.")
        otp_value = input("- Valeur de l'OTP : ")
        otp_result = verifOtp(otp_value)

    putInfoOnCertif(name, surname, certif_name)


def createQRCode():



def putInfoOnCertif(name, surname, certif_name):
    template_certificate = Image.open("template_certificate.png")
    certificate_name = "Diplôme " + certif_name
    certificate_delivery = "Ce certificat est délivré à " + surname + " " + name
    font_certificate_name = ImageFont.truetype("Almond_Cookies.ttf", 60)
    font_certificate_delivery = ImageFont.truetype("Almond_Cookies.ttf", 30)
    certificate_editable = ImageDraw.Draw(template_certificate)
    certificate_editable.text((400,400), certificate_name, (37, 30, 10), font=font_certificate_name)
    certificate_editable.text((875,620), certificate_delivery, (37, 30, 10), font=font_certificate_delivery)
    template_certificate.save("result.png")



def verifOtp(secret):
    totp = pyotp.TOTP(otp_id)
    verify = totp.verify(secret)
    return verify

