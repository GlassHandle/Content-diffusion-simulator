from pathlib import Path
import json

from Context_Engine.core.orchestrator import ContentUnderstandingEngine


def main() -> None:
    engine = ContentUnderstandingEngine()
    # video_path = Path("video.mp4")
    # image_path = Path("image.png")
    tweet_text = (
        "Just shipped a tiny feature and learned more from the failure than the win. "
        "The build looks simple, but the hard part was getting the system to stay calm."
    )

    # if not video_path.is_file():
    #     raise FileNotFoundError(f"Missing video file: {video_path}")
    # if not image_path.is_file():
    #     raise FileNotFoundError(f"Missing image file: {image_path}")

    results = {
        # "video": engine.analyze(video_path=str(video_path)),
        # "image": engine.analyze(image_path=str(image_path)),
        "tweet": engine.analyze(text=tweet_text),
    }
    print(json.dumps(results["tweet"]["engagement"], indent=2))


if __name__ == "__main__":
    main()