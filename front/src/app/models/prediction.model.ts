export type SellerType = 'produit' | 'service';
export type ScoreLabel = 'faible' | 'moyen' | 'élevé';

export interface HistoricalPoint {
  date: string;
  benefice: number;
  ca?: number;
  cout?: number;
  nb_ventes?: number;
  revenu?: number;
  depense?: number;
}

export interface PredictionPoint {
  date: string;
  benefice: number;
}

export interface ScoreDetails {
  pred_current_month: number;
  pred_next_month: number;
  historical_p33: number;
  historical_p66: number;
  current_month_label: string;
  next_month_label: string;
}

export interface ProductRecommendation {
  designation: string;
  total_ventes: number;
  benefice_total: number;
  marge_pct: number;
  prix_vente_moyen: number;
  approvisionnement_suggere: number;
  priorite: 'haute' | 'moyenne' | 'basse';
}

export interface Stats {
  total_benefice: number;
  avg_mensuel: number;
  min_benefice: number;
  max_benefice: number;
}

export interface PredictionResult {
  type: SellerType;
  best_model: string;
  best_model_score: number;
  all_model_scores: Record<string, number | null>;
  score_label: ScoreLabel;
  score_details: ScoreDetails;
  historical: HistoricalPoint[];
  predictions: PredictionPoint[];
  product_analysis?: ProductRecommendation[];
  stats: Stats;
}
