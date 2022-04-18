Implementační dokumentace k 2. úloze do IPP 2021/2022 <br>
Jméno a příjmení: Kristián Kičinka <br>
Login: xkicin02

## Interpret

### Príklad spustenia programu
``` python3.8 interpret.py --source=xml_file.src < input_file.in > output_file.out ```
### Členenie programu na základe funkcionality
* Načítanie a kontrola vstupných argumentov skriptu.
* Načítanie a kontrola dát zo vstupných súborov
* Načítanie a kontrola inštrukcií
  * Vyhľadanie a uloženie náveští
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

#### Vyhľadanie a uloženie náveští
Interpret musí podporovať možnosť podmienených a nepodmienených skokov v programe, 
na platné náveštia. Preto je nutné prvotne ešte pred spracovaním programu vyhľadať a overiť 
dostupné náveštia v zdrojovom súbore. Túto funkcionalitu zabezpečuje funkcia _find_labels()_.
Funkcia vyhľadá náveštia, za pomoci funkcie _check_labels()_ ich overí a uloží do zoznamu 
náveští.

#### Naplnenie príslušných objektov dátami
Pri načítaní inštrukcií využívame objekty _Instruction_ a _Argument_. Objekt _Instruction_
uchováva operačný kód inštrukcie, jej poradie a zoznam jej argumentov. V argumente uchovávame
názov argumentu, jeho typ a hodnotu. Tieto objekty sú naplňané počas načítavania inštrukcií. 

#### Spracovanie inštrukcií
Spracovanie inštrukcií je zabezpečené súčinnosťou funkcie _interpret_instructions()_ a
jednotlivých čiastkových funkcií, ktoré tvoria funkcionalitu konkrétnych inštrukcií. Rozhodovacia 
funkcia _interpret_instructions()_ určí o aký typ inštrukcie ide a na základe toho volá príslušnú
funkciu zodpovedajúcu za konkrétnu inštrukciu. V čiastkových funkciach na základe typu 
inštrucie spracuvávajú argumenty inštukcií, pracuje sa s premennými a symbolmi, 
overujú sa typy premanných a symbolov a získavajú sa ich hodnoty. Môže dôjsť k práci so zásobníkom rámcov,
dát a iným operáciám.