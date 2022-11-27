#!/usr/bin/python
# coding=utf8

from CreerAttestation import *
from ExtrairePreuve import *

print("Bonjour, bienvenue sur l'application d'attestation de CY Tech ! Ici, vous pourrez créer une attestation, ainsi que verifier la validité de votre attestation.")
print("Veuillez choisir ce que vous souhaitez faire :")

choix_default = 1
choix = int(input("1- Créer une attestation\n2- Vérifier la validité de votre attestation\n0- Quitter le programme\nVotre choix [1] : ") or 1)
print("")
if choix == 1:
	print("Vous avez choisi de créer une attestation.")
	creer_attestation()
elif choix == 2:
	print("Vous avez choisi de vérifier la validité de votre attestation.")
	extraire_preuve()
elif choix == 0:
	print("Vous avez choisi de quitter le programme.")
	exit()
else:
	print("Le choix n'est pas valable.")