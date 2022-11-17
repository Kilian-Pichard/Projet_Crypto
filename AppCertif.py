#!/usr/bin/python
# coding=utf8

from CreerAttestation import *
from ExtrairePreuve import *

print("Bonjour, bienvenue sur l'application de certification de CY Tech ! Ici, vous pourrez créer un certificat, ainsi que verifier la validité de votre certificat.")
print("Veuillez choisir ce que vous souhaitez faire :")

choix_default = 1
choix = int(input("1- Créer un certificat\n2- Vérifier la validité de votre certificat\n0- Quitter le programme\nVotre choix [1] : ") or 2)
print("")
if choix == 1:
	print("Vous avez choisi de créer un certificat.")
	creer_attestation()
elif choix == 2:
	print("Vous avez choisi de vérifier la validité de votre certificat.")
	extraire_preuve()
elif choix == 0:
	print("Vous avez choisi de quitter le programme.")
	exit()
else:
	print("Le choix n'est pas valable.")