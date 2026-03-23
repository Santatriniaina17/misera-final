import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.pipeline import Pipeline
import warnings
warnings.filterwarnings('ignore')

try:
    from xgboost import XGBRegressor
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False


def _build_models_config():
    config = {
        'ridge': {
            'model': Ridge(),
            'params': {'model__alpha': [0.01, 0.1, 1, 10, 100]}
        },
        'lasso': {
            'model': Lasso(max_iter=5000),
            'params': {'model__alpha': [0.001, 0.01, 0.1, 1, 10]}
        },
        'random_forest': {
            'model': RandomForestRegressor(random_state=42),
            'params': {
                'model__n_estimators': [50, 100, 200],
                'model__max_depth': [None, 5, 10],
            }
        },
        'gradient_boosting': {
            'model': GradientBoostingRegressor(random_state=42),
            'params': {
                'model__n_estimators': [50, 100],
                'model__learning_rate': [0.05, 0.1, 0.2],
                'model__max_depth': [3, 5],
            }
        },
        'svr': {
            'model': SVR(),
            'params': {
                'model__C': [0.1, 1, 10],
                'model__kernel': ['rbf', 'linear'],
            }
        },
    }
    if XGBOOST_AVAILABLE:
        config['xgboost'] = {
            'model': XGBRegressor(random_state=42, verbosity=0),
            'params': {
                'model__n_estimators': [50, 100, 200],
                'model__learning_rate': [0.05, 0.1, 0.2],
                'model__max_depth': [3, 5, 7],
            }
        }
    return config

MODELS_CONFIG = _build_models_config()


""" def train_best_model(X, y):
    #Train multiple models with GridSearch and return the best one.
    tscv = TimeSeriesSplit(n_splits=min(3, len(X) - 1))
    best_model = None
    best_score = -np.inf
    best_name = ''
    model_scores = {}

    for name, config in MODELS_CONFIG.items():
        try:
            pipe = Pipeline([
                ('scaler', StandardScaler()),
                ('model', config['model'])
            ])
            gs = GridSearchCV(
                pipe, config['params'],
                cv=tscv,
                scoring='r2',
                n_jobs=-1,
                refit=True
            )
            gs.fit(X, y)
            score = gs.best_score_
            model_scores[name] = round(score, 4)
            if score > best_score:
                best_score = score
                best_model = gs.best_estimator_
                best_name = name
        except Exception:
            model_scores[name] = None

    return best_model, best_name, best_score, model_scores """
def train_best_model(X, y):
    """
    Version optimisée :
    - Pas de GridSearch (trop lent)
    - Validation simple avec TimeSeriesSplit
    - Compatible production (Render)
    """

    # Sécurité si dataset trop petit
    if len(X) < 5:
        pipe = Pipeline([
            ('scaler', StandardScaler()),
            ('model', Ridge(alpha=1.0))
        ])
        pipe.fit(X, y)
        return pipe, "ridge", 0, {"ridge": 0}

    tscv = TimeSeriesSplit(n_splits=2)

    best_model = None
    best_score = -np.inf
    best_name = ''
    model_scores = {}

    for name, config in MODELS_CONFIG.items():
        try:
            pipe = Pipeline([
                ('scaler', StandardScaler()),
                ('model', config['model'])
            ])

            scores = []

            for train_idx, test_idx in tscv.split(X):
                X_train, X_test = X[train_idx], X[test_idx]
                y_train, y_test = y[train_idx], y[test_idx]

                pipe.fit(X_train, y_train)
                score = pipe.score(X_test, y_test)
                scores.append(score)

            avg_score = float(np.mean(scores))
            model_scores[name] = round(avg_score, 4)

            if avg_score > best_score:
                best_score = avg_score
                best_model = pipe
                best_name = name

        except Exception:
            model_scores[name] = None

    # Fit final sur toutes les données
    if best_model is not None:
        best_model.fit(X, y)
    else:
        # fallback sécurité
        best_model = Pipeline([
            ('scaler', StandardScaler()),
            ('model', Ridge(alpha=1.0))
        ])
        best_model.fit(X, y)
        best_name = "ridge"
        best_score = 0

    return best_model, best_name, best_score, model_scores

def compute_score_label(pred_current_month: float, pred_next_month: float, historical_benefits: np.ndarray):
    """
    Compare bénéfices prédits pour mois actuel & mois prochain
    par rapport aux percentiles de l'historique.

    Logique :
    - On calcule la moyenne des 2 prédictions (mois actuel + mois prochain)
    - On la positionne par rapport aux percentiles 33 et 66 de l'historique
      → faible  : < P33
      → moyen   : P33 – P66
      → élevé   : > P66
    """
    p33 = float(np.percentile(historical_benefits, 33))
    p66 = float(np.percentile(historical_benefits, 66))

    avg_pred = (pred_current_month + pred_next_month) / 2

    if avg_pred >= p66:
        label = 'élevé'
    elif avg_pred >= p33:
        label = 'moyen'
    else:
        label = 'faible'

    return label, round(p33, 2), round(p66, 2)


def add_time_features(df):
    """Create time-based features for ML."""
    df = df.copy()
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    df['t'] = (df['year'] - df['year'].min()) * 12 + df['month']
    df['t_sq'] = df['t'] ** 2
    return df


def predict_product_seller(df):
    """
    Process product seller CSV: date, designation, prix_achat, prix_vente
    Returns prediction results + product analysis.
    """
    required = ['date', 'designation', 'prix_achat', 'prix_vente']
    df.columns = [c.strip().lower().replace(' ', '_').replace("'", '_').replace("'", '_') for c in df.columns]

    # Flexible column mapping
    col_map = {}
    for req in required:
        for col in df.columns:
            if req.replace('_', '') in col.replace('_', ''):
                col_map[req] = col
                break

    df = df.rename(columns={v: k for k, v in col_map.items()})
    df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['date'])
    df['prix_achat'] = pd.to_numeric(df['prix_achat'], errors='coerce').fillna(0)
    df['prix_vente'] = pd.to_numeric(df['prix_vente'], errors='coerce').fillna(0)
    df['benefice'] = df['prix_vente'] - df['prix_achat']

    # Monthly aggregation
    df['month_year'] = df['date'].dt.to_period('M')
    monthly = df.groupby('month_year').agg(
        benefice=('benefice', 'sum'),
        ca=('prix_vente', 'sum'),
        cout=('prix_achat', 'sum'),
        nb_ventes=('designation', 'count')
    ).reset_index()
    monthly['date'] = monthly['month_year'].dt.to_timestamp()
    monthly = add_time_features(monthly)
    monthly = monthly.sort_values('date')

    # ML prediction
    feature_cols = ['t', 't_sq', 'month_sin', 'month_cos', 'month']
    X = monthly[feature_cols].values
    y = monthly['benefice'].values

    best_model, best_name, best_score, all_scores = train_best_model(X, y)

    # Predict future 6 months
    last_t = monthly['t'].max()
    last_year = monthly['date'].max().year
    last_month = monthly['date'].max().month

    future_rows = []
    for i in range(1, 7):
        nm = last_month + i
        ny = last_year + (nm - 1) // 12
        nm = ((nm - 1) % 12) + 1
        t = last_t + i
        future_rows.append({
            't': t,
            't_sq': t ** 2,
            'month_sin': np.sin(2 * np.pi * nm / 12),
            'month_cos': np.cos(2 * np.pi * nm / 12),
            'month': nm,
            'year': ny,
            'label': f"{ny}-{nm:02d}"
        })

    future_df = pd.DataFrame(future_rows)
    X_future = future_df[feature_cols].values
    future_preds = best_model.predict(X_future).tolist()

    # Score : mois actuel = future_preds[0], mois prochain = future_preds[1]
    # comparés aux percentiles de l'historique
    score_label, p33, p66 = compute_score_label(
        future_preds[0], future_preds[1], y
    )

    # Product analysis
    product_analysis = _analyze_products(df)

    # Historical data
    historical = [
        {
            'date': str(row['month_year']),
            'benefice': round(row['benefice'], 2),
            'ca': round(row['ca'], 2),
            'cout': round(row['cout'], 2),
            'nb_ventes': int(row['nb_ventes'])
        }
        for _, row in monthly.iterrows()
    ]

    predictions = [
        {'date': row['label'], 'benefice': round(val, 2)}
        for row, val in zip(future_df.to_dict('records'), future_preds)
    ]

    return {
        'type': 'produit',
        'best_model': best_name,
        'best_model_score': round(best_score, 4),
        'all_model_scores': all_scores,
        'score_label': score_label,
        'score_details': {
            'pred_current_month': round(future_preds[0], 2),
            'pred_next_month': round(future_preds[1], 2),
            'historical_p33': p33,
            'historical_p66': p66,
            'current_month_label': future_df.iloc[0]['label'],
            'next_month_label': future_df.iloc[1]['label'],
        },
        'historical': historical,
        'predictions': predictions,
        'product_analysis': product_analysis,
        'stats': {
            'total_benefice': round(float(sum(y)), 2),
            'avg_mensuel': round(float(np.mean(y)), 2),
            'min_benefice': round(float(np.min(y)), 2),
            'max_benefice': round(float(np.max(y)), 2),
        }
    }


def _analyze_products(df):
    """Analyze products and suggest optimal supply for current month."""
    product_stats = df.groupby('designation').agg(
        total_ventes=('designation', 'count'),
        benefice_total=('benefice', 'sum'),
        benefice_moyen=('benefice', 'mean'),
        prix_achat_moyen=('prix_achat', 'mean'),
        prix_vente_moyen=('prix_vente', 'mean'),
    ).reset_index()

    product_stats['marge_pct'] = (
        (product_stats['prix_vente_moyen'] - product_stats['prix_achat_moyen'])
        / product_stats['prix_achat_moyen'].replace(0, 1) * 100
    )

    # Scoring: combine frequency + marge
    marge_clipped = product_stats['marge_pct'].clip(0)
    marge_max = float(marge_clipped.max()) or 1.0
    ventes_max = float(product_stats['total_ventes'].max()) or 1.0
    product_stats['score'] = (
        product_stats['total_ventes'] / ventes_max * 0.5 +
        marge_clipped / marge_max * 0.5
    )

    product_stats = product_stats.sort_values('score', ascending=False)

    # Monthly trend for each product
    df['month_year_str'] = df['date'].dt.to_period('M').astype(str)
    monthly_product = df.groupby(['designation', 'month_year_str']).size().reset_index(name='count')
    avg_monthly = monthly_product.groupby('designation')['count'].mean()

    recommendations = []
    for _, row in product_stats.iterrows():
        avg = avg_monthly.get(row['designation'], row['total_ventes'])
        suggested_qty = max(1, round(avg * 1.15))  # 15% buffer
        recommendations.append({
            'designation': row['designation'],
            'total_ventes': int(row['total_ventes']),
            'benefice_total': round(float(row['benefice_total']), 2),
            'marge_pct': round(float(row['marge_pct']), 1),
            'prix_vente_moyen': round(float(row['prix_vente_moyen']), 2),
            'approvisionnement_suggere': int(suggested_qty),
            'priorite': 'haute' if row['score'] > 0.66 else ('moyenne' if row['score'] > 0.33 else 'basse')
        })

    return recommendations


def predict_service_seller(df):
    """
    Process service seller CSV: date, depense, revenu
    """
    df.columns = [
        str(c).strip().lower()
        .replace(' ', '_').replace("'", '_')
        .replace('é', 'e').replace('è', 'e').replace('ê', 'e')
        .replace('ô', 'o').replace('à', 'a').replace('ù', 'u')
        for c in df.columns
    ]
    cols = list(df.columns)

    # Flexible col mapping - cherche par mots-clés dans les noms de colonnes
    date_col = next((c for c in cols if 'date' in c), cols[0])
    depense_col = next((c for c in cols if any(k in c for k in ['dep', 'charge', 'cost', 'depense', 'cout'])), cols[1])
    revenu_col = next((c for c in cols if any(k in c for k in ['rev', 'recette', 'revenu', 'chiffre'])), cols[2])

    df = df.rename(columns={date_col: 'date', depense_col: 'depense', revenu_col: 'revenu'})
    df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['date'])
    df['depense'] = pd.to_numeric(df['depense'], errors='coerce').fillna(0)
    df['revenu'] = pd.to_numeric(df['revenu'], errors='coerce').fillna(0)
    df['benefice'] = df['revenu'] - df['depense']

    df['month_year'] = df['date'].dt.to_period('M')
    monthly = df.groupby('month_year').agg(
        benefice=('benefice', 'sum'),
        revenu=('revenu', 'sum'),
        depense=('depense', 'sum'),
    ).reset_index()
    monthly['date'] = monthly['month_year'].dt.to_timestamp()
    monthly = add_time_features(monthly)
    monthly = monthly.sort_values('date')

    feature_cols = ['t', 't_sq', 'month_sin', 'month_cos', 'month']
    X = monthly[feature_cols].values
    y = monthly['benefice'].values

    best_model, best_name, best_score, all_scores = train_best_model(X, y)

    last_t = monthly['t'].max()
    last_year = monthly['date'].max().year
    last_month = monthly['date'].max().month

    future_rows = []
    for i in range(1, 7):
        nm = last_month + i
        ny = last_year + (nm - 1) // 12
        nm = ((nm - 1) % 12) + 1
        t = last_t + i
        future_rows.append({
            't': t,
            't_sq': t ** 2,
            'month_sin': np.sin(2 * np.pi * nm / 12),
            'month_cos': np.cos(2 * np.pi * nm / 12),
            'month': nm,
            'year': ny,
            'label': f"{ny}-{nm:02d}"
        })

    future_df = pd.DataFrame(future_rows)
    X_future = future_df[feature_cols].values
    future_preds = best_model.predict(X_future).tolist()

    score_label, p33, p66 = compute_score_label(
        future_preds[0], future_preds[1], y
    )

    historical = [
        {
            'date': str(row['month_year']),
            'benefice': round(row['benefice'], 2),
            'revenu': round(row['revenu'], 2),
            'depense': round(row['depense'], 2),
        }
        for _, row in monthly.iterrows()
    ]

    predictions = [
        {'date': row['label'], 'benefice': round(val, 2)}
        for row, val in zip(future_df.to_dict('records'), future_preds)
    ]

    return {
        'type': 'service',
        'best_model': best_name,
        'best_model_score': round(best_score, 4),
        'all_model_scores': all_scores,
        'score_label': score_label,
        'score_details': {
            'pred_current_month': round(future_preds[0], 2),
            'pred_next_month': round(future_preds[1], 2),
            'historical_p33': p33,
            'historical_p66': p66,
            'current_month_label': future_df.iloc[0]['label'],
            'next_month_label': future_df.iloc[1]['label'],
        },
        'historical': historical,
        'predictions': predictions,
        'stats': {
            'total_benefice': round(float(sum(y)), 2),
            'avg_mensuel': round(float(np.mean(y)), 2),
            'min_benefice': round(float(np.min(y)), 2),
            'max_benefice': round(float(np.max(y)), 2),
        }
    }