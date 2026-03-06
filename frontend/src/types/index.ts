export interface CountryData {
  name: string;
  name_pl: string;
  iso2: string;
  iso3: string;
  capital: string;
  continent: string;
  region: string;
  flag_emoji: string;
  flag_url: string;
  latitude: number | null;
  longitude: number | null;
  unesco_count: number;
  timezone: string | null;
  national_dish: string | null;
  wiki_summary: string | null;
  national_symbols: string | null;
  population: number | null;
  area: number | null;
  phone_code: string | null;
  largest_cities: string | null;
  ethnic_groups: string | null;
  climate_description?: string;
  is_independent: boolean;
  parent?: {
    iso2: string;
    name_pl: string;
  } | null;
  territories?: {
    iso2: string;
    name_pl: string;
  }[];
  religions: { name: string; percentage: number }[];
  languages: { name: string; is_official: boolean }[];
  safety: {
    risk_level: string;
    risk_text: string;
    risk_details: string;
    url: string;
    last_updated?: string | null;
  };
  currency: {
    code: string;
    name: string;
    rate_pln: number | null;
    last_updated?: string | null;
    relative_cost?: string | null;
  };
  practical: {
    plug_types: string;
    voltage: number | null;
    water_safe: boolean | null;
    water_safe_for_brushing: boolean | null;
    driving_side: string;
    card_acceptance: string;
    best_exchange_currency: string;
    exchange_where: string;
    atm_advice: string;
    bargaining_info: string;
    alcohol_rules: string;
    dress_code: string;
    photography_restrictions: string;
    sensitive_topics: string;
    local_norms: string;
    store_hours: string;
    internet_notes: string;
    esim_available: boolean | null;
    emergency?: {
      police: string | null;
      ambulance: string | null;
      fire: string | null;
      dispatch: string | null;
      member_112?: boolean;
    } | null;
    vaccinations_required: string;
    vaccinations_suggested: string;
    health_info: string;
    roaming_info: string;
    license_type: string;
    souvenirs: string;
    last_updated?: string | null;
  };
  costs?: {
    index: number | null;
    restaurants: number | null;
    groceries: number | null;
    transport: number | null;
    accommodation: number | null;
    ratio_to_pl: number | null;
    daily_budget_low: number | null;
    daily_budget_mid: number | null;
    daily_budget_high: number | null;
    last_updated?: string | null;
  };
  embassies?: {
    type: string;
    city: string;
    address: string;
    phone: string;
    email: string;
    website: string;
  }[];
  entry?: {
    visa_required: boolean | null;
    visa_status: string;
    passport_required: boolean | null;
    temp_passport_allowed: boolean | null;
    id_card_allowed: boolean | null;
    visa_notes: string;
  };
  holidays?: {
    name: string;
    date: string;
  }[];
  attractions?: {
    name: string;
    category: string;
    description?: string;
  }[];
  souvenirs_list?: {
    name: string;
    description?: string;
    category?: string;
    image_url?: string;
  }[];
  unesco_places?: {
    name: string;
    category: string;
    is_danger?: boolean;
    is_transnational?: boolean;
    unesco_id?: string;
    image_url?: string;
    description?: string;
  }[];
  climate?: {
    month: number;
    temp_day: number;
    temp_night: number;
    rain: number;
    season?: string;
  }[];
  weather?: {
    temp: number | null;
    condition: string;
    icon: string;
    forecast?: any[];
    last_updated?: string | null;
  };
  laws_and_customs?: {
    category: string;
    title: string;
    description: string;
  }[];
  // Advanced Wikidata Fields
  hdi?: number;
  life_expectancy?: number;
  gdp_nominal?: number;
  gdp_ppp?: number;
  gdp_per_capita?: number;
  gini?: number;
  coat_of_arms_url?: string;
  inception_date?: string;
  official_tourist_website?: string;
  regional_products?: string;
  has_ekuz: boolean;
  natural_hazards?: string;
  popular_apps?: string;
  largest_cities?: string;
  ethnic_groups?: string;
  last_updated?: string | null;
}
