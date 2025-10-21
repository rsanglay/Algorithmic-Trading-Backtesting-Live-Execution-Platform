"""
Machine learning models for trading
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
import joblib
import os
from datetime import datetime

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, GRU, Conv1D, MaxPooling1D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset


class TradingModel:
    """Base class for trading ML models"""
    
    def __init__(self, model_type: str, **kwargs):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.feature_columns = None
        self.target_column = None
        
    def fit(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """Fit the model to training data"""
        raise NotImplementedError
        
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")
        raise NotImplementedError
        
    def save(self, filepath: str):
        """Save the model"""
        raise NotImplementedError
        
    def load(self, filepath: str):
        """Load the model"""
        raise NotImplementedError


class SklearnTradingModel(TradingModel):
    """Scikit-learn based trading models"""
    
    def __init__(self, model_type: str, **kwargs):
        super().__init__(model_type, **kwargs)
        self._create_model(**kwargs)
    
    def _create_model(self, **kwargs):
        """Create the appropriate sklearn model"""
        if self.model_type == 'random_forest':
            self.model = RandomForestRegressor(**kwargs)
        elif self.model_type == 'gradient_boosting':
            self.model = GradientBoostingRegressor(**kwargs)
        elif self.model_type == 'extra_trees':
            self.model = ExtraTreesRegressor(**kwargs)
        elif self.model_type == 'linear_regression':
            self.model = LinearRegression(**kwargs)
        elif self.model_type == 'ridge':
            self.model = Ridge(**kwargs)
        elif self.model_type == 'lasso':
            self.model = Lasso(**kwargs)
        elif self.model_type == 'elastic_net':
            self.model = ElasticNet(**kwargs)
        elif self.model_type == 'svr':
            self.model = SVR(**kwargs)
        elif self.model_type == 'mlp':
            self.model = MLPRegressor(**kwargs)
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def fit(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """Fit the model to training data"""
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit model
        self.model.fit(X_scaled, y)
        
        # Store feature columns
        self.feature_columns = X.columns.tolist()
        self.target_column = y.name if hasattr(y, 'name') else 'target'
        self.is_fitted = True
        
        # Calculate training metrics
        y_pred = self.model.predict(X_scaled)
        mse = mean_squared_error(y, y_pred)
        mae = mean_absolute_error(y, y_pred)
        r2 = r2_score(y, y_pred)
        
        return {
            'mse': mse,
            'mae': mae,
            'r2': r2,
            'feature_count': len(self.feature_columns)
        }
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Make predictions
        return self.model.predict(X_scaled)
    
    def save(self, filepath: str):
        """Save the model"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'target_column': self.target_column,
            'is_fitted': self.is_fitted,
            'model_type': self.model_type
        }
        joblib.dump(model_data, filepath)
    
    def load(self, filepath: str):
        """Load the model"""
        model_data = joblib.load(filepath)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']
        self.target_column = model_data['target_column']
        self.is_fitted = model_data['is_fitted']


class LSTMTradingModel(TradingModel):
    """LSTM model for time series prediction"""
    
    def __init__(self, sequence_length: int = 60, **kwargs):
        super().__init__('lstm', **kwargs)
        self.sequence_length = sequence_length
        self.model = None
        self.history = None
    
    def _create_model(self, input_shape: Tuple[int, int], **kwargs):
        """Create LSTM model architecture"""
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(50, return_sequences=True),
            Dropout(0.2),
            LSTM(50),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def _prepare_sequences(self, X: pd.DataFrame, y: pd.Series = None) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare sequences for LSTM"""
        X_scaled = self.scaler.fit_transform(X) if not self.is_fitted else self.scaler.transform(X)
        
        sequences = []
        targets = []
        
        for i in range(self.sequence_length, len(X_scaled)):
            sequences.append(X_scaled[i-self.sequence_length:i])
            if y is not None:
                targets.append(y.iloc[i])
        
        sequences = np.array(sequences)
        targets = np.array(targets) if targets else None
        
        return sequences, targets
    
    def fit(self, X: pd.DataFrame, y: pd.Series, epochs: int = 100, 
            batch_size: int = 32, validation_split: float = 0.2) -> Dict[str, Any]:
        """Fit the LSTM model"""
        # Prepare sequences
        X_seq, y_seq = self._prepare_sequences(X, y)
        
        if X_seq.shape[0] == 0:
            raise ValueError("Not enough data to create sequences")
        
        # Create model
        input_shape = (X_seq.shape[1], X_seq.shape[2])
        self.model = self._create_model(input_shape)
        
        # Callbacks
        callbacks = [
            EarlyStopping(patience=10, restore_best_weights=True),
            ReduceLROnPlateau(patience=5, factor=0.5)
        ]
        
        # Fit model
        self.history = self.model.fit(
            X_seq, y_seq,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=callbacks,
            verbose=0
        )
        
        # Store feature columns
        self.feature_columns = X.columns.tolist()
        self.target_column = y.name if hasattr(y, 'name') else 'target'
        self.is_fitted = True
        
        # Calculate training metrics
        y_pred = self.model.predict(X_seq)
        mse = mean_squared_error(y_seq, y_pred)
        mae = mean_absolute_error(y_seq, y_pred)
        r2 = r2_score(y_seq, y_pred)
        
        return {
            'mse': mse,
            'mae': mae,
            'r2': r2,
            'epochs_trained': len(self.history.history['loss']),
            'feature_count': len(self.feature_columns)
        }
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")
        
        # Prepare sequences
        X_seq, _ = self._prepare_sequences(X)
        
        if X_seq.shape[0] == 0:
            raise ValueError("Not enough data to create sequences")
        
        # Make predictions
        predictions = self.model.predict(X_seq)
        return predictions.flatten()
    
    def save(self, filepath: str):
        """Save the model"""
        if self.model is not None:
            self.model.save(filepath)
        
        # Save additional data
        model_data = {
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'target_column': self.target_column,
            'is_fitted': self.is_fitted,
            'model_type': self.model_type,
            'sequence_length': self.sequence_length
        }
        joblib.dump(model_data, f"{filepath}_metadata.joblib")
    
    def load(self, filepath: str):
        """Load the model"""
        self.model = tf.keras.models.load_model(filepath)
        
        # Load additional data
        model_data = joblib.load(f"{filepath}_metadata.joblib")
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']
        self.target_column = model_data['target_column']
        self.is_fitted = model_data['is_fitted']
        self.sequence_length = model_data['sequence_length']


class EnsembleTradingModel(TradingModel):
    """Ensemble model combining multiple models"""
    
    def __init__(self, models: List[TradingModel], weights: Optional[List[float]] = None):
        super().__init__('ensemble')
        self.models = models
        self.weights = weights or [1.0 / len(models)] * len(models)
        self.is_fitted = False
    
    def fit(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """Fit all models in the ensemble"""
        results = {}
        
        for i, model in enumerate(self.models):
            print(f"Training model {i+1}/{len(self.models)}: {model.model_type}")
            model_results = model.fit(X, y)
            results[f'model_{i+1}'] = model_results
        
        self.is_fitted = True
        return results
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make ensemble predictions"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")
        
        predictions = []
        for model in self.models:
            pred = model.predict(X)
            predictions.append(pred)
        
        # Weighted average
        ensemble_pred = np.average(predictions, axis=0, weights=self.weights)
        return ensemble_pred
    
    def save(self, filepath: str):
        """Save the ensemble model"""
        for i, model in enumerate(self.models):
            model.save(f"{filepath}_model_{i}")
        
        ensemble_data = {
            'weights': self.weights,
            'model_count': len(self.models),
            'is_fitted': self.is_fitted
        }
        joblib.dump(ensemble_data, f"{filepath}_ensemble.joblib")
    
    def load(self, filepath: str):
        """Load the ensemble model"""
        ensemble_data = joblib.load(f"{filepath}_ensemble.joblib")
        self.weights = ensemble_data['weights']
        self.is_fitted = ensemble_data['is_fitted']
        
        # Load individual models
        for i in range(ensemble_data['model_count']):
            # This would need to be implemented based on the specific model types
            pass


class ModelFactory:
    """Factory for creating trading models"""
    
    @staticmethod
    def create_model(model_type: str, **kwargs) -> TradingModel:
        """Create a model of the specified type"""
        if model_type in ['random_forest', 'gradient_boosting', 'extra_trees', 
                          'linear_regression', 'ridge', 'lasso', 'elastic_net', 'svr', 'mlp']:
            return SklearnTradingModel(model_type, **kwargs)
        elif model_type == 'lstm':
            return LSTMTradingModel(**kwargs)
        elif model_type == 'ensemble':
            models = kwargs.get('models', [])
            weights = kwargs.get('weights', None)
            return EnsembleTradingModel(models, weights)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    @staticmethod
    def create_ensemble(models_config: List[Dict[str, Any]], weights: Optional[List[float]] = None) -> EnsembleTradingModel:
        """Create an ensemble model from configuration"""
        models = []
        for config in models_config:
            model_type = config.pop('model_type')
            model = ModelFactory.create_model(model_type, **config)
            models.append(model)
        
        return EnsembleTradingModel(models, weights)
