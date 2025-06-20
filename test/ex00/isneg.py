try:
    number = float(input("Entrez un nombre : "))

    if number < 0:
        print("Ce nombre est négatif")
    elif number > 0:
        print("Ce nombre est positif")
    else:
        print("Ce nombre est à la fois positif et négatif")

except ValueError:
    print("Erreur : vous devez entrer un nombre valide.")
