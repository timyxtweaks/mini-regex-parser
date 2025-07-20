# Kreirao: timyx

class TipTokena:
    """Definisanje tipova tokena koje lexer može prepoznati"""
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
    """Reprezencija jednog tokena s tipom i vrijednošću"""
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
    
    def greška(self):
        """Baca grešku za neočekivani karakter"""
        raise Exception(f"Neočekivani karakter '{self.trenutni_karakter}' na poziciji {self.pozicija}")
    
    def pomijeri(self):
        """Pomjera pokazivač na sljedeći karakter"""
        self.pozicija += 1
        if self.pozicija >= len(self.regex):
            self.trenutni_karakter = None
        else:
            self.trenutni_karakter = self.regex[self.pozicija]
    
    def sljedeći_token(self):
        """Vraća sljedeći token iz regex stringa"""
        if self.trenutni_karakter is None:
            return Token(TipTokena.KRAJ, None)
        
        if self.trenutni_karakter == '.':
            self.pomijeri()
            return Token(TipTokena.TACKA, '.')
        
        if self.trenutni_karakter == '*':
            self.pomijeri()
            return Token(TipTokena.ZVJEZDICA, '*')
        
        if self.trenutni_karakter == '+':
            self.pomijeri()
            return Token(TipTokena.PLUS, '+')
        
        if self.trenutni_karakter == '?':
            self.pomijeri()
            return Token(TipTokena.UPITNIK, '?')
        
        if self.trenutni_karakter == '|':
            self.pomijeri()
            return Token(TipTokena.VERTIKALNA_CRTA, '|')
        
        if self.trenutni_karakter == '(':
            self.pomijeri()
            return Token(TipTokena.LIJEVA_ZAGRADA, '(')
        
        if self.trenutni_karakter == ')':
            self.pomijeri()
            return Token(TipTokena.DESNA_ZAGRADA, ')')
        
        # Svi ostali karakteri se tretiraju kao obični karakteri
        karakter = self.trenutni_karakter
        self.pomijeri()
        return Token(TipTokena.KARAKTER, karakter)
    
    def tokeniziraj(self):
        """Vraća listu svih tokena"""
        tokeni = []
        while True:
            token = self.sljedeći_token()
            tokeni.append(token)
            if token.tip == TipTokena.KRAJ:
                break
        return tokeni

# AST čvorovi za predstavljanje regex stabla
class ASTČvor:
    """Bazna klasa za sve AST čvorove"""
    pass

class Karakter(ASTČvor):
    """Čvor za obične karaktere"""
    def __init__(self, vrijednost):
        self.vrijednost = vrijednost
    
    def __repr__(self):
        return f"Karakter('{self.vrijednost}')"

class TačkaBiloKoji(ASTČvor):
    """Čvor za . (bilo koji karakter)"""
    def __repr__(self):
        return "TačkaBiloKoji()"

class Sekvenca(ASTČvor):
    """Čvor za sekvencu čvorova (konkatenacija)"""
    def __init__(self, čvorovi):
        self.čvorovi = čvorovi
    
    def __repr__(self):
        return f"Sekvenca({self.čvorovi})"

class Alternativa(ASTČvor):
    """Čvor za | (alternativa)"""
    def __init__(self, lijevo, desno):
        self.lijevo = lijevo
        self.desno = desno
    
    def __repr__(self):
        return f"Alternativa({self.lijevo}, {self.desno})"

class Kvantifikator(ASTČvor):
    """Čvor za kvantifikatore (*, +, ?)"""
    def __init__(self, čvor, tip):
        self.čvor = čvor
        self.tip = tip  # '*', '+', ili '?'
    
    def __repr__(self):
        return f"Kvantifikator({self.čvor}, '{self.tip}')"

class Grupa(ASTČvor):
    """Čvor za grupisanje ()"""
    def __init__(self, čvor):
        self.čvor = čvor
    
    def __repr__(self):
        return f"Grupa({self.čvor})"

class Parser:
    """Parser koji od tokena pravi AST stablo"""
    
    def __init__(self, tokeni):
        self.tokeni = tokeni
        self.pozicija = 0
        self.trenutni_token = self.tokeni[0] if tokeni else None
    
    def greška(self):
        """Baca grešku za neočekivani token"""
        raise Exception(f"Neočekivani token {self.trenutni_token}")
    
    def pojedi_token(self, očekivani_tip):
        """Konzumira token određenog tipa"""
        if self.trenutni_token.tip == očekivani_tip:
            self.trenutni_token = self.tokeni[self.pozicija + 1] if self.pozicija + 1 < len(self.tokeni) else None
            self.pozicija += 1
        else:
            self.greška()
    
    def parsiraj(self):
        """Glavni ulazak u parsiranje - parsira alternativu"""
        rezultat = self.parsiraj_alternativu()
        if self.trenutni_token and self.trenutni_token.tip != TipTokena.KRAJ:
            self.greška()
        return rezultat
    
    def parsiraj_alternativu(self):
        """Parsira alternativu (najniži prioritet)"""
        čvor = self.parsiraj_sekvencu()
        
        while self.trenutni_token and self.trenutni_token.tip == TipTokena.VERTIKALNA_CRTA:
            self.pojedi_token(TipTokena.VERTIKALNA_CRTA)
            desno = self.parsiraj_sekvencu()
            čvor = Alternativa(čvor, desno)
        
        return čvor
    
    def parsiraj_sekvencu(self):
        """Parsira sekvencu čvorova (konkatenacija)"""
        čvorovi = []
        
        while (self.trenutni_token and 
               self.trenutni_token.tip not in [TipTokena.VERTIKALNA_CRTA, TipTokena.DESNA_ZAGRADA, TipTokena.KRAJ]):
            čvorovi.append(self.parsiraj_kvantifikator())
        
        if len(čvorovi) == 0:
            return None
        elif len(čvorovi) == 1:
            return čvorovi[0]
        else:
            return Sekvenca(čvorovi)
    
    def parsiraj_kvantifikator(self):
        """Parsira kvantifikatore (*, +, ?)"""
        čvor = self.parsiraj_osnovni()
        
        if self.trenutni_token and self.trenutni_token.tip in [TipTokena.ZVJEZDICA, TipTokena.PLUS, TipTokena.UPITNIK]:
            tip_kvantifikatora = self.trenutni_token.vrijednost
            self.pojedi_token(self.trenutni_token.tip)
            return Kvantifikator(čvor, tip_kvantifikatora)
        
        return čvor
    
    def parsiraj_osnovni(self):
        """Parsira osnovne elemente (karakteri, tačka, grupe)"""
        if self.trenutni_token.tip == TipTokena.KARAKTER:
            vrijednost = self.trenutni_token.vrijednost
            self.pojedi_token(TipTokena.KARAKTER)
            return Karakter(vrijednost)
        
        elif self.trenutni_token.tip == TipTokena.TACKA:
            self.pojedi_token(TipTokena.TACKA)
            return TačkaBiloKoji()
        
        elif self.trenutni_token.tip == TipTokena.LIJEVA_ZAGRADA:
            self.pojedi_token(TipTokena.LIJEVA_ZAGRADA)
            čvor = self.parsiraj_alternativu()
            self.pojedi_token(TipTokena.DESNA_ZAGRADA)
            return Grupa(čvor)
        
        else:
            self.greška()

class Evaluator:
    """Evaluira AST stablo protiv ulaznog teksta"""
    
    def __init__(self, ast):
        self.ast = ast
    
    def odgovara(self, tekst):
        """Provjerava da li regex odgovara bilo kojem dijelu teksta"""
        # Pokušavamo match na svakoj poziciji u tekstu
        for i in range(len(tekst) + 1):
            if self._pokušaj_match(self.ast, tekst, i) is not None:
                return True
        return False
    
    def _pokušaj_match(self, čvor, tekst, pozicija):
        """Pokušava match čvora na određenoj poziciji. Vraća novu poziciju ili None"""
        if čvor is None:
            return pozicija
        
        if isinstance(čvor, Karakter):
            if pozicija < len(tekst) and tekst[pozicija] == čvor.vrijednost:
                return pozicija + 1
            return None
        
        elif isinstance(čvor, TačkaBiloKoji):
            if pozicija < len(tekst):
                return pozicija + 1
            return None
        
        elif isinstance(čvor, Sekvenca):
            trenutna_pozicija = pozicija
            for pod_čvor in čvor.čvorovi:
                rezultat = self._pokušaj_match(pod_čvor, tekst, trenutna_pozicija)
                if rezultat is None:
                    return None
                trenutna_pozicija = rezultat
            return trenutna_pozicija
        
        elif isinstance(čvor, Alternativa):
            # Pokušavamo lijevi čvor
            lijevi_rezultat = self._pokušaj_match(čvor.lijevo, tekst, pozicija)
            if lijevi_rezultat is not None:
                return lijevi_rezultat
            
            # Ako lijevi ne uspije, pokušavamo desni
            return self._pokušaj_match(čvor.desno, tekst, pozicija)
        
        elif isinstance(čvor, Kvantifikator):
            if čvor.tip == '*':
                return self._match_zvjezdica(čvor.čvor, tekst, pozicija)
            elif čvor.tip == '+':
                return self._match_plus(čvor.čvor, tekst, pozicija)
            elif čvor.tip == '?':
                return self._match_upitnik(čvor.čvor, tekst, pozicija)
        
        elif isinstance(čvor, Grupa):
            return self._pokušaj_match(čvor.čvor, tekst, pozicija)
        
        return None
    
    def _match_zvjezdica(self, čvor, tekst, pozicija):
        """Match za * kvantifikator (nula ili više)"""
        # Prvo pokušavamo bez match-a (nula ponavljanja)
        rezultat = pozicija
        
        # Zatim pokušavamo što više match-ova
        while True:
            novi_rezultat = self._pokušaj_match(čvor, tekst, rezultat)
            if novi_rezultat is None or novi_rezultat == rezultat:
                break
            rezultat = novi_rezultat
        
        return rezultat
    
    def _match_plus(self, čvor, tekst, pozicija):
        """Match za + kvantifikator (jedno ili više)"""
        # Moramo imati barem jedan match
        rezultat = self._pokušaj_match(čvor, tekst, pozicija)
        if rezultat is None:
            return None
        
        # Zatim pokušavamo dodatne match-ove
        while True:
            novi_rezultat = self._pokušaj_match(čvor, tekst, rezultat)
            if novi_rezultat is None or novi_rezultat == rezultat:
                break
            rezultat = novi_rezultat
        
        return rezultat
    
    def _match_upitnik(self, čvor, tekst, pozicija):
        """Match za ? kvantifikator (nula ili jedno)"""
        # Pokušavamo match
        rezultat = self._pokušaj_match(čvor, tekst, pozicija)
        if rezultat is not None:
            return rezultat
        
        # Ako nema match-a, vraćamo originalnu poziciju (nula pojavljivanja)
        return pozicija

def da_li_odgovara(regex, tekst):
    """
    Glavna funkcija koja provjerava da li regex odgovara tekstu.
    
    Args:
        regex (str): Regex pattern
        tekst (str): Tekst za pretraživanje
    
    Returns:
        bool: True ako regex odgovara, False inače
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
        print(f"Greška pri parsiranju regex-a '{regex}': {e}")
        return False

# Testiranje funkcionalnosti
if __name__ == "__main__":
    # Osnovni testovi
    test_slučajevi = [
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
    uspješni = 0
    ukupno = len(test_slučajevi)
    
    for regex, tekst, očekivano in test_slučajevi:
        rezultat = da_li_odgovara(regex, tekst)
        status = "✓" if rezultat == očekivano else "✗"
        print(f"{status} '{regex}' vs '{tekst}' -> {rezultat} (očekivano: {očekivano})")
        if rezultat == očekivano:
            uspješni += 1
    
    print(f"\nRezultat: {uspješni}/{ukupno} testova prošlo")