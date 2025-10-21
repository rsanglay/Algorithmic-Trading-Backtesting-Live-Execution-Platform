"""
Strategy optimization using machine learning
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from sklearn.model_selection import ParameterGrid
from sklearn.metrics import make_scorer
import optuna
from optuna.samplers import TPESampler
from optuna.pruners import MedianPruner

from app.ml.models import ModelFactory, TradingModel
from app.ml.feature_engineering import FeatureEngineer


class StrategyOptimizer:
    """Optimize trading strategy parameters using ML"""
    
    def __init__(self, strategy_class, feature_engineer: FeatureEngineer = None):
        self.strategy_class = strategy_class
        self.feature_engineer = feature_engineer or FeatureEngineer()
        self.best_params = None
        self.best_score = None
        self.optimization_history = []
    
    def grid_search_optimization(self, param_grid: Dict[str, List], 
                               X: pd.DataFrame, y: pd.Series,
                               scoring: str = 'neg_mean_squared_error',
                               cv: int = 5) -> Dict[str, Any]:
        """Perform grid search optimization"""
        best_score = -np.inf
        best_params = None
        results = []
        
        for params in ParameterGrid(param_grid):
            # Create strategy with parameters
            strategy = self.strategy_class(**params)
            
            # Calculate cross-validation score
            scores = self._evaluate_strategy(strategy, X, y, cv, scoring)
            mean_score = np.mean(scores)
            
            results.append({
                'params': params,
                'mean_score': mean_score,
                'std_score': np.std(scores),
                'scores': scores
            })
            
            if mean_score > best_score:
                best_score = mean_score
                best_params = params
        
        self.best_params = best_params
        self.best_score = best_score
        self.optimization_history = results
        
        return {
            'best_params': best_params,
            'best_score': best_score,
            'all_results': results
        }
    
    def bayesian_optimization(self, param_space: Dict[str, Any], 
                            X: pd.DataFrame, y: pd.Series,
                            n_trials: int = 100, cv: int = 5,
                            scoring: str = 'neg_mean_squared_error') -> Dict[str, Any]:
        """Perform Bayesian optimization using Optuna"""
        
        def objective(trial):
            # Sample parameters from the space
            params = {}
            for param_name, param_config in param_space.items():
                if param_config['type'] == 'categorical':
                    params[param_name] = trial.suggest_categorical(param_name, param_config['choices'])
                elif param_config['type'] == 'int':
                    params[param_name] = trial.suggest_int(param_name, param_config['low'], param_config['high'])
                elif param_config['type'] == 'float':
                    params[param_name] = trial.suggest_float(param_name, param_config['low'], param_config['high'])
                elif param_config['type'] == 'log_float':
                    params[param_name] = trial.suggest_loguniform(param_name, param_config['low'], param_config['high'])
            
            # Create strategy with parameters
            strategy = self.strategy_class(**params)
            
            # Evaluate strategy
            scores = self._evaluate_strategy(strategy, X, y, cv, scoring)
            return np.mean(scores)
        
        # Create study
        study = optuna.create_study(
            direction='maximize',
            sampler=TPESampler(),
            pruner=MedianPruner()
        )
        
        # Optimize
        study.optimize(objective, n_trials=n_trials)
        
        self.best_params = study.best_params
        self.best_score = study.best_value
        
        return {
            'best_params': study.best_params,
            'best_score': study.best_value,
            'n_trials': len(study.trials),
            'optimization_history': study.trials
        }
    
    def _evaluate_strategy(self, strategy, X: pd.DataFrame, y: pd.Series, 
                          cv: int, scoring: str) -> List[float]:
        """Evaluate a strategy using cross-validation"""
        from sklearn.model_selection import cross_val_score
        
        # This would need to be implemented based on the specific strategy class
        # For now, return dummy scores
        return np.random.random(cv)
    
    def walk_forward_optimization(self, data: pd.DataFrame, 
                                 param_space: Dict[str, Any],
                                 train_window: int = 252, 
                                 test_window: int = 63,
                                 step_size: int = 21) -> Dict[str, Any]:
        """Perform walk-forward optimization"""
        results = []
        
        for start_idx in range(0, len(data) - train_window - test_window, step_size):
            # Define train and test periods
            train_end = start_idx + train_window
            test_start = train_end
            test_end = test_start + test_window
            
            train_data = data.iloc[start_idx:train_end]
            test_data = data.iloc[test_start:test_end]
            
            # Optimize parameters on training data
            optimization_result = self.bayesian_optimization(
                param_space, train_data, train_data['target'], n_trials=50
            )
            
            # Test on out-of-sample data
            best_strategy = self.strategy_class(**optimization_result['best_params'])
            test_score = self._evaluate_strategy(best_strategy, test_data, test_data['target'], 1, 'neg_mean_squared_error')[0]
            
            results.append({
                'train_period': (start_idx, train_end),
                'test_period': (test_start, test_end),
                'best_params': optimization_result['best_params'],
                'test_score': test_score
            })
        
        return {
            'walk_forward_results': results,
            'average_test_score': np.mean([r['test_score'] for r in results]),
            'test_score_std': np.std([r['test_score'] for r in results])
        }


class MLStrategyOptimizer:
    """Optimize ML model hyperparameters for trading strategies"""
    
    def __init__(self, model_type: str, feature_engineer: FeatureEngineer = None):
        self.model_type = model_type
        self.feature_engineer = feature_engineer or FeatureEngineer()
        self.best_model = None
        self.best_params = None
        self.optimization_history = []
    
    def optimize_hyperparameters(self, X: pd.DataFrame, y: pd.Series,
                               param_space: Dict[str, Any],
                               n_trials: int = 100, cv: int = 5,
                               scoring: str = 'neg_mean_squared_error') -> Dict[str, Any]:
        """Optimize hyperparameters using Optuna"""
        
        def objective(trial):
            # Sample hyperparameters
            params = {}
            for param_name, param_config in param_space.items():
                if param_config['type'] == 'categorical':
                    params[param_name] = trial.suggest_categorical(param_name, param_config['choices'])
                elif param_config['type'] == 'int':
                    params[param_name] = trial.suggest_int(param_name, param_config['low'], param_config['high'])
                elif param_config['type'] == 'float':
                    params[param_name] = trial.suggest_float(param_name, param_config['low'], param_config['high'])
                elif param_config['type'] == 'log_float':
                    params[param_name] = trial.suggest_loguniform(param_name, param_config['low'], param_config['high'])
            
            # Create model with parameters
            model = ModelFactory.create_model(self.model_type, **params)
            
            # Evaluate model
            scores = self._evaluate_model(model, X, y, cv, scoring)
            return np.mean(scores)
        
        # Create study
        study = optuna.create_study(
            direction='maximize',
            sampler=TPESampler(),
            pruner=MedianPruner()
        )
        
        # Optimize
        study.optimize(objective, n_trials=n_trials)
        
        # Create best model
        self.best_model = ModelFactory.create_model(self.model_type, **study.best_params)
        self.best_params = study.best_params
        
        return {
            'best_params': study.best_params,
            'best_score': study.best_value,
            'n_trials': len(study.trials),
            'optimization_history': study.trials
        }
    
    def _evaluate_model(self, model: TradingModel, X: pd.DataFrame, y: pd.Series,
                        cv: int, scoring: str) -> List[float]:
        """Evaluate model using cross-validation"""
        from sklearn.model_selection import cross_val_score
        from sklearn.metrics import make_scorer
        
        # Create scorer
        if scoring == 'neg_mean_squared_error':
            scorer = make_scorer(lambda y_true, y_pred: -np.mean((y_true - y_pred) ** 2))
        elif scoring == 'neg_mean_absolute_error':
            scorer = make_scorer(lambda y_true, y_pred: -np.mean(np.abs(y_true - y_pred)))
        else:
            scorer = scoring
        
        # Perform cross-validation
        scores = []
        for train_idx, val_idx in self._create_time_series_cv(X, cv):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            
            # Fit model
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_val)
            
            # Calculate score
            score = scorer(y_val, y_pred)
            scores.append(score)
        
        return scores
    
    def _create_time_series_cv(self, X: pd.DataFrame, cv: int) -> List[Tuple[np.ndarray, np.ndarray]]:
        """Create time series cross-validation splits"""
        n_samples = len(X)
        fold_size = n_samples // cv
        
        splits = []
        for i in range(cv):
            train_end = (i + 1) * fold_size
            val_start = train_end
            val_end = min(val_start + fold_size, n_samples)
            
            train_idx = np.arange(0, train_end)
            val_idx = np.arange(val_start, val_end)
            
            splits.append((train_idx, val_idx))
        
        return splits
    
    def optimize_feature_selection(self, X: pd.DataFrame, y: pd.Series,
                                 feature_selection_methods: List[str] = ['mutual_info', 'f_regression'],
                                 k_values: List[int] = [10, 20, 50, 100]) -> Dict[str, Any]:
        """Optimize feature selection"""
        best_score = -np.inf
        best_config = None
        results = []
        
        for method in feature_selection_methods:
            for k in k_values:
                # Select features
                X_selected = self.feature_engineer.select_features(X, y, method=method, k=k)
                
                # Evaluate with simple model
                model = ModelFactory.create_model('random_forest', n_estimators=100)
                scores = self._evaluate_model(model, X_selected, y, 5, 'neg_mean_squared_error')
                mean_score = np.mean(scores)
                
                results.append({
                    'method': method,
                    'k': k,
                    'mean_score': mean_score,
                    'std_score': np.std(scores),
                    'selected_features': X_selected.columns.tolist()
                })
                
                if mean_score > best_score:
                    best_score = mean_score
                    best_config = {'method': method, 'k': k}
        
        return {
            'best_config': best_config,
            'best_score': best_score,
            'all_results': results
        }
    
    def optimize_ensemble(self, X: pd.DataFrame, y: pd.Series,
                         model_configs: List[Dict[str, Any]],
                         weight_optimization: bool = True) -> Dict[str, Any]:
        """Optimize ensemble model"""
        # Train individual models
        models = []
        for config in model_configs:
            model_type = config.pop('model_type')
            model = ModelFactory.create_model(model_type, **config)
            model.fit(X, y)
            models.append(model)
        
        # Optimize weights if requested
        if weight_optimization:
            weights = self._optimize_ensemble_weights(models, X, y)
        else:
            weights = [1.0 / len(models)] * len(models)
        
        # Create ensemble
        ensemble = ModelFactory.create_ensemble(
            [{'model_type': m.model_type} for m in models],
            weights
        )
        
        # Evaluate ensemble
        ensemble_scores = self._evaluate_model(ensemble, X, y, 5, 'neg_mean_squared_error')
        
        return {
            'ensemble_models': [m.model_type for m in models],
            'weights': weights,
            'mean_score': np.mean(ensemble_scores),
            'std_score': np.std(ensemble_scores)
        }
    
    def _optimize_ensemble_weights(self, models: List[TradingModel], 
                                 X: pd.DataFrame, y: pd.Series) -> List[float]:
        """Optimize ensemble weights using linear regression"""
        from sklearn.linear_model import LinearRegression
        
        # Get predictions from all models
        predictions = []
        for model in models:
            pred = model.predict(X)
            predictions.append(pred)
        
        # Stack predictions
        X_ensemble = np.column_stack(predictions)
        
        # Fit linear regression to find optimal weights
        lr = LinearRegression()
        lr.fit(X_ensemble, y)
        
        # Normalize weights to sum to 1
        weights = lr.coef_
        weights = weights / np.sum(weights)
        
        return weights.tolist()
