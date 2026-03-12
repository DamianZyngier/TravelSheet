export interface ChecklistItem {
  id: string;
  label: string;
}

export interface ChecklistCategory {
  title: string;
  items: ChecklistItem[];
}

export interface ChecklistVariant {
  id: 'minimum' | 'optimal' | 'maximum';
  title: string;
  description: string;
  categories: ChecklistCategory[];
}

export const CHECKLISTS: ChecklistVariant[] = [
  {
    id: 'minimum',
    title: 'Wariant MINIMUM – absolutne must‑have',
    description: 'Niezbędne rzeczy, bez których podróż może być utrudniona lub niemożliwa.',
    categories: [
      {
        title: 'Dokumenty i formalności',
        items: [
          { id: 'min-doc-1', label: 'Dowód osobisty lub paszport' },
          { id: 'min-doc-2', label: 'Wiza / eVisa (kraj spoza UE)' },
          { id: 'min-doc-3', label: 'Prawo jazdy (planowany wynajem auta)' },
          { id: 'min-doc-4', label: 'Bilety (samolot/pociąg/autobus) – papierowe lub w aplikacji' },
          { id: 'min-doc-5', label: 'Rezerwacje noclegów (wydruk lub PDF w telefonie)' },
          { id: 'min-doc-6', label: 'Ubezpieczenie podróżne (numer polisy + kontakt alarmowy)' },
          { id: 'min-doc-7', label: 'Karta EKUZ (podróż w UE)' },
          { id: 'min-doc-8', label: 'Dane kontaktowe do bliskiej osoby w kraju (na kartce przy dokumentach)' },
        ]
      },
      {
        title: 'Finanse',
        items: [
          { id: 'min-fin-1', label: 'Karta płatnicza/kredytowa główna' },
          { id: 'min-fin-2', label: 'Karta płatnicza zapasowa (trzymana w innym miejscu)' },
          { id: 'min-fin-3', label: 'Gotówka w walucie lokalnej (kraj spoza UE)' },
          { id: 'min-fin-4', label: 'Trochę gotówki w EUR/USD (rezerwowo, kraj spoza UE)' },
          { id: 'min-fin-5', label: 'PIN-y do kart zapamiętane, nie na kartce przy karcie' },
        ]
      },
      {
        title: 'Elektronika',
        items: [
          { id: 'min-ele-1', label: 'Telefon' },
          { id: 'min-ele-2', label: 'Ładowarka do telefonu' },
          { id: 'min-ele-3', label: 'Powerbank (podróż długa/samolot)' },
          { id: 'min-ele-4', label: 'Adapter do gniazdek (kraj spoza UE / inny standard wtyczek)' },
          { id: 'min-ele-5', label: 'Słuchawki (podróż samolotem/pociągiem)' },
        ]
      },
      {
        title: 'Odzież i obuwie',
        items: [
          { id: 'min-clo-1', label: 'Bielizna na każdy dzień + 1–2 zapasowe komplety' },
          { id: 'min-clo-2', label: 'Skarpetki na każdy dzień' },
          { id: 'min-clo-3', label: '1–2 pary wygodnych spodni / szortów (tropiki – więcej lekkich)' },
          { id: 'min-clo-4', label: '2–4 koszulki/bluzki' },
          { id: 'min-clo-5', label: 'Bluza / lekka kurtka' },
          { id: 'min-clo-6', label: 'Wygodne buty do chodzenia' },
          { id: 'min-clo-7', label: 'Kurtka ciepła / softshell (góry/zima)' },
          { id: 'min-clo-8', label: 'Czapka, rękawiczki, szalik (góry/zima)' },
          { id: 'min-clo-9', label: 'Strój kąpielowy (tropiki / basen / spa)' },
          { id: 'min-clo-10', label: 'Piżama / strój do spania' },
          { id: 'min-clo-11', label: 'Lekka chusta / pareo (przydatna przy wejściu do świątyń / jako osłona przed słońcem)' },
        ]
      },
      {
        title: 'Higiena i kosmetyki',
        items: [
          { id: 'min-hyg-1', label: 'Szczoteczka do zębów' },
          { id: 'min-hyg-2', label: 'Pasta do zębów' },
          { id: 'min-hyg-3', label: 'Dezodorant' },
          { id: 'min-hyg-4', label: 'Mini żel pod prysznic / mydło (jeśli nie będzie w noclegu)' },
          { id: 'min-hyg-5', label: 'Szczotka / grzebień do włosów' },
          { id: 'min-hyg-6', label: 'Podpaski/tampony / kubeczek (osoba menstruująca)' },
          { id: 'min-hyg-7', label: 'Chusteczki higieniczne' },
        ]
      },
      {
        title: 'Zdrowie / apteczka',
        items: [
          { id: 'min-hea-1', label: 'Leki przyjmowane na stałe (w oryginalnych opakowaniach)' },
          { id: 'min-hea-2', label: 'Podstawowe leki przeciwbólowe/przeciwgorączkowe' },
          { id: 'min-hea-3', label: 'Leki na biegunkę / zatrucia pokarmowe (tropiki)' },
          { id: 'min-hea-4', label: 'Podstawowe plastry / plaster na odciski' },
          { id: 'min-hea-5', label: 'Mini środek dezynfekujący (żel/spray)' },
        ]
      },
      {
        title: 'Rzeczy „ratujące wyjazd”, o których łatwo zapomnieć',
        items: [
          { id: 'min-sav-1', label: 'Kopia dokumentów (wydruk + zdjęcia w telefonie)' },
          { id: 'min-sav-2', label: 'Adres i kontakt do ambasady/konsulatu (kraj spoza UE)' },
          { id: 'min-sav-3', label: 'Mała torba na brudną bieliznę/pranie' },
          { id: 'min-sav-4', label: 'Mały długopis (do formularzy, notatek)' },
          { id: 'min-sav-5', label: 'Mały notes/karteczki z ważnymi adresami (gdy telefon padnie)' },
        ]
      }
    ]
  },
  {
    id: 'optimal',
    title: 'Wariant OPTIMAL – komfort bez przepakowania',
    description: 'Wszystko z wariantu Minimum plus dodatki zwiększające komfort.',
    categories: [
      {
        title: 'Dokumenty i formalności',
        items: [
          { id: 'opt-doc-1', label: 'Lista ważnych numerów: bank, ubezpieczyciel, linie lotnicze, hotel' },
          { id: 'opt-doc-2', label: 'Wydruk planu podróży / trasy z adresami noclegów' },
          { id: 'opt-doc-3', label: 'Skany dokumentów w chmurze (np. Drive, Dropbox)' },
        ]
      },
      {
        title: 'Finanse',
        items: [
          { id: 'opt-fin-1', label: 'Portfel podróżny (z osobną kieszenią na waluty)' },
          { id: 'opt-fin-2', label: 'Mała saszetka na dokumenty i pieniądze pod ubranie (kraj spoza UE / duże miasta)' },
          { id: 'opt-fin-3', label: 'Aplikacja bankowa skonfigurowana pod wyjazd (powiadomienia, limity, powiadomienie banku o podróży – kraj spoza UE)' },
        ]
      },
      {
        title: 'Elektronika',
        items: [
          { id: 'opt-ele-1', label: 'Ładowarka do zegarka / opaski sportowej' },
          { id: 'opt-ele-2', label: 'Ładowarka do laptopa / tabletu (wyjazd służbowy)' },
          { id: 'opt-ele-3', label: 'Laptop/tablet (wyjazd służbowy / długi wyjazd)' },
          { id: 'opt-ele-4', label: 'Listwa/przedłużacz z kilkoma gniazdami (hotel z małą liczbą gniazdek)' },
          { id: 'opt-ele-5', label: 'Dodatkowa karta pamięci (fotografia)' },
          { id: 'opt-ele-6', label: 'Mała lampka/latarka na baterie (kemping / słabe oświetlenie)' },
        ]
      },
      {
        title: 'Odzież i obuwie',
        items: [
          { id: 'opt-clo-1', label: 'Ubrania „na kolację” / bardziej eleganckie (miasto / wyjazd służbowy)' },
          { id: 'opt-clo-2', label: 'Lekka kurtka przeciwdeszczowa / poncho' },
          { id: 'opt-clo-3', label: 'Klapki pod prysznic / na plażę' },
          { id: 'opt-clo-4', label: 'Czapka z daszkiem / kapelusz przeciwsłoneczny (tropiki / lato)' },
          { id: 'opt-clo-5', label: 'Okulary przeciwsłoneczne' },
          { id: 'opt-clo-6', label: 'Piżama / strój do spania' },
          { id: 'opt-clo-7', label: 'Dodatkowa para butów (np. lekkie na zmianę)' },
          { id: 'opt-clo-8', label: 'Bielizna termiczna (góry/zima)' },
          { id: 'opt-clo-9', label: 'Lekka chusta / pareo (przydatna przy wejściu do świątyń / jako osłona przed słońcem)' },
        ]
      },
      {
        title: 'Higiena i kosmetyki',
        items: [
          { id: 'opt-hyg-1', label: 'Zestaw podróżny w kosmetyczce (miniatury): szampon, odżywka, żel, balsam' },
          { id: 'opt-hyg-2', label: 'Maszynka do golenia + pianka/żel' },
          { id: 'opt-hyg-3', label: 'Kosmetyki do codziennej pielęgnacji twarzy' },
          { id: 'opt-hyg-4', label: 'Krem z filtrem UV (tropiki / lato / góry – śnieg)' },
          { id: 'opt-hyg-5', label: 'Krem po opalaniu / łagodzący na słoce (tropiki)' },
          { id: 'opt-hyg-6', label: 'Balsam do ust (suchy klimat / samolot)' },
          { id: 'opt-hyg-7', label: 'Mała paczka mokrych chusteczek' },
          { id: 'opt-hyg-8', label: 'Mały detergent do prania ręcznego (na dłuższy wyjazd)' },
        ]
      },
      {
        title: 'Zdrowie / apteczka',
        items: [
          { id: 'opt-hea-1', label: 'Leki na alergię (alergicy / tropiki)' },
          { id: 'opt-hea-2', label: 'Leki na chorobę lokomocyjną (rejsy, kręte drogi, autokar)' },
          { id: 'opt-hea-3', label: 'Zapas plastrów na odciski / pęcherze (wyjazd z dużą ilością chodzenia)' },
          { id: 'opt-hea-4', label: 'Mała opaska elastyczna (sport / góry)' },
          { id: 'opt-hea-5', label: 'Krem na otarcia (dużo chodzenia / upał)' },
          { id: 'opt-hea-6', label: 'Krople do oczu (klimatyzacja, długi lot)' },
          { id: 'opt-hea-7', label: 'Mini termometr (wyjazd z dzieckiem / dłuższy wyjazd)' },
        ]
      },
      {
        title: 'Sen i komfort w podróży',
        items: [
          { id: 'opt-com-1', label: 'Poduszka podróżna (samolot / nocny pociąg/autobus)' },
          { id: 'opt-com-2', label: 'Zatyczki do uszu' },
          { id: 'opt-com-3', label: 'Maska na oczy' },
          { id: 'opt-com-4', label: 'Lekka chusta/apaszka, która może służyć jako kocyk w samolocie' },
        ]
      },
      {
        title: 'Jedzenie / napoje',
        items: [
          { id: 'opt-foo-1', label: 'Butelka na wodę wielokrotnego użytku' },
          { id: 'opt-foo-2', label: 'Małe przekąski na drogę (batony, orzechy, suszone owoce)' },
          { id: 'opt-foo-3', label: 'Herbatki/napoje instant (góry/zima / kemping)' },
        ]
      },
      {
        title: 'Organizacja i bezpieczeństwo',
        items: [
          { id: 'opt-org-1', label: 'Małe woreczki strunowe (na kabelki, kosmetyki, mokre rzeczy)' },
          { id: 'opt-org-2', label: 'Kłódka do walizki/plecaka' },
          { id: 'opt-org-3', label: 'Etykiety z danymi kontaktowymi na bagaż' },
          { id: 'opt-org-4', label: 'Mały organizer na kable i elektronikę' },
          { id: 'opt-org-5', label: 'Mini apteczka spakowana w jedno etui' },
          { id: 'opt-org-6', label: 'Notatka z adresem noclegu w języku lokalnym (taksówki, pytanie o drogę)' },
        ]
      },
      {
        title: 'Dla dziecka (jeśli dotyczy – wyjazd z dzieckiem)',
        items: [
          { id: 'opt-chi-1', label: 'Książeczka zdrowia / karta szczepień (wyjazd z dzieckiem)' },
          { id: 'opt-chi-2', label: 'Ulubiona przytulanka / kocyk (wyjazd z dzieckiem)' },
          { id: 'opt-chi-3', label: 'Przekąski i napoje dla dziecka (wyjazd z dzieckiem)' },
          { id: 'opt-chi-4', label: 'Podstawowe zabawki / kolorowanki / kredki (wyjazd z dzieckiem)' },
          { id: 'opt-chi-5', label: 'Pieluchy / chusteczki / kremy (wyjazd z małym dzieckiem)' },
        ]
      }
    ]
  },
  {
    id: 'maximum',
    title: 'Wariant MAXIMUM – dla perfekcjonistów i długich wyjazdów',
    description: 'Wszystko z wariantów Minimum i Optimal plus zaawansowane wyposażenie.',
    categories: [
      {
        title: 'Dokumenty i formalności',
        items: [
          { id: 'max-doc-1', label: 'Wydrukowane regulaminy linii lotniczych (bagaż, opóźnienia – loty dalekie)' },
          { id: 'max-doc-2', label: 'Zaświadczenia lekarskie nt. leków / sprzętu medycznego (loty międzykontynentalne / kraj spoza UE)' },
          { id: 'max-doc-3', label: 'Zapasowe zdjęcia paszportowe (w razie utraty dokumentów, kraj spoza UE)' },
          { id: 'max-doc-4', label: 'Lista ważnych kontaktów lokalnych: hotel, wynajem auta, przewodnik, lokalny znajomy' },
        ]
      },
      {
        title: 'Finanse',
        items: [
          { id: 'max-fin-1', label: 'Trzecia karta płatnicza (schowana osobno, np. w bagażu rejestrowanym)' },
          { id: 'max-fin-2', label: 'Kilka kopert z „awaryjną gotówką” w różnych miejscach bagażu' },
          { id: 'max-fin-3', label: 'Karta przedpłacona w obcej walucie (kraj spoza UE / długie wyjazdy)' },
        ]
      },
      {
        title: 'Elektronika',
        items: [
          { id: 'max-ele-1', label: 'Powerbank o większej pojemności + drugi mały (długie wyjazdy / trekking / kemping)' },
          { id: 'max-ele-2', label: 'Mały rozdzielacz USB (ładowanie kilku urządzeń naraz)' },
          { id: 'max-ele-3', label: 'Aparat fotograficzny + zapasowe baterie / akumulator' },
          { id: 'max-ele-4', label: 'Router podróżny / eSIM z pakietem danych (kraj spoza UE)' },
          { id: 'max-ele-5', label: 'Czytnik e-booków (długie loty/pociągi)' },
          { id: 'max-ele-6', label: 'Mały głośnik Bluetooth (kemping / apartament)' },
        ]
      },
      {
        title: 'Odzież i obuwie',
        items: [
          { id: 'max-clo-1', label: 'Zestaw „kapsułowej garderoby” – rzeczy, które łatwo się ze sobą łączą (długie wyjazdy)' },
          { id: 'max-clo-2', label: 'Lekka koszula lniana / ubrania szybkoschnące (tropiki)' },
          { id: 'max-clo-3', label: 'Kurtka przeciwdeszczowa o wyższych parametrach (góry)' },
          { id: 'max-clo-4', label: 'Stuptuty (góry/zima, trekking w błocie/śniegu)' },
          { id: 'max-clo-5', label: 'Buty trekkingowe wysokie + impregnat (góry)' },
          { id: 'max-clo-6', label: 'Sandały trekkingowe (tropiki, wyjazd „miasto + natura”)' },
          { id: 'max-clo-7', label: 'Składana puchówka (góry/zima / chłodniejsze wieczory w tropikach)' },
          { id: 'max-clo-8', label: 'Kapelusz przeciwsłoneczny z dużym rondem (tropiki / pustynia)' },
          { id: 'max-clo-9', label: 'Rękawiczki narciarskie / gogle (góry/zima, narciarski)' },
        ]
      },
      {
        title: 'Higiena i kosmetyki',
        items: [
          { id: 'max-hyg-1', label: 'Pełny zestaw kosmetyków w wersji podróżnej (w tym peeling, maseczka, ulubione produkty)' },
          { id: 'max-hyg-2', label: 'Zestaw manicure/pedicure (nożyczki, pilniczek, cążki) – uwaga: do bagażu rejestrowanego' },
          { id: 'max-hyg-3', label: 'Zapas soczewek kontaktowych + płyn (osoby noszące soczewki)' },
          { id: 'max-hyg-4', label: 'Spray na komary/kleszcze (tropiki / las / kemping)' },
          { id: 'max-hyg-5', label: 'Żel po ukąszeniach (tropiki / las)' },
          { id: 'max-hyg-6', label: 'Tabletki do uzdatniania wody (trekking / kemping / miejsca z niepewną wodą)' },
        ]
      },
      {
        title: 'Zdrowie / apteczka – rozszerzona',
        items: [
          { id: 'max-hea-1', label: 'Zestaw opatrunkowy: bandaże, gaza, plaster w rolce, chusta trójkątna' },
          { id: 'max-hea-2', label: 'Małe nożyczki (bagaż rejestrowany)' },
          { id: 'max-hea-3', label: 'Maść przeciwzapalna / na stłuczenia' },
          { id: 'max-hea-4', label: 'Leki na przeziębienie / katar / gardło' },
          { id: 'max-hea-5', label: 'Elektrolity w saszetkach (tropiki / intensywny wysiłek)' },
          { id: 'max-hea-6', label: 'Indywidualne leki „specjalne” (np. na migrenę, refluks itd.)' },
          { id: 'max-hea-7', label: 'Mini instrukcja obsługi apteczki (dla współpodróżnych)' },
        ]
      },
      {
        title: 'Kemping / outdoor',
        items: [
          { id: 'max-cam-1', label: 'Namiot (kemping)' },
          { id: 'max-cam-2', label: 'Śpiwór dobrany do temperatur (kemping / góry)' },
          { id: 'max-cam-3', label: 'Karimata / mata samopompująca (kemping)' },
          { id: 'max-cam-4', label: 'Czołówka + zapasowe baterie (kemping / trekking)' },
          { id: 'max-cam-5', label: 'Sznurek/paracord (suszenie ubrań, awarie, kemping)' },
          { id: 'max-cam-6', label: 'Zestaw naczyń turystycznych + kubek składany (kemping)' },
          { id: 'max-cam-7', label: 'Kuchenka turystyczna + paliwo (kemping)' },
          { id: 'max-cam-8', label: 'Scyzoryk / multitool (kemping – do bagażu rejestrowanego)' },
          { id: 'max-cam-9', label: 'Worki na śmieci (kemping / trekking – leave no trace)' },
          { id: 'max-cam-10', label: 'Pokrowce przeciwdeszczowe na plecak (góry / deszczowe regiony)' },
        ]
      },
      {
        title: 'Organizacja i „quality of life”',
        items: [
          { id: 'max-qol-1', label: 'Packing cubes / organizery do walizki' },
          { id: 'max-qol-2', label: 'Składana torba na zakupy / dodatkowy bagaż podręczny na powrót' },
          { id: 'max-qol-3', label: 'Mały zestaw do szycia (igła, nitki, agrafki, guziki)' },
          { id: 'max-qol-4', label: 'Taśma naprawcza (duct tape) – do szybkich napraw butów, plecaka, namiotu' },
          { id: 'max-qol-5', label: 'Zapasowe okulary (osoby w okularach)' },
          { id: 'max-qol-6', label: 'Notatnik podróżny / dziennik + zapasowy długopis' },
          { id: 'max-qol-7', label: 'Karteczki samoprzylepne (oznaczanie rzeczy, notatki w hotelu)' },
          { id: 'max-qol-8', label: 'Mała waga bagażowa do walizek (loty z limitem bagażu)' },
        ]
      },
      {
        title: 'Dla dziecka – rozszerzenie (wyjazd z dzieckiem)',
        items: [
          { id: 'max-chi-1', label: 'Zapas ulubionych przekąsek/produktów, które mogą być trudno dostępne za granicą' },
          { id: 'max-chi-2', label: 'Książeczki, gry podróżne, naklejanki (długie przejazdy/loty)' },
          { id: 'max-chi-3', label: 'Zapas ubranek „do ubrudzenia” + worki na brudne rzeczy' },
          { id: 'max-chi-4', label: 'Termos na ciepłe napoje / jedzenie (wyjazd z małym dzieckiem)' },
          { id: 'max-chi-5', label: 'Składany wózek / nosidło ergonomiczne (wiek dziecka, charakter wyjazdu)' },
        ]
      }
    ]
  }
];
