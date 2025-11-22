from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO
from database.attrazione_DAO import AttrazioneDAO

class Model:
    def __init__(self):
        self.tour_map = {} # Mappa ID tour -> oggetti Tour
        self.attrazioni_map = {} # Mappa ID attrazione -> oggetti Attrazione
        self.relazioni_map= {}
        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        # TODO: Aggiungere eventuali altri attributi

        # Caricamento
        self.load_tour()
        self.load_attrazioni()
        self.load_relazioni()

    @staticmethod
    def load_regioni():
        """ Restituisce tutte le regioni disponibili """
        return RegioneDAO.get_regioni()

    def load_tour(self):
        """ Carica tutti i tour in un dizionario [id, Tour]"""
        self.tour_map = TourDAO.get_tour()

    def load_attrazioni(self):
        """ Carica tutte le attrazioni in un dizionario [id, Attrazione]"""
        self.attrazioni_map = AttrazioneDAO.get_attrazioni()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra tour e attrazioni e salvarle nelle strutture dati
            Collega tour <-> attrazioni.
            --> Ogni Tour ha un set di Attrazione.
            --> Ogni Attrazione ha un set di Tour.
        """
        # TODO
        self.relazioni_map= TourDAO.get_tour_attrazioni()


    def genera_pacchetto(self, id_regione: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto turistico ottimale per una regione rispettando i vincoli di durata, budget e attrazioni uniche.
        :param id_regione: id della regione
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Tour)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il valore culturale del pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        # TODO
        for relazione in self.relazioni_map:
            if self.tour_map[relazione["id_tour"]].id_regione == id_regione:
                self.attrazioni_map[relazione["id_attrazione"]].tour.add(self.tour_map[relazione["id_tour"]])
                self.tour_map[relazione["id_tour"]].attrazioni.add(self.attrazioni_map[relazione["id_attrazione"]])

        durata_corrente = 0
        pacchetto_parziale = []
        costo_corrente= 0.0
        valore_corrente= 0
        attrazioni_usate = set()
        livello=0

        limite_giorni=  max_giorni if max_giorni is not None else 10000
        limite_budget= max_budget if max_budget is not None else 10000000000

        self._ricorsione(pacchetto_parziale, durata_corrente, costo_corrente, valore_corrente, attrazioni_usate, limite_giorni, limite_budget)

        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _ricorsione(self,  pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, attrazioni_usate: set,limite_giorni, limite_budget):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il valore culturale"""

        # TODO: è possibile cambiare i parametri formali della funzione se ritenuto opportuno

        if valore_corrente > self._valore_ottimo:
            self._pacchetto_ottimo = list(pacchetto_parziale)
            self._costo = costo_corrente
            self._valore_ottimo = valore_corrente


        tour_disponibili = []
        for t in self.tour_map.values():
            if t not in pacchetto_parziale and t.attrazioni:
                tour_disponibili.append(t)


        for tour in tour_disponibili:

            if not tour.attrazioni.intersection(attrazioni_usate):
                if float(tour.costo) + costo_corrente <= limite_budget:
                    if tour.durata_giorni + durata_corrente <= limite_giorni:
                        pacchetto_parziale.append(tour)

                        nuove_attrazioni = attrazioni_usate.copy()

                        nuove_attrazioni.update(tour.attrazioni)

                        # Calcolo il valore aggiunto di questo tour
                        valore= self.calcola_valore_cult(pacchetto_parziale)
                        delta_valore = valore_corrente + valore


                        self._ricorsione(pacchetto_parziale,
                                         durata_corrente + tour.durata_giorni,
                                         costo_corrente + float(tour.costo),
                                         valore_corrente + delta_valore,
                                         nuove_attrazioni,
                                         limite_giorni,
                                         limite_budget)


                        pacchetto_parziale.pop()


    def calcola_valore_cult(self, lista):
        valore=0
        for tour in lista:
            for attrazione in tour.attrazioni:
               valore += attrazione.valore_culturale
        return valore


