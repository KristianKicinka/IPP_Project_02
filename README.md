Implementační dokumentace k 2. úloze do IPP 2021/2022 <br>
Jméno a příjmení: Kristián Kičinka <br>
Login: xkicin02

## Interpret XML (interpret.py)

### Príklad spustenia programu
``` python3.8 interpret.py --source=xml_file.src < input_file.in > output_file.out ```

### Členenie programu na základe funkcionality
* Načítanie a kontrola vstupných argumentov skriptu
* Načítanie a kontrola dát zo vstupných súborov
* Načítanie a kontrola inštrukcií
  * Vyhľadanie a uloženie návestí
  * Naplnenie príslušných objektov dátami
* Spracovanie inštrukcií

#### Načítanie a kontrola vstupných argumentov skriptu
Načítanie argumentov skriptu ako aj ich syntaktickú kontrolu zabezpečuje knižnica
_Argparse_. Celkové spracovanie argumentov ako aj práca s vyššie spomínanou knižnicou
je zahrnuté vo funkcii _process_arguments()_. V tejto funkcii je taktiež implementovaný
rozhodovací mechanizmus vstupných súborov. Ide o mechanizmus, ktorý určuje zdroj vstupných
súborov.

#### Načítanie a kontrola dát zo vstupných súborov
Program pracuje s dvoma typmi vstupných súborov, ide o _input_ súbor, ktorý slúži ako zdroj dát 
pre interpret a zdrojový súbor, ktorý obsahuje zdrojový XML kód. Načítanie dát zo input súboru 
zabezpečuje funkcia _load_input_file()_. Načitanie XML súboru zabezpečuje funkcia 
_load_xml_file()_. Po načítaní XML súboru je nutné vykonať kontrolu jeho obsahu, 
jedná sa o správnu štruktúru XML kódu. Tento úkon vakonáva funkcia _check_xml_file()_. 
Kontroluje sa existenica hlavičky, prítomnosť inštrukcií a ich argumenotv. 

#### Načítanie a kontrola inštrukcií
Načítanie a kontrola inštrukcií programu prebieha vo funkcii _load_instructions()_. 
Inštrukcie sú postupne načítavané zo vstupného súboru a ukladané do objektu _Instruction_, 
ktorý reprezentuje inštrukciu a uchováva jej dostupné dáta. Kontroluje sa platnosť inštrukcie, 
tj. či je takáto inštrukcia definovaná v zadanej sade inštrukcií. Je nutné overovať aj správnosť 
poradia inštrukcií, počet a typ ich argumentov. Pri spracovaní argumentov využívame objekt 
_Argument_, ktorý uchováva dostupné o argumente inštrukcie. Jednotlivé inštrukcie sú vo 
forme objektov ukladané do zoznamu inštrucií.

#### Vyhľadanie a uloženie návestí
Interpret musí podporovať možnosť podmienených a nepodmienených skokov v programe, 
na platné návestia. Preto je nutné prvotne ešte pred spracovaním programu vyhľadať a overiť 
dostupné návestia v zdrojovom súbore. Túto funkcionalitu zabezpečuje funkcia _find_labels()_.
Funkcia vyhľadá návestia, za pomoci funkcie _check_labels()_ ich overí a uloží do zoznamu 
návestí.

#### Naplnenie príslušných objektov dátami
Pri načítaní inštrukcií využívame objekty _Instruction_ a _Argument_. Objekt _Instruction_
uchováva operačný kód inštrukcie, jej poradie a zoznam jej argumentov. V argumente uchovávame
názov argumentu, jeho typ a hodnotu. Tieto objekty sú napĺňané počas načítavania inštrukcií. 

#### Spracovanie inštrukcií
Spracovanie inštrukcií je zabezpečené súčinnosťou funkcie _interpret_instructions()_ a
jednotlivých čiastkových funkcií, ktoré tvoria funkcionalitu konkrétnych inštrukcií. Rozhodovacia 
funkcia _interpret_instructions()_ určí o aký typ inštrukcie ide a na základe toho volá príslušnú
funkciu zodpovedajúcu za konkrétnu inštrukciu. V čiastkových funkciách na základe typu 
inštrukcie spracovávajú argumenty inštrukcií, pracuje sa s premennými a symbolmi, 
overujú sa typy premenných a symbolov a získavajú sa ich hodnoty. Môže dôjsť k práci so zásobníkom rámcov,
dát a iným operáciám.


## Testovací rámec (test.php)

### Príklad spustenia programu
``` php8.1 test.php --directory=tests > output.html  ```

### Členenie programu na základe funkcionality
* Načítanie a kontrola vstupných argumentov skriptu
* Načítanie a kontrola súborov zo zadaného testovacieho adresára
* Načítanie a kontrola testov
  * Generovanie chýbajúcich súborov
* Spracovanie a vykonanie testovania
  * Parse testy
  * Interpret testy
  * Both testy
* Generovanie HTML výstupu

#### Načítanie a kontrola vstupných argumentov skriptu
Načítanie a kontrolu vstupných argumentov zabezpečuje funkcia _process_arguments()_. Tester prijíma 
prostredníctvom argumentov cestu k testovaciemu adresáru, cestu k jexamxml programu, cesty skriptom 
parse.php a interpret.py, ktoré zabezpečujú vykonanie programu, ktorý testujeme.

#### Načítanie a kontrola súborov zo zadaného testovacieho adresára
Načítanie a kontrolu z test adresára zabezpečuje funkcia _scan_directory()_. V tejto funkcii sa prehľadá zadaný
testovací adresár a jeho súbory sa uložia do zoznamu súborov. Na popis súborov využívame funkciu _pathinfo()_. 
Ak je povolené rekurzívne prehľadávanie, tak sa prehľadávajú aj podadresáre testovacieho adresára. 
Funkcia sa volá rekurzívne a jej návratové hodnoty (súbory) sa ukladajú do zoznamu súborov.

#### Načítanie a kontrola testov
Táto programová časť je implementovaná vo funkcii _load_tests()_. Pri načítavaní testov využívame objekt 
_TestObject_, ktorý uchováva názov testu, názov testovacieho súboru, cestu k testovaciemu adresáru ako aj
informácie týkajúce sa načítaných zdrojových súborov nutných na správny priebeh testu. Ide o súbory s príponami
_.src_, _.in_, _.out_, _.rc_. Existenciu týchto súborov evidujeme ku každému testu jednotlivo za pomoci 
TestObject objektu. Testovací objekt sa ukladá do zoznamu testovacích objektov (testov).

#### Generovanie chýbajúcich súborov
Pokiaľ v objekte TestObject pri nejakom teste chýba vstupný súbor s dátami, výstupný súbor alebo súbor s 
očakávaným návratovým kódom, nie je to dôvod na ukončenie programu. Chýbajúce súbory sú automaticky vygenerované
a naplnené predvolenými hodnotami. Generovanie takýchto súborov zabezpečuje funkcia _process_extensions()_.

#### Spracovanie a vykonanie testovania
Spracovanie a vykonanie celkového testovania zabezpečuje funkcia _testing()_. Pre každý testovací objekt sa vykonajú
testy na základe konfigurácie zadanej argumentami skriptu a uloženej v objekte _Script_. K dispozícii máme 3 typy
testovania. Ide o _Parse testy_, _Interpret testy_ a _Both testy_. Pre každý z týchto typov testov sa generujú
testovacie procesy. Testovací proces reprezentuje objekt _TestProcess_. Tento objekt uchováva názov testu, jeho typ,
návratové kódy ale aj cestu k dočasným súborom potrebným na vykonanie testu. Taktiež sa doň ukladajú výsledky testov.
Jednotlivé procesy sa ukladajú do zoznamu spracovaných procesov.

#### Parse testy
Ak sú v konfigurácii zadané len parse testy, spustí sa funkcia _process_parse_test()_, ktorá zabezpečuje len
testovanie parse.php. Vytvorí sa nový _TestProcess_ objekt, naplní sa dátami, následne sa vytvorí príkaz na spustenie 
parse.php skriptu a spustí sa. Pokiaľ je nutné porovnávať referenčný výstup s aktuálnym, vytvorí a spustí
sa príkaz pre jexamxml. Výsledok testu sa zapíše do patričného _TestProcess_ objektu.

#### Interpret testy
Pri nastavení testovania len interpret testov sa spúšťa funkcia _process_interpret_test()_. Opäť sa vytvorí nový 
_TestProcess_ objekt, naplní sa dátami a následne sa pristúpi k vytvoreniu a spusteniu príkazov pre chod skriptu 
_interpret.py_. Skript sa spúšťa s dostupnými testovacími súbormi. Vásledky testu sa opäť vložia do _TestProcessu_.

#### Both testy
Both testy sú akýmsi spojením parse a interpret testov. Najprv sa zavádzajú parse testy. Pokiaľ nedôjde k chybe pri 
parse testoch (návratový kód je iný ako 0), tak sa pristupuje k interpret testom. Interpret skript je volaný s 
dočasnými súbormi, ktoré boli vytvorené počas parse testovania. Následne sa zapíšu výsledky testovania do _TestProcess_ 
objektu.

#### Generovanie HTML výstupu
Pri generovaní výstupného HTML súboru využívame front-end open source toolkit Bootstrap, ktorým vytvárame štruktúru a
vzhľad výstupnej stránky. Funkcie zabezpečujúce generovanie výstupu sa nachádzajú v objekte _Output_. 
Najprv sa generuje základná šablóna stránky, následne hlavička s konfiguračnými detailmi a číselným hodnotením testov.
V neposlednom rade sa generujú výstupy pre jednotlivé spracované testy.
