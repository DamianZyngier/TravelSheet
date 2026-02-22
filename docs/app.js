// CONFIGURATION
// Since we are using static JSON for GitHub Pages
const DATA_PATH = 'data.json';

// ELEMENTS
const countrySearch = document.getElementById('countrySearch');
const searchResults = document.getElementById('searchResults');
const welcomeView = document.getElementById('welcomeView');
const detailView = document.getElementById('detailView');
const loader = document.getElementById('loader');
const popularCountries = document.getElementById('popularCountries');
const backBtn = document.getElementById('backBtn');

// DATA STATE (Local JSON)
let countriesData = {};

// INITIALIZATION
async function init() {
    showLoader(true);
    try {
        const response = await fetch(DATA_PATH);
        if (!response.ok) throw new Error("Could not find data.json");
        countriesData = await response.json();
        renderPopular();
    } catch (error) {
        console.error("Failed to load data.json", error);
        popularCountries.innerHTML = `
            <div class="card" style="grid-column: 1/-1; border-color: #ef4444; color: #991b1b;">
                <p>⚠️ Nie znaleziono pliku <b>docs/data.json</b>.</p>
                <p>Aby strona działała, musisz najpierw wygenerować ten plik skryptem: <br><code>python scripts/export_to_json.py</code></p>
            </div>
        `;
    } finally {
        showLoader(false);
    }
}

// SEARCH LOGIC
countrySearch.addEventListener('input', (e) => {
    const val = e.target.value.toLowerCase();
    if (val.length < 2) {
        searchResults.classList.add('hidden');
        return;
    }

    const filtered = Object.values(countriesData)
        .filter(c => c.name.toLowerCase().includes(val))
        .slice(0, 10);

    renderSearchResults(filtered);
});

function renderSearchResults(results) {
    if (results.length === 0) {
        searchResults.classList.add('hidden');
        return;
    }

    searchResults.innerHTML = results.map(c => `
        <div onclick="selectCountry('${c.iso2}')">
            ${c.flag_emoji || '🏳️'} ${c.name}
        </div>
    `).join('');
    searchResults.classList.remove('hidden');
}

// NAVIGATION
function selectCountry(iso2) {
    const country = countriesData[iso2];
    if (!country) return;

    searchResults.classList.add('hidden');
    countrySearch.value = '';
    
    renderDetail(country);
    welcomeView.classList.add('hidden');
    detailView.classList.remove('hidden');
    window.scrollTo(0, 0);
}

backBtn.addEventListener('click', () => {
    detailView.classList.add('hidden');
    welcomeView.classList.remove('hidden');
});

// RENDERING
function renderPopular() {
    const popularCodes = ['PL', 'TH', 'IT', 'GR', 'ES', 'TR', 'EG', 'HR', 'JP', 'US'];
    const popular = Object.values(countriesData).filter(c => popularCodes.includes(c.iso2));
    
    popularCountries.innerHTML = popular.map(c => `
        <div class="country-item" onclick="selectCountry('${c.iso2}')">
            <img src="${c.flag_url}" alt="${c.name}">
            <strong>${c.name}</strong>
        </div>
    `).join('');
}

function renderDetail(c) {
    // Basic Info
    document.getElementById('countryName').innerText = c.name;
    document.getElementById('countryFlag').src = c.flag_url;
    document.getElementById('countryMeta').innerText = `${c.capital || 'Brak stolicy'}, ${c.continent || ''}`;

    // Safety
    const safety = c.safety || {};
    const riskEl = document.getElementById('riskLevel');
    riskEl.innerText = translateRisk(safety.risk_level);
    riskEl.className = `risk-badge risk-${safety.risk_level || 'unknown'}`;
    document.getElementById('safetySummary').innerText = safety.summary || "Brak szczegółowych informacji o bezpieczeństwie.";
    document.getElementById('mszLink').href = safety.url || "https://www.gov.pl/web/dyplomacja/informacje-dla-podrozujacych";

    // Currency
    const curr = c.currency || {};
    document.getElementById('currencyInfo').innerText = `${curr.name || ''} (${curr.code || ''})`;
    document.getElementById('exchangeRate').innerText = curr.rate_pln ? `1 ${curr.code} = ${curr.rate_pln.toFixed(2)} PLN` : "Brak danych";
    
    // Practical
    const practical = c.practical || {};
    document.getElementById('cardAcceptance').innerText = translateAcceptance(practical.card_acceptance);
    document.getElementById('plugTypes').innerText = practical.plug_types || "Brak danych";
    document.getElementById('voltage').innerText = practical.voltage ? `${practical.voltage}V` : "Brak danych";
    document.getElementById('tapWater').innerText = practical.water_safe === true ? "✅ Zdatna do picia" : (practical.water_safe === false ? "❌ Lepiej pić butelkowaną" : "Brak pewnych danych");
    document.getElementById('drivingSide').innerText = practical.driving_side === 'right' ? "Prawostronny" : (practical.driving_side === 'left' ? "Lewostronny" : "Brak danych");

    // Weather
    const weather = c.weather || {};
    if (weather.temp !== null) {
        document.getElementById('currentTemp').innerText = `${Math.round(weather.temp)}°C`;
        document.getElementById('weatherCondition').innerText = weather.condition || "";
        document.getElementById('weatherIcon').src = weather.icon ? `https://openweathermap.org/img/wn/${weather.icon}@2x.png` : "";
    } else {
        document.getElementById('currentTemp').innerText = "--°C";
        document.getElementById('weatherIcon').src = "";
    }

    // Attractions
    const attractions = c.attractions || [];
    const attrList = document.getElementById('attractionsList');
    if (attractions.length > 0) {
        attrList.innerHTML = attractions.map(a => `
            <li>
                <strong>${a.name}</strong><br>
                <small>${a.category || ''}</small>
            </li>
        `).join('');
    } else {
        attrList.innerHTML = "<li>Brak danych o atrakcjach UNESCO.</li>";
    }
}

// HELPERS
function showLoader(show) {
    if (show) loader.classList.remove('hidden');
    else loader.classList.add('hidden');
}

function translateRisk(risk) {
    const map = {
        'low': 'Zachowaj zwykłą ostrożność',
        'medium': 'Zachowaj szczególną ostrożność',
        'high': 'Odradzamy podróże (niekonieczne)',
        'critical': 'Odradzamy wszelkie podróże',
        'unknown': 'Brak oficjalnych komunikatów'
    };
    return map[risk] || risk;
}

function translateAcceptance(val) {
    const map = {
        'high': 'Karta akceptowana niemal wszędzie',
        'medium': 'Warto mieć gotówkę na targu/w małych sklepach',
        'low': 'Gotówka jest niezbędna'
    };
    return map[val] || "Brak danych";
}

// Start
init();
