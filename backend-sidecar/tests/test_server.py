"""Integration tests for the FastAPI server."""

from __future__ import annotations

import base64
import io
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from server import app
from services.ocr import OCRResult


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_base64_image() -> str:
    """Create a sample base64-encoded image for testing."""
    img = Image.new("RGB", (100, 50), color="white")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return base64.b64encode(img_bytes.read()).decode("utf-8")


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_returns_online(self, client: TestClient) -> None:
        """Test health check returns online status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"


class TestProcessImageEndpoint:
    """Tests for the /process-image endpoint."""

    @patch("server.recognize_base64")
    @patch("server.translate")
    @patch("server.tokenize")
    def test_process_image_success(
        self,
        mock_tokenize: MagicMock,
        mock_translate: MagicMock,
        mock_recognize: MagicMock,
        client: TestClient,
        sample_base64_image: str,
    ) -> None:
        """Test successful image processing."""
        mock_recognize.return_value = OCRResult(text="テスト", confidence=0.95)
        mock_translate.return_value = "Test"
        mock_tokenize.return_value = [
            MagicMock(surface="テスト", lemma="テスト", reading="テスト", pos="名詞")
        ]

        response = client.post(
            "/process-image", json={"image": sample_base64_image}
        )

        assert response.status_code == 200
        data = response.json()
        assert "raw_text" in data
        assert "translated_text" in data
        assert "tokens" in data
        assert "confidence" in data
        assert data["raw_text"] == "テスト"
        assert data["translated_text"] == "Test"
        assert len(data["tokens"]) == 1
        assert data["confidence"] == 0.95

    def test_process_image_empty_image(self, client: TestClient) -> None:
        """Test process image with empty image field."""
        response = client.post("/process-image", json={"image": ""})
        assert response.status_code == 400

    def test_process_image_missing_image(self, client: TestClient) -> None:
        """Test process image with missing image field."""
        response = client.post("/process-image", json={})
        assert response.status_code == 422

    @patch("server.recognize_base64")
    def test_process_image_ocr_failure(
        self,
        mock_recognize: MagicMock,
        client: TestClient,
        sample_base64_image: str,
    ) -> None:
        """Test process image when OCR fails."""
        mock_recognize.side_effect = Exception("OCR Error")

        response = client.post(
            "/process-image", json={"image": sample_base64_image}
        )

        assert response.status_code == 500

    @patch("server.recognize_base64")
    @patch("server.translate")
    def test_process_image_empty_ocr_result(
        self,
        mock_translate: MagicMock,
        mock_recognize: MagicMock,
        client: TestClient,
        sample_base64_image: str,
    ) -> None:
        """Test process image when OCR returns empty text."""
        mock_recognize.return_value = OCRResult(text="", confidence=0.0)

        response = client.post(
            "/process-image", json={"image": sample_base64_image}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["raw_text"] == ""
        assert data["translated_text"] == ""
        assert data["tokens"] == []
        assert data["confidence"] == 0.0

    @patch("server.recognize_base64")
    @patch("server.translate")
    @patch("server.tokenize")
    def test_process_image_translation_failure(
        self,
        mock_tokenize: MagicMock,
        mock_translate: MagicMock,
        mock_recognize: MagicMock,
        client: TestClient,
        sample_base64_image: str,
    ) -> None:
        """Test process image when translation fails."""
        mock_recognize.return_value = OCRResult(text="テスト", confidence=0.85)
        mock_translate.side_effect = Exception("Translation Error")
        mock_tokenize.return_value = []

        response = client.post(
            "/process-image", json={"image": sample_base64_image}
        )

        assert response.status_code == 200
        data = response.json()
        assert "translation error" in data["translated_text"].lower()
        assert data["confidence"] == 0.85
