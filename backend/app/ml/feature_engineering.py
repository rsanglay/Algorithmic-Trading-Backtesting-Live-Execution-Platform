"""
Feature engineering for trading strategies
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import ta
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.feature_selection import SelectKBest, f_regression, mutual_info_regression
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor


class FeatureEngineer:
    """Feature engineering for trading data"""
    
    def __init__(self):
        self.scalers = {}
        self.feature_selectors = {}
        self.pca_models = {}
    
    def create_technical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create technical indicators as features"""
        features_df = df.copy()
        
        # Price-based features
        features_df['returns'] = df['close'].pct_change()
        features_df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        features_df['price_change'] = df['close'] - df['open']
        features_df['price_range'] = df['high'] - df['low']
        features_df['body_size'] = abs(df['close'] - df['open'])
        features_df['upper_shadow'] = df['high'] - np.maximum(df['open'], df['close'])
        features_df['lower_shadow'] = np.minimum(df['open'], df['close']) - df['low']
        
        # Moving averages
        for window in [5, 10, 20, 50, 100]:
            features_df[f'sma_{window}'] = ta.trend.sma_indicator(df['close'], window=window)
            features_df[f'ema_{window}'] = ta.trend.ema_indicator(df['close'], window=window)
            features_df[f'price_sma_{window}_ratio'] = df['close'] / features_df[f'sma_{window}']
            features_df[f'price_ema_{window}_ratio'] = df['close'] / features_df[f'ema_{window}']
        
        # Momentum indicators
        features_df['rsi'] = ta.momentum.rsi(df['close'], window=14)
        features_df['rsi_30'] = ta.momentum.rsi(df['close'], window=30)
        features_df['stoch_k'] = ta.momentum.stoch(df['high'], df['low'], df['close'])
        features_df['stoch_d'] = ta.momentum.stoch_signal(df['high'], df['low'], df['close'])
        features_df['williams_r'] = ta.momentum.williams_r(df['high'], df['low'], df['close'])
        features_df['roc'] = ta.momentum.roc(df['close'], window=10)
        
        # Trend indicators
        features_df['macd'] = ta.trend.macd(df['close'])
        features_df['macd_signal'] = ta.trend.macd_signal(df['close'])
        features_df['macd_histogram'] = ta.trend.macd_diff(df['close'])
        features_df['adx'] = ta.trend.adx(df['high'], df['low'], df['close'])
        features_df['cci'] = ta.trend.cci(df['high'], df['low'], df['close'])
        features_df['aroon_up'] = ta.trend.aroon_up(df['close'])
        features_df['aroon_down'] = ta.trend.aroon_down(df['close'])
        
        # Volatility indicators
        features_df['bb_upper'] = ta.volatility.bollinger_hband(df['close'])
        features_df['bb_middle'] = ta.volatility.bollinger_mavg(df['close'])
        features_df['bb_lower'] = ta.volatility.bollinger_lband(df['close'])
        features_df['bb_width'] = (features_df['bb_upper'] - features_df['bb_lower']) / features_df['bb_middle']
        features_df['bb_position'] = (df['close'] - features_df['bb_lower']) / (features_df['bb_upper'] - features_df['bb_lower'])
        features_df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'])
        features_df['natr'] = ta.volatility.normalized_average_true_range(df['high'], df['low'], df['close'])
        features_df['keltner_upper'] = ta.volatility.keltner_channel_hband(df['high'], df['low'], df['close'])
        features_df['keltner_middle'] = ta.volatility.keltner_channel_mband(df['high'], df['low'], df['close'])
        features_df['keltner_lower'] = ta.volatility.keltner_channel_lband(df['high'], df['low'], df['close'])
        
        # Volume indicators
        features_df['volume_sma'] = ta.volume.volume_sma(df['close'], df['volume'])
        features_df['volume_ratio'] = df['volume'] / features_df['volume_sma']
        features_df['obv'] = ta.volume.on_balance_volume(df['close'], df['volume'])
        features_df['ad'] = ta.volume.acc_dist_index(df['high'], df['low'], df['close'], df['volume'])
        features_df['mfi'] = ta.volume.money_flow_index(df['high'], df['low'], df['close'], df['volume'])
        features_df['vwap'] = ta.volume.volume_weighted_average_price(df['high'], df['low'], df['close'], df['volume'])
        
        # Lagged features
        for lag in [1, 2, 3, 5, 10]:
            features_df[f'close_lag_{lag}'] = df['close'].shift(lag)
            features_df[f'volume_lag_{lag}'] = df['volume'].shift(lag)
            features_df[f'returns_lag_{lag}'] = features_df['returns'].shift(lag)
        
        # Rolling statistics
        for window in [5, 10, 20]:
            features_df[f'returns_std_{window}'] = features_df['returns'].rolling(window=window).std()
            features_df[f'returns_skew_{window}'] = features_df['returns'].rolling(window=window).skew()
            features_df[f'returns_kurt_{window}'] = features_df['returns'].rolling(window=window).kurt()
            features_df[f'volume_std_{window}'] = df['volume'].rolling(window=window).std()
            features_df[f'volume_mean_{window}'] = df['volume'].rolling(window=window).mean()
        
        return features_df
    
    def create_market_microstructure_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create market microstructure features"""
        features_df = df.copy()
        
        # Bid-ask spread proxy (using high-low range)
        features_df['spread_proxy'] = (df['high'] - df['low']) / df['close']
        
        # Price impact proxy
        features_df['price_impact'] = abs(df['close'] - df['open']) / df['volume']
        
        # Volatility clustering
        features_df['volatility_cluster'] = features_df['returns'].rolling(window=5).std()
        
        # Market depth proxy
        features_df['depth_proxy'] = df['volume'] / (df['high'] - df['low'])
        
        # Order flow imbalance proxy
        features_df['flow_imbalance'] = (df['close'] - df['open']) / (df['high'] - df['low'])
        
        return features_df
    
    def create_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create time-based features"""
        features_df = df.copy()
        
        if 'timestamp' in df.columns:
            features_df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            features_df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
            features_df['day_of_month'] = pd.to_datetime(df['timestamp']).dt.day
            features_df['month'] = pd.to_datetime(df['timestamp']).dt.month
            features_df['quarter'] = pd.to_datetime(df['timestamp']).dt.quarter
            
            # Cyclical encoding
            features_df['hour_sin'] = np.sin(2 * np.pi * features_df['hour'] / 24)
            features_df['hour_cos'] = np.cos(2 * np.pi * features_df['hour'] / 24)
            features_df['day_sin'] = np.sin(2 * np.pi * features_df['day_of_week'] / 7)
            features_df['day_cos'] = np.cos(2 * np.pi * features_df['day_of_week'] / 7)
            features_df['month_sin'] = np.sin(2 * np.pi * features_df['month'] / 12)
            features_df['month_cos'] = np.cos(2 * np.pi * features_df['month'] / 12)
        
        return features_df
    
    def create_cross_asset_features(self, df: pd.DataFrame, reference_assets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Create cross-asset features"""
        features_df = df.copy()
        
        for asset_name, asset_df in reference_assets.items():
            # Align data by timestamp
            aligned_asset = asset_df.reindex(df.index, method='ffill')
            
            # Relative performance
            features_df[f'{asset_name}_returns'] = aligned_asset['close'].pct_change()
            features_df[f'{asset_name}_relative_performance'] = features_df['returns'] - features_df[f'{asset_name}_returns']
            
            # Correlation features
            features_df[f'{asset_name}_correlation'] = features_df['returns'].rolling(window=20).corr(features_df[f'{asset_name}_returns'])
            
            # Relative volatility
            features_df[f'{asset_name}_vol_ratio'] = features_df['returns'].rolling(window=20).std() / features_df[f'{asset_name}_returns'].rolling(window=20).std()
        
        return features_df
    
    def create_sentiment_features(self, df: pd.DataFrame, news_data: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Create sentiment-based features"""
        features_df = df.copy()
        
        if news_data is not None:
            # Align news data with price data
            news_aligned = news_data.reindex(df.index, method='ffill')
            
            # Sentiment features
            features_df['sentiment_score'] = news_aligned['sentiment_score']
            features_df['sentiment_ma'] = news_aligned['sentiment_score'].rolling(window=5).mean()
            features_df['sentiment_std'] = news_aligned['sentiment_score'].rolling(window=5).std()
            
            # News volume features
            features_df['news_count'] = news_aligned['news_count'] if 'news_count' in news_aligned.columns else 0
            features_df['news_volume'] = news_aligned['news_volume'] if 'news_volume' in news_aligned.columns else 0
        
        return features_df
    
    def scale_features(self, df: pd.DataFrame, feature_columns: List[str], 
                      scaler_type: str = 'standard', fit: bool = True) -> pd.DataFrame:
        """Scale features using specified scaler"""
        scaled_df = df.copy()
        
        if scaler_type == 'standard':
            scaler = StandardScaler()
        elif scaler_type == 'minmax':
            scaler = MinMaxScaler()
        elif scaler_type == 'robust':
            scaler = RobustScaler()
        else:
            raise ValueError(f"Unknown scaler type: {scaler_type}")
        
        if fit:
            scaled_features = scaler.fit_transform(df[feature_columns])
            self.scalers[scaler_type] = scaler
        else:
            if scaler_type not in self.scalers:
                raise ValueError(f"Scaler {scaler_type} not fitted")
            scaled_features = self.scalers[scaler_type].transform(df[feature_columns])
        
        # Update DataFrame with scaled features
        for i, col in enumerate(feature_columns):
            scaled_df[f'{col}_scaled'] = scaled_features[:, i]
        
        return scaled_df
    
    def select_features(self, X: pd.DataFrame, y: pd.Series, method: str = 'mutual_info', 
                       k: int = 20) -> pd.DataFrame:
        """Select top k features using specified method"""
        if method == 'mutual_info':
            selector = SelectKBest(score_func=mutual_info_regression, k=k)
        elif method == 'f_regression':
            selector = SelectKBest(score_func=f_regression, k=k)
        else:
            raise ValueError(f"Unknown selection method: {method}")
        
        # Fit selector
        X_selected = selector.fit_transform(X, y)
        selected_features = X.columns[selector.get_support()].tolist()
        
        # Store selector for later use
        self.feature_selectors[method] = selector
        
        return pd.DataFrame(X_selected, columns=selected_features, index=X.index)
    
    def apply_pca(self, X: pd.DataFrame, n_components: int = 10, fit: bool = True) -> pd.DataFrame:
        """Apply PCA dimensionality reduction"""
        pca = PCA(n_components=n_components)
        
        if fit:
            X_pca = pca.fit_transform(X)
            self.pca_models['pca'] = pca
        else:
            if 'pca' not in self.pca_models:
                raise ValueError("PCA model not fitted")
            X_pca = self.pca_models['pca'].transform(X)
        
        # Create DataFrame with PCA components
        pca_columns = [f'pca_{i}' for i in range(n_components)]
        return pd.DataFrame(X_pca, columns=pca_columns, index=X.index)
    
    def create_feature_importance(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """Calculate feature importance using Random Forest"""
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf.fit(X, y)
        
        feature_importance = dict(zip(X.columns, rf.feature_importances_))
        return dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
    
    def create_all_features(self, df: pd.DataFrame, reference_assets: Optional[Dict[str, pd.DataFrame]] = None,
                          news_data: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Create all available features"""
        # Start with technical features
        features_df = self.create_technical_features(df)
        
        # Add microstructure features
        features_df = self.create_market_microstructure_features(features_df)
        
        # Add time features
        features_df = self.create_time_features(features_df)
        
        # Add cross-asset features if available
        if reference_assets:
            features_df = self.create_cross_asset_features(features_df, reference_assets)
        
        # Add sentiment features if available
        if news_data is not None:
            features_df = self.create_sentiment_features(features_df, news_data)
        
        return features_df
