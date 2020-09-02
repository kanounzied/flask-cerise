class Client_:
    def __init__(self, firstname, lastname):
        self.prenom = firstname
        self.nom = lastname
        self.cin = 0
        self.tel_num = 00000000
        self.e_mail = ""
        self.password = ""
        self.cin = 00000000
        self.date_de_naissance = ""
        self.type_famille = ""
        self.confirmed = False


class Propriete_:
    def __init__(self, apt_unit):
        self.apt_unit = apt_unit
        self.nbr_chambres = 0
        self.rentown = ""
        self.etage = 0
        self.sys_alarm = False
        self.climatisation = False
        self.chauffage = False
        self.type = ""
        self.surface = ""
        self.jardin = False
        self.under_construction = False
        self.rue = ""
        self.valuables = ""


class AutresBiens_:
    def __init__(self, libelle, valeurEstimee):
        self.libelle = libelle
        self.valeurEstimee = valeurEstimee


class Contrat_:
    def __init__(self, date_debut, prix):
        self.date_debut = date_debut
        self.prix = prix
        self.deductible = 250
        self.date_renouvellment = ""
