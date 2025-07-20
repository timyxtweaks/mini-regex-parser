# Kreirao: timyx

class TipTokena:
    """Definisanje tipova tokena koje lexer moze prepoznati"""
    KARAKTER = "KARAKTER"
    TACKA = "TACKA"
    ZVJEZDICA = "ZVJEZDICA"
    PLUS = "PLUS"
    UPITNIK = "UPITNIK"
    VERTIKALNA_CRTA = "VERTIKALNA_CRTA"
    LIJEVA_ZAGRADA = "LIJEVA_ZAGRADA"
    DESNA_ZAGRADA = "DESNA_ZAGRADA"
    KRAJ = "KRAJ"

class Token:
    """Reprezencija jednog tokena s tipom i vrijednoscu"""
    def __init__(self, tip, vrijednost):
        self.tip = tip
        self.vrijednost = vrijednost
    
    def __repr__(self):
        return f"Token({self.tip}, '{self.vrijednost}')"

class Lexer:
    """Tokenizuje regex string u niz tokena"""
    
    def __init__(self, regex):
        self.regex = regex
        self.pozicija = 0
        self.trenutni_karakter = self.regex[0] if regex else None
    
    def greska(self):
        """Baca gresku za neocekivani karakter"""
        raise Exception(f"Neocekivani karakter '{self.trenutni_karakter}' na poziciji {self.pozicija}")
    
    def pomjeri(self):
        """Pomjera pokazivac na sljedeci karakter"""
        self.pozicija += 1
        if self.pozicija >= len(self.regex):
            self.trenutni_karakter = None
        else:
            self.trenutni_karakter = self.regex[self.pozicija]
    
    def sljedeci_token(self):
        """Vraca sljedeci token iz regex stringa"""
        if self.trenutni_karakter is None:
            return Token(TipTokena.KRAJ, None)
        
        if self.trenutni_karakter == '.':
            self.pomjeri()
            return Token(TipTokena.TACKA, '.')
        
        if self.trenutni_karakter == '*':
            self.pomjeri()
            return Token(TipTokena.ZVJEZDICA, '*')
        
        if self.trenutni_karakter == '+':
            self.pomjeri()
            return Token(TipTokena.PLUS, '+')
        
        if self.trenutni_karakter == '?':
            self.pomjeri()
            return Token(TipTokena.UPITNIK, '?')
        
        if self.trenutni_karakter == '|':
            self.pomjeri()
            return Token(TipTokena.VERTIKALNA_CRTA, '|')
        
        if self.trenutni_karakter == '(':
            self.pomjeri()
            return Token(TipTokena.LIJEVA_ZAGRADA, '(')
        
        if self.trenutni_karakter == ')':
            self.pomjeri()
            return Token(TipTokena.DESNA_ZAGRADA, ')')
        
        # Svi ostali karakteri se tretiraju kao obicni karakteri
        karakter = self.trenutni_karakter
        self.pomjeri()
        return Token(TipTokena.KARAKTER, karakter)
    
    def tokeniziraj(self):
        """Vraca listu svih tokena"""
        tokeni = []
        while True:
            token = self.sljedeci_token()
            tokeni.append(token)
            if token.tip == TipTokena.KRAJ:
                break
        return tokeni

# AST cvorovi za predstavljanje regex stabla
class ASTCvor:
    """Bazna klasa za sve AST cvorove"""
    pass

class Karakter(ASTCvor):
    """Cvor za obicne karaktere"""
    def __init__(self, vrijednost):
        self.vrijednost = vrijednost
    
    def __repr__(self):
        return f"Karakter('{self.vrijednost}')"

class TackaBiloKoji(ASTCvor):
    """Cvor za . (bilo koji karakter)"""
    def __repr__(self):
        return "TackaBiloKoji()"

class Sekvenca(ASTCvor):
    """Cvor za sekvencu cvorova (konkatenacija)"""
    def __init__(self, cvorovi):
        self.cvorovi = cvorovi
    
    def __repr__(self):
        return f"Sekvenca({self.cvorovi})"

class Alternativa(ASTCvor):
    """Cvor za | (alternativa)"""
    def __init__(self, lijevo, desno):
        self.lijevo = lijevo
        self.desno = desno
    
    def __repr__(self):
        return f"Alternativa({self.lijevo}, {self.desno})"

class Kvantifikator(ASTCvor):
    """Cvor za kvantifikatore (*, +, ?)"""
    def __init__(self, cvor, tip):
        self.cvor = cvor
        self.tip = tip  # '*', '+', ili '?'
    
    def __repr__(self):
        return f"Kvantifikator({self.cvor}, '{self.tip}')"

class Grupa(ASTCvor):
    """Cvor za grupisanje ()"""
    def __init__(self, cvor):
        self.cvor = cvor
    
    def __repr__(self):
        return f"Grupa({self.cvor})"

class Parser:
    """Parser koji od tokena pravi AST stablo"""
    
    def __init__(self, tokeni):
        self.tokeni = tokeni
        self.pozicija = 0
        self.trenutni_token = self.tokeni[0] if tokeni else None
    
    def greska(self):
        """Baca gresku za neocekivani token"""
        raise Exception(f"Neocekivani token {self.trenutni_token}")
    
    def pojedi_token(self, ocekivani_tip):
        """Konzumira token odredjenog tipa"""
        if self.trenutni_token.tip == ocekivani_tip:
            self.trenutni_token = self.tokeni[self.pozicija + 1] if self.pozicija + 1 < len(self.tokeni) else None
            self.pozicija += 1
        else:
            self.greska()
    
    def parsiraj(self):
        """Glavni ulazak u parsiranje - parsira alternativu"""
        rezultat = self.parsiraj_alternativu()
        if self.trenutni_token and self.trenutni_token.tip != TipTokena.KRAJ:
            self.greska()
        return rezultat
    
    def parsiraj_alternativu(self):
        """Parsira alternativu (najnizi prioritet)"""
        cvor = self.parsiraj_sekvencu()
        
        while self.trenutni_token and self.trenutni_token.tip == TipTokena.VERTIKALNA_CRTA:
            self.pojedi_token(TipTokena.VERTIKALNA_CRTA)
            desno = self.parsiraj_sekvencu()
            cvor = Alternativa(cvor, desno)
        
        return cvor
    
    def parsiraj_sekvencu(self):
        """Parsira sekvencu cvorova (konkatenacija)"""
        cvorovi = []
        
        while (self.trenutni_token and 
               self.trenutni_token.tip not in [TipTokena.VERTIKALNA_CRTA, TipTokena.DESNA_ZAGRADA, TipTokena.KRAJ]):
            cvorovi.append(self.parsiraj_kvantifikator())
        
        if len(cvorovi) == 0:
            return None
        elif len(cvorovi) == 1:
            return cvorovi[0]
        else:
            return Sekvenca(cvorovi)
    
    def parsiraj_kvantifikator(self):
        """Parsira kvantifikatore (*, +, ?)"""
        cvor = self.parsiraj_osnovni()
        
        if self.trenutni_token and self.trenutni_token.tip in [TipTokena.ZVJEZDICA, TipTokena.PLUS, TipTokena.UPITNIK]:
            tip_kvantifikatora = self.trenutni_token.vrijednost
            self.pojedi_token(self.trenutni_token.tip)
            return Kvantifikator(cvor, tip_kvantifikatora)
        
        return cvor
    
    def parsiraj_osnovni(self):
        """Parsira osnovne elemente (karakteri, tacka, grupe)"""
        if self.trenutni_token.tip == TipTokena.KARAKTER:
            vrijednost = self.trenutni_token.vrijednost
            self.pojedi_token(TipTokena.KARAKTER)
            return Karakter(vrijednost)
        
        elif self.trenutni_token.tip == TipTokena.TACKA:
            self.pojedi_token(TipTokena.TACKA)
            return TackaBiloKoji()
        
        elif self.trenutni_token.tip == TipTokena.LIJEVA_ZAGRADA:
            self.pojedi_token(TipTokena.LIJEVA_ZAGRADA)
            cvor = self.parsiraj_alternativu()
            self.pojedi_token(TipTokena.DESNA_ZAGRADA)
            return Grupa(cvor)
        
        else:
            self.greska()

class Evaluator:
    """Evaluira AST stablo protiv ulaznog teksta"""
    
    def __init__(self, ast):
        self.ast = ast
    
    def odgovara(self, tekst):
        """Provjerava da li regex odgovara bilo kojem dijelu teksta"""
        # Pokusavamo match na svakoj poziciji u tekstu
        for i in range(len(tekst) + 1):
            if self._pokusaj_match(self.ast, tekst, i) is not None:
                return True
        return False
    
    def _pokusaj_match(self, cvor, tekst, pozicija):
        """Pokusava match cvora na odredjenoj poziciji. Vraca novu poziciju ili None"""
        if cvor is None:
            return pozicija
        
        if isinstance(cvor, Karakter):
            if pozicija < len(tekst) and tekst[pozicija] == cvor.vrijednost:
                return pozicija + 1
            return None
        
        elif isinstance(cvor, TackaBiloKoji):
            if pozicija < len(tekst):
                return pozicija + 1
            return None
        
        elif isinstance(cvor, Sekvenca):
            trenutna_pozicija = pozicija
            for pod_cvor in cvor.cvorovi:
                rezultat = self._pokusaj_match(pod_cvor, tekst, trenutna_pozicija)
                if rezultat is None:
                    return None
                trenutna_pozicija = rezultat
            return trenutna_pozicija
        
        elif isinstance(cvor, Alternativa):
            # Pokusavamo lijevi cvor
            lijevi_rezultat = self._pokusaj_match(cvor.lijevo, tekst, pozicija)
            if lijevi_rezultat is not None:
                return lijevi_rezultat
            
            # Ako lijevi ne uspije, pokusavamo desni
            return self._pokusaj_match(cvor.desno, tekst, pozicija)
        
        elif isinstance(cvor, Kvantifikator):
            if cvor.tip == '*':
                return self._match_zvjezdica(cvor.cvor, tekst, pozicija)
            elif cvor.tip == '+':
                return self._match_plus(cvor.cvor, tekst, pozicija)
            elif cvor.tip == '?':
                return self._match_upitnik(cvor.cvor, tekst, pozicija)
        
        elif isinstance(cvor, Grupa):
            return self._pokusaj_match(cvor.cvor, tekst, pozicija)
        
        return None
    
    def _match_zvjezdica(self, cvor, tekst, pozicija):
        """Match za * kvantifikator (nula ili vise)"""
        # Prvo pokusavamo bez match-a (nula ponavljanja)
        rezultat = pozicija
        
        # Zatim pokusavamo sto vise match-ova
        while True:
            novi_rezultat = self._pokusaj_match(cvor, tekst, rezultat)
            if novi_rezultat is None or novi_rezultat == rezultat:
                break
            rezultat = novi_rezultat
        
        return rezultat
    
    def _match_plus(self, cvor, tekst, pozicija):
        """Match za + kvantifikator (jedno ili vise)"""
        # Moramo imati barem jedan match
        rezultat = self._pokusaj_match(cvor, tekst, pozicija)
        if rezultat is None:
            return None
        
        # Zatim pokusavamo dodatne match-ove
        while True:
            novi_rezultat = self._pokusaj_match(cvor, tekst, rezultat)
            if novi_rezultat is None or novi_rezultat == rezultat:
                break
            rezultat = novi_rezultat
        
        return rezultat
    
    def _match_upitnik(self, cvor, tekst, pozicija):
        """Match za ? kvantifikator (nula ili jedno)"""
        # Pokusavamo match
        rezultat = self._pokusaj_match(cvor, tekst, pozicija)
        if rezultat is not None:
            return rezultat
        
        # Ako nema match-a, vracamo originalnu poziciju (nula pojavljivanja)
        return pozicija

def da_li_odgovara(regex, tekst):
    """
    Glavna funkcija koja provjerava da li regex odgovara tekstu.
    
    Args:
        regex (str): Regex pattern
        tekst (str): Tekst za pretrazivanje
    
    Returns:
        bool: True ako regex odgovara, False inace
    """
    try:
        # Korak 1: Tokenizacija
        lexer = Lexer(regex)
        tokeni = lexer.tokeniziraj()
        
        # Korak 2: Parsiranje
        parser = Parser(tokeni)
        ast = parser.parsiraj()
        
        # Korak 3: Evaluacija
        evaluator = Evaluator(ast)
        return evaluator.odgovara(tekst)
    
    except Exception as e:
        print(f"Greska pri parsiranju regex-a '{regex}': {e}")
        return False

# Testiranje funkcionalnosti
if __name__ == "__main__":
    # Osnovni testovi
    test_slucajevi = [
        ("a", "a", True),
        ("a", "b", False),
        (".", "x", True),
        ("a*", "", True),
        ("a*", "aaa", True),
        ("a+", "", False),
        ("a+", "aaa", True),
        ("a?", "", True),
        ("a?", "a", True),
        ("a?", "aa", True),
        ("a|b", "a", True),
        ("a|b", "b", True),
        ("a|b", "c", False),
        ("(ab)*", "", True),
        ("(ab)*", "abab", True),
        ("a.c", "abc", True),
        ("a.c", "axc", True),
        ("a.c", "ac", False),
        ("a(b|c)d", "abd", True),
        ("a(b|c)d", "acd", True),
        ("a(b|c)d", "axd", False),
    ]
    
    print("Pokretanje testova...")
    uspjesni = 0
    ukupno = len(test_slucajevi)
    
    for regex, tekst, ocekivano in test_slucajevi:
        rezultat = da_li_odgovara(regex, tekst)
        status = "✓" if rezultat == ocekivano else "✗"
        print(f"{status} '{regex}' vs '{tekst}' -> {rezultat} (ocekivano: {ocekivano})")
        if rezultat == ocekivano:
            uspjesni += 1
    
    print(f"\nRezultat: {uspjesni}/{ukupno} testova proslo")
