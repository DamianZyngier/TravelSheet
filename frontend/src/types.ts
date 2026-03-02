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
  last_updated: string | null;
  timezone: string | null;
  national_dish: string | null;
  wiki_summary: string | null;
  national_symbols: string | null;
  unique_things: string | null;
  alcohol_status: string | null;
  lgbtq_status: string | null;
  id_requirement: string | null;
  main_airport: string | null;
  railway_info: string | null;
  natural_hazards: string | null;
  popular_apps: string | null;
  population: number | null;
  area: number | null;
  phone_code: string | null;
  largest_cities: string | null;
  ethnic_groups: string | null;
  is_independent: boolean;
  parent?: {
    iso2: string;
    name_pl: string;
  } | null;
  territories?: {
    iso2: string;
    name_pl: string;
  }[];
  religions: { name: string; percentage: number; last_updated?: string }[];
  languages: { name: string; is_official: boolean; last_updated?: string }[];
  safety: {
    risk_level: string;
    risk_text: string;
    risk_details: string;
    url: string;
    last_updated: string | null;
  };
  currency: {
    code: string;
    name: string;
    rate_pln: number | null;
    last_updated: string | null;
  };
  practical: {
    plug_types: string;
    voltage: number | null;
    frequency: number | null;
    water_safe: boolean | null;
    water_safe_for_brushing: boolean | null;
    driving_side: string;
    card_acceptance: string;
    best_exchange_currency: string;
    exchange_where: string;
    atm_advice: string;
    tipping_culture: string;
    drinking_age: string;
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
    last_updated: string | null;
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
    last_updated: string | null;
  };
  embassies?: {
    type: string;
    city: string;
    address: string;
    phone: string;
    email: string;
    website: string;
    last_updated?: string;
  }[];
  entry?: {
    visa_required: boolean | null;
    visa_status: string;
    passport_required: boolean | null;
    temp_passport_allowed: boolean | null;
    id_card_allowed: boolean | null;
    visa_notes: string;
    last_updated?: string;
  };
  holidays?: {
    name: string;
    date: string;
    last_updated?: string;
  }[];
  attractions?: {
    name: string;
    category: string;
    description?: string;
    booking_info?: string | null;
    last_updated?: string;
  }[];
  unesco_places?: {
    name: string;
    category: string;
    is_danger?: boolean;
    is_transnational?: boolean;
    unesco_id?: string;
    image_url?: string;
    description?: string;
    last_updated?: string;
  }[];
  climate?: {
    month: number;
    temp_day: number;
    temp_night: number;
    rain: number;
    last_updated?: string;
  }[];
  weather?: {
    temp: number | null;
    condition: string;
    icon: string;
    last_updated: string | null;
    forecast?: {
      date: string;
      temp_max: number;
      temp_min: number;
      condition: string;
      icon: string;
    }[];
  };
}
