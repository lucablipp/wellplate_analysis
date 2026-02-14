import argparse
from .run_pipeline import run_pipeline

def main():
    parser = argparse.ArgumentParser(
        description = "Run the well plate analysis pipeline from a YAML config file"
    )

    parser.add_argument(
        "config",
        type=str,
        help="Path to YAML configuration file"
    )

    args = parser.parse_args()

    run_pipeline(args.config)

    if __name__ == "__main__":
        main()
