from pathlib import Path
import sys
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from gui_voice_classifier_app import CascadeRandomForestPredictor


MODEL_PATH = PROJECT_ROOT / "model" / "voice_random_forest_model_bundle.joblib"
INPUT_DIR = PROJECT_ROOT / "lab13_dast" / "test_inputs"


@pytest.fixture(scope="session")
def predictor():
    assert MODEL_PATH.exists(), f"Модель не найдена: {MODEL_PATH}"
    return CascadeRandomForestPredictor(MODEL_PATH)


@pytest.mark.parametrize("filename", [
    "normal.wav",
    "short.wav",
])
def test_valid_audio_files_are_processed(predictor, filename):
    audio_path = INPUT_DIR / filename
    assert audio_path.exists(), f"Файл не найден: {audio_path}"

    result = predictor.predict_file(audio_path)

    assert "predicted_label" in result
    assert result["predicted_label"] in [
        "adult_male",
        "adult_female",
        "child_boy",
        "child_girl",
    ]
    assert "probabilities" in result
    assert result["n_windows"] >= 1


@pytest.mark.parametrize("filename", [
    "empty.wav",
    "broken.wav",
    "not_audio.wav",
])
def test_invalid_audio_files_are_handled(predictor, filename):
    audio_path = INPUT_DIR / filename
    assert audio_path.exists(), f"Файл не найден: {audio_path}"

    with pytest.raises(Exception):
        predictor.predict_file(audio_path)