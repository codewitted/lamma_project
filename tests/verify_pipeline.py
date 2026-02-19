import sys
import os
import json
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm_client import LLMClient
from core.schema import validate_json_response
from core.logger import BenchmarkingLogger

class TestPrecisionPipeline(unittest.TestCase):
    def setUp(self):
        self.mock_instruction = "Move the block"
        self.valid_response = json.dumps({
            "tasks": ["move"],
            "objects": ["block"],
            "constraints": [],
            "robots": ["robot1"],
            "goal_predicates": ["at(block, target)"]
        })

    @patch('openai.OpenAI')
    def test_successful_parse_first_try(self, mock_openai):
        # Configure Mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices[0].message.content = self.valid_response
        mock_client.chat.completions.create.return_value = mock_response

        client = LLMClient(provider="ollama", model="test-model")
        result = client.parse_instruction(self.mock_instruction)

        self.assertTrue(result['success'])
        self.assertEqual(result['retries'], 0)
        self.assertEqual(result['data']['tasks'], ["move"])

    @patch('openai.OpenAI')
    def test_retry_on_invalid_json(self, mock_openai):
        # Configure Mock: First call invalid, second valid
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response_invalid = MagicMock()
        mock_response_invalid.choices[0].message.content = "Invalid JSON string"
        
        mock_response_valid = MagicMock()
        mock_response_valid.choices[0].message.content = self.valid_response
        
        mock_client.chat.completions.create.side_effect = [mock_response_invalid, mock_response_valid]

        client = LLMClient(provider="ollama", model="test-model")
        result = client.parse_instruction(self.mock_instruction)

        self.assertTrue(result['success'])
        self.assertEqual(result['retries'], 1)

    @patch('openai.OpenAI')
    @patch('core.llm_client.FALLBACK_TO_CLOUD', True)
    @patch('core.llm_client.CLOUD_FALLBACK_MODEL', 'cloud-model')
    def test_fallback_to_cloud_after_max_retries(self, mock_openai):
        # We need to mock TWO clients: local (fails twice) and cloud (succeeds)
        # However, for simplicity in this test, we can mock the internal call
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Responses for local client (2 failures)
        mock_response_invalid = MagicMock()
        mock_response_invalid.choices[0].message.content = "Fail"
        
        # Response for cloud client (1 success)
        mock_response_valid = MagicMock()
        mock_response_valid.choices[0].message.content = self.valid_response
        
        mock_client.chat.completions.create.side_effect = [
            mock_response_invalid, # Try 0
            mock_response_invalid, # Retry 1
            mock_response_valid    # Fallback Try 0
        ]

        client = LLMClient(provider="ollama", model="local-model")
        result = client.parse_instruction(self.mock_instruction)

        self.assertTrue(result.get('fallback_occurred', False))
        self.assertTrue(result['success'])

if __name__ == "__main__":
    unittest.main()
