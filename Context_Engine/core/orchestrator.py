from Context_Engine.core.engine import ContentUnderstandingEngine


def main() -> None:
    import json
    import logging

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
    engine = ContentUnderstandingEngine()
    result = engine.analyze(text="I quit my 9-5 to sell candles and honestly? Best decision I never thought I'd make. Here's what nobody warns you about.")
    print("\n--- Content Understanding (Layer 3) ---")
    print(json.dumps(result["engagement"], indent=2))


if __name__ == "__main__":
    main()
