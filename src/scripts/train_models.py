import sys
import os
import logging
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
from datetime import datetime
from ..models.predictor import MatchPredictor

def setup_logging():
    """Configure logging for the training script"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Create a timestamp for the log file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f'logs/training_{timestamp}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def plot_confusion_matrix(y_true, y_pred, labels, output_dir):
    """Plot and save confusion matrix"""
    plt.figure(figsize=(10, 8))
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=labels, yticklabels=labels)
    plt.title('Confusion Matrix for Match Outcome Prediction')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    
    # Save the plot
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'confusion_matrix.png'))
    plt.close()

def plot_score_prediction_error(y_true, y_pred, output_dir):
    """Plot and save score prediction error distribution"""
    errors = y_pred - y_true
    
    plt.figure(figsize=(12, 6))
    
    # Home score errors
    plt.subplot(1, 2, 1)
    plt.hist(errors[:, 0], bins=20, alpha=0.7)
    plt.title('Home Score Prediction Error Distribution')
    plt.xlabel('Prediction Error')
    plt.ylabel('Frequency')
    
    # Away score errors
    plt.subplot(1, 2, 2)
    plt.hist(errors[:, 1], bins=20, alpha=0.7)
    plt.title('Away Score Prediction Error Distribution')
    plt.xlabel('Prediction Error')
    plt.ylabel('Frequency')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'score_prediction_error.png'))
    plt.close()

def evaluate_predictions(predictor, test_matches, logger):
    """Evaluate model predictions on test matches"""
    results = []
    for match in test_matches:
        home_team_id = match['home_team_id']
        away_team_id = match['away_team_id']
        actual_outcome = match['outcome']
        actual_score = [match['home_score'], match['away_score']]
        
        prediction = predictor.predict_match(home_team_id, away_team_id)
        if prediction:
            results.append({
                'home_team': prediction['home_team'],
                'away_team': prediction['away_team'],
                'predicted_outcome': prediction['predicted_outcome'],
                'actual_outcome': actual_outcome,
                'predicted_score': prediction['predicted_score'],
                'actual_score': actual_score,
                'outcome_probabilities': prediction['outcome_probabilities']
            })
    
    return results

def main():
    """Main function to train and evaluate models"""
    # Setup logging
    logger = setup_logging()
    logger.info("Starting model training and evaluation")
    
    try:
        # Initialize predictor
        predictor = MatchPredictor()
        logger.info("Predictor initialized successfully")
        
        # Train models
        training_success = predictor.train()
        if not training_success:
            logger.error("Model training failed")
            return
        
        # Create output directory for evaluation results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = f'evaluation_results_{timestamp}'
        os.makedirs(output_dir, exist_ok=True)
        
        # Get test data
        X, y_outcome, y_score = predictor.prepare_training_data()
        X_train, X_test, y_outcome_train, y_outcome_test, y_score_train, y_score_test = predictor.split_and_scale_data(X, y_outcome, y_score)
        
        # Make predictions on test set
        outcome_pred = predictor.outcome_model.predict(X_test)
        score_pred = predictor.score_model.predict(X_test)
        
        # Plot confusion matrix
        plot_confusion_matrix(y_outcome_test, outcome_pred, 
                            labels=['H', 'D', 'A'], output_dir=output_dir)
        
        # Plot score prediction error
        plot_score_prediction_error(y_score_test, score_pred, output_dir=output_dir)
        
        # Save detailed classification report
        report = classification_report(y_outcome_test, outcome_pred)
        with open(os.path.join(output_dir, 'classification_report.txt'), 'w') as f:
            f.write(report)
        
        # Calculate and save additional metrics
        mse_home = np.mean((y_score_test[:, 0] - score_pred[:, 0]) ** 2)
        mse_away = np.mean((y_score_test[:, 1] - score_pred[:, 1]) ** 2)
        
        with open(os.path.join(output_dir, 'score_prediction_metrics.txt'), 'w') as f:
            f.write(f"Mean Squared Error - Home Score: {mse_home:.4f}\n")
            f.write(f"Mean Squared Error - Away Score: {mse_away:.4f}\n")
            f.write(f"Root MSE - Home Score: {np.sqrt(mse_home):.4f}\n")
            f.write(f"Root MSE - Away Score: {np.sqrt(mse_away):.4f}\n")
        
        logger.info(f"Evaluation results saved to directory: {output_dir}")
        
    except Exception as e:
        logger.error(f"Error during model training and evaluation: {str(e)}")
        raise
    finally:
        predictor.close()
        logger.info("Resources cleaned up")

if __name__ == "__main__":
    main() 