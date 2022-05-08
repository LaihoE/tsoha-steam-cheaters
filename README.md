# Tsoha harjoitustyö kevät 2022

Heroku: https://steamcheaters.herokuapp.com/form  
Voit esimerkiksi käyttää tätä testaamiseen: 76561197991348083  


Asioita jotka jäivät tekemättä ajanpuutteen takia:
- Käyttäjille toimintaa (tällä hetkellä voit vain luoda käyttäjän ja kirjautua sisään)
- Nätimpi ulkoasu
- Joitain pieniä bugeja


Projektia käytetään steam käyttäjien tutkimiseen. Steam on maailman isoin pelien jakelualusta. Erityisesti projektissa tarkastellaan miten luotettava pelaaja on. Tämä tehdään keräämällä tietoa 
pelaajien ystäväsuhteista, pelitiedoista yms. 

Tietoa Steamista saa heidän APIn kautta: https://steamcommunity.com/dev

Käyttäjä antaa SteamIDn ja applikaatio palauttaa kiinnostavaa tietoa käyttäjästä.  
Esimerkkinä käyttäjästä joka on vähemmän luotettava on sellainen jolla on suuri osa ystävistä pelikiellossa.

Esimerkkejä tietokannan tauluista: 
- Ystäväsuhteet
- Pelaajan pelit (pelitunnit, pelien määrä yms.)
- Pelaajan saavutukset eri peleissä.


Hieman vastaava applikaatio on: https://faceitfinder.com/ voit esimerkiksi syöttää tämän steamidn: 76561197991348083

Projekti on aputyökalu isommalle projektille: https://github.com/LaihoE/DLAC


## Todo
- [x] Funktiot jotka hakevat datan API:sta
- [x] Perus toiminnallisuus ilman tietokantaa
- [x] Funktiot jotka lähettävät datan tietokantaan
- [x] Funktiot jotka hakevat datan tietokannasta
- [x] Esteettisempi html, (noh hieman paremi...)
- [x] Tarkistaa että ID on toimiva
- [x] Login
- [x] redirectaa onnistuneen haun
- [ ] Käyttäjä pystyy seuraamaan edellisiä hakujansa
