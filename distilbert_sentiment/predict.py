#!/usr/bin/env python3
"""
Sentiment Prediction Script for DistilBERT

Makes sentiment predictions on custom text input.
Supports both command-line and interactive modes.

Usage:
    # Interactive mode (prompt for input)
    python predict.py

    # Predict single sentence
    python predict.py "This movie was amazing!"

    # Multiple sentences (comma-separated)
    python predict.py "Great film,Terrible movie,Not bad"

    # Batch from file
    python predict.py --file sentences.txt

    # Custom model path
    python predict.py --model_path models/checkpoint-1000 "Your text here"

    # Show help
    python predict.py --help
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# Local imports
from src.config import DEVICE, SEED, MODEL_NAME
from src.utils import set_seed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class SentimentPredictor:
    """Production-grade sentiment prediction model."""

    def __init__(self, model_path: str = "models/best_model", device: str = DEVICE, seed: int = SEED):
        """
        Initialize predictor.

        Args:
            model_path: Path to trained model checkpoint
            device: Device to use (cpu, cuda)
            seed: Random seed for reproducibility
        """
        set_seed(seed)
        self.model_path = model_path
        self.device = device
        self.model = None
        self.tokenizer = None
        self.label_names = {0: "NEGATIVE", 1: "POSITIVE"}
        logger.info(f"Initializing predictor with device: {self.device}")

    def load_model_and_tokenizer(self) -> bool:
        """
        Load trained model and tokenizer from checkpoint.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate model path exists
            model_path = Path(self.model_path)
            if not model_path.exists():
                logger.error(f"Model directory not found: {self.model_path}")
                logger.error("Make sure training completed: python train.py")
                return False
            
            config_file = model_path / "config.json"
            if not config_file.exists():
                logger.error(f"Model config not found: {config_file}")
                logger.error("Invalid model checkpoint directory")
                return False
            
            logger.info(f"Loading model from: {self.model_path}")
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
            self.model.to(self.device)
            self.model.eval()
            logger.info("Model loaded successfully")

            logger.info("Loading tokenizer")
            # Load tokenizer from base model (distilbert-base-uncased) if not in saved model
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            except Exception:
                # Fall back to base model tokenizer if not found in saved model
                self.tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
            logger.info("Tokenizer loaded successfully")
            return True

        except FileNotFoundError:
            logger.error(f"Model not found at: {self.model_path}")
            logger.error("Make sure training completed: python train.py")
            return False
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False

    def validate_input(self, text: str) -> Tuple[bool, str]:
        """
        Validate user input.

        Args:
            text: Text to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text:
            return False, "Error: Empty input. Please provide text to analyze."

        if not isinstance(text, str):
            return False, "Error: Input must be text (string)."

        text_stripped = text.strip()
        if not text_stripped:
            return False, "Error: Input contains only whitespace."

        if len(text_stripped) < 3:
            return False, "Error: Input too short. Provide at least 3 characters."

        if len(text_stripped) > 512:
            return False, f"Error: Input too long ({len(text_stripped)} chars). Maximum 512 characters."

        return True, ""

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Predict sentiment for single text input.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with prediction results
        """
        # Validate input
        is_valid, error_msg = self.validate_input(text)
        if not is_valid:
            return {
                "success": False,
                "text": text,
                "error": error_msg,
            }

        try:
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=128,
            )
            
            # Validate tokenizer output has required keys
            required_keys = {"input_ids", "attention_mask"}
            if not required_keys.issubset(inputs.keys()):
                logger.error(f"Tokenizer output missing keys. Got: {inputs.keys()}, Expected: {required_keys}")
                return {
                    "success": False,
                    "text": text,
                    "error": "Tokenizer error: missing required output keys",
                }

            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Predict
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                
                # Validate logits shape (should be [1, 2] for single sample, binary classification)
                if logits.shape[0] != 1 or logits.shape[1] != 2:
                    logger.error(f"Unexpected logits shape: {logits.shape}. Expected [1, 2]")
                    return {
                        "success": False,
                        "text": text,
                        "error": f"Model output error: unexpected shape {logits.shape}",
                    }
                
                probabilities = torch.softmax(logits, dim=-1)

            # Extract results
            pred_label = torch.argmax(logits, dim=-1).item()
            negative_prob = probabilities[0, 0].item()
            positive_prob = probabilities[0, 1].item()
            confidence = max(negative_prob, positive_prob)

            result = {
                "success": True,
                "text": text,
                "label": self.label_names[pred_label],
                "confidence": float(confidence),
                "probabilities": {
                    "NEGATIVE": float(negative_prob),
                    "POSITIVE": float(positive_prob),
                },
                "prediction_id": pred_label,
            }

            return result

        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            return {
                "success": False,
                "text": text,
                "error": f"Prediction failed: {str(e)}",
            }

    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Predict sentiment for multiple texts.

        Args:
            texts: List of texts to analyze

        Returns:
            List of prediction results
        """
        logger.info(f"Processing batch of {len(texts)} samples")
        results = [self.predict(text) for text in texts]
        logger.info("Batch processing complete")
        return results

    def print_prediction(self, result: Dict[str, Any], show_probabilities: bool = True) -> None:
        """
        Pretty-print prediction result.

        Args:
            result: Prediction result dictionary
            show_probabilities: Whether to show detailed probabilities
        """
        if not result["success"]:
            print(f"\n❌ {result['error']}")
            return

        text = result["text"]
        if len(text) > 100:
            text = text[:97] + "..."

        print("\n" + "=" * 80)
        print("PREDICTION RESULT")
        print("=" * 80)
        print(f"Text:       {text}")
        print(f"Sentiment:  {result['label']}")
        print(f"Confidence: {result['confidence']:.2%}")

        if show_probabilities:
            print(f"\nDetailed Probabilities:")
            for label, prob in result["probabilities"].items():
                bar_width = int(prob * 40)
                bar = "█" * bar_width + "░" * (40 - bar_width)
                print(f"  {label:10} {prob:.4f} ({prob:.2%}) [{bar}]")

        print("=" * 80 + "\n")

    def print_batch_results(self, results: List[Dict[str, Any]], show_probabilities: bool = False) -> None:
        """
        Pretty-print batch prediction results.

        Args:
            results: List of prediction results
            show_probabilities: Whether to show detailed probabilities
        """
        print("\n" + "=" * 80)
        print("BATCH PREDICTION RESULTS")
        print("=" * 80)

        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful

        print(f"Total: {len(results)} | Successful: {successful} | Failed: {failed}\n")

        for i, result in enumerate(results, 1):
            if result["success"]:
                text = result["text"][:50] + "..." if len(result["text"]) > 50 else result["text"]
                print(
                    f"{i:2d}. [{result['label']:8}] {result['confidence']:6.1%} | {text}"
                )
                if show_probabilities:
                    neg_prob = result["probabilities"]["NEGATIVE"]
                    pos_prob = result["probabilities"]["POSITIVE"]
                    print(f"     NEGATIVE: {neg_prob:.4f} ({neg_prob:.2%}) | POSITIVE: {pos_prob:.4f} ({pos_prob:.2%})")
            else:
                print(f"{i:2d}. [ERROR] {result['error']}")

        print("=" * 80 + "\n")

    def interactive_mode(self, show_probabilities: bool = True) -> None:
        """Run interactive prediction mode.
        
        Args:
            show_probabilities: Whether to show detailed probability breakdown
        """
        print("\n" + "=" * 80)
        print("INTERACTIVE SENTIMENT ANALYSIS")
        print("=" * 80)
        print("Enter text to analyze (or 'quit' to exit)\n")

        while True:
            try:
                user_input = input(">> ").strip()

                if user_input.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break

                if not user_input:
                    print("Please enter some text.\n")
                    continue

                result = self.predict(user_input)
                self.print_prediction(result, show_probabilities=show_probabilities)

            except KeyboardInterrupt:
                print("\n\nInterrupted by user. Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                print(f"Error: {e}\n")


def main():
    """Main prediction function."""
    parser = argparse.ArgumentParser(
        description="Sentiment prediction using DistilBERT",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive mode:
    python predict.py

  Single prediction:
    python predict.py "This movie was amazing!"

  Multiple sentences (comma-separated):
    python predict.py "Great!,Terrible,Not bad"

  Batch from file:
    python predict.py --file sentences.txt

  Custom model:
    python predict.py --model_path models/checkpoint-1000 "Your text"

  Test mode (predefined examples):
    python predict.py --test
        """,
    )

    parser.add_argument(
        "text",
        nargs="?",
        default=None,
        help="Text to analyze (optional, triggers interactive mode if omitted)",
    )
    parser.add_argument(
        "--model_path",
        type=str,
        default="models/best_model",
        help="Path to trained model checkpoint (default: models/best_model)",
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Path to file with sentences (one per line)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run with predefined test examples",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=DEVICE,
        choices=["cpu", "cuda"],
        help=f"Device to use (default: {DEVICE})",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=SEED,
        help=f"Random seed (default: {SEED})",
    )
    parser.add_argument(
        "--no-probabilities",
        action="store_true",
        help="Hide detailed probability breakdown",
    )

    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("DISTILBERT SENTIMENT PREDICTION")
    logger.info("=" * 80)
    logger.info(f"Model path: {args.model_path}")
    logger.info(f"Device: {args.device}")
    logger.info("=" * 80)

    # Initialize predictor
    predictor = SentimentPredictor(
        model_path=args.model_path,
        device=args.device,
        seed=args.seed,
    )

    # Load model
    if not predictor.load_model_and_tokenizer():
        logger.error("Failed to load model")
        return 1

    show_probabilities = not args.no_probabilities

    # Mode 1: Test with predefined examples
    if args.test:
        logger.info("Running in test mode")
        test_texts = [
            "This movie is absolutely fantastic! Best film I've ever seen!",
            "Terrible waste of time. Horrible acting and boring plot.",
            "It was okay, nothing special but watchable.",
            "Amazing cinematography and brilliant performances!",
            "Don't bother watching this. Absolutely dreadful.",
            "Pretty good, would recommend to friends.",
            "The worst movie ever made. Complete disaster.",
            "I loved every second of it!",
            "Mediocre at best. Very disappointing.",
            "Outstanding masterpiece! A true classic!",
        ]
        results = predictor.predict_batch(test_texts)
        predictor.print_batch_results(results, show_probabilities=show_probabilities)
        return 0

    # Mode 2: Batch from file
    if args.file:
        logger.info(f"Reading from file: {args.file}")
        try:
            file_path = Path(args.file)
            if not file_path.exists():
                logger.error(f"File not found: {args.file}")
                return 1

            with open(file_path, "r") as f:
                texts = [line.strip() for line in f if line.strip()]

            if not texts:
                logger.error("File is empty")
                return 1

            results = predictor.predict_batch(texts)
            predictor.print_batch_results(results, show_probabilities=show_probabilities)
            return 0

        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return 1

    # Mode 3: Single prediction from command line
    if args.text:
        logger.info("Single prediction mode")
        # Handle comma-separated texts
        if "," in args.text:
            texts = [t.strip() for t in args.text.split(",")]
            results = predictor.predict_batch(texts)
            predictor.print_batch_results(results, show_probabilities=show_probabilities)
        else:
            result = predictor.predict(args.text)
            predictor.print_prediction(result, show_probabilities=show_probabilities)
        return 0

    # Mode 4: Interactive mode
    logger.info("Interactive mode")
    predictor.interactive_mode(show_probabilities=show_probabilities)
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
