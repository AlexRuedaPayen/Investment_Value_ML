import unittest
from unittest.mock import MagicMock, patch
from utils import DotDict
from Google_API.Google_Drive_Handler import Google_Drive_Handler
import pytest


@pytest.mark.mock
class TestGoogleDriveHandlerMock(unittest.TestCase):
    def setUp(self):
        """
        Set up a mock Google_Drive_Handler instance for testing.
        """
        self.root_folder_id = "mock_root_folder_id"
        self.handler = Google_Drive_Handler(
            root_folder_id=self.root_folder_id,
            log_dir="./mock_logfiles",
            token_path="./secrets/Google_Drive/token.json",
            credentials_path="./secrets/Google_Drive/creds.json"
        )
        self.handler.service = MagicMock()  # Mock the service object

    @patch("Google_API.Google_Drive_Handler.Google_Drive_Handler.authenticate")
    def test_authenticate(self, mock_authenticate):
        """
        Test the authenticate method with mocks.
        """
        mock_authenticate.return_value = None  # Simulate successful authentication
        self.handler.authenticate()
        mock_authenticate.assert_called_once()

    def test_upload_file(self):
        """
        Test the upload_file method with mocks.
        """
        # Mock the create method of the files API
        mock_file_create = self.handler.service.files().create
        mock_file_create.return_value.execute.return_value = {"id": "mock_file_id"}

        file_path = "mock_file.txt"
        folder_id = "mock_folder_id"
        self.handler.upload_file(file_path, folder_id)

        # Check that the service.files().create method was called with expected arguments
        mock_file_create.assert_called_once()
        args, kwargs = mock_file_create.call_args
        self.assertEqual(kwargs["body"]["name"], "mock_file.txt")
        self.assertEqual(kwargs["body"]["parents"], [folder_id])

    def test_list_files_by_pattern(self):
        """
        Test the list_files_by_pattern method with mocks.
        """
        # Mock the list method of the files API
        mock_files_list = self.handler.service.files().list
        mock_files_list.return_value.execute.return_value = {
            "files": [{"name": "mock_file___data.txt"}]
        }

        files = self.handler.list_files_by_pattern()
        self.assertEqual(files, (["mock_file", "data"],))

    @patch("shutil.rmtree")
    def test_remove_folder(self, mock_rmtree):
        """
        Test the remove_folder method with mocks.
        """
        folder_path = "mock_folder"
        self.handler.remove_folder(folder_path)
        mock_rmtree.assert_called_once_with(folder_path)

    def test_get_folder_id(self):
        """
        Test the get_folder_id method with mocks.
        """
        # Mock API responses for country and exchange folders
        mock_files_list = self.handler.service.files().list
        mock_files_list.side_effect = [
            {"files": [{"id": DotDict("secrets/Google_Drive/folder_ids.json").USA.NASDAQ}]},
            {"files": [{"id": DotDict("secrets/Google_Drive/folder_ids.json").USA.NASDAQ}]},
        ]

        folder_id = self.handler.get_folder_id("USA", "NASDAQ")
        self.assertEqual(folder_id, DotDict("secrets/Google_Drive/folder_ids.json").USA.NASDAQ)

        # Verify queries made to the service.files().list method
        calls = mock_files_list.call_args_list
        self.assertIn("name='USA'", calls[0][1]["q"])
        self.assertIn("name='NASDAQ'", calls[1][1]["q"])


@pytest.mark.no_mock
class TestGoogleDriveHandlerNoMock(unittest.TestCase):
    def setUp(self):
        """
        Set up a real Google_Drive_Handler instance for testing.
        """
        self.root_folder_id = "real_root_folder_id"
        self.handler = Google_Drive_Handler(
            root_folder_id=self.root_folder_id,
            log_dir="./real_logfiles",
            token_path="./secrets/Google_Drive/token.json",
            credentials_path="./secrets/Google_Drive/creds.json"
        )

    def test_authenticate(self):
        """
        Test the authenticate method without mocks.
        """
        self.handler.authenticate()

    def test_upload_file(self):
        """
        Test the upload_file method without mocks.
        """
        file_path = "real_file.txt"
        folder_id = "real_folder_id"
        self.handler.upload_file(file_path, folder_id)

    def test_list_files_by_pattern(self):
        """
        Test the list_files_by_pattern method without mocks.
        """
        files = self.handler.list_files_by_pattern()
        self.assertIsInstance(files, tuple)

    def test_get_folder_id(self):
        """
        Test the get_folder_id method without mocks.
        """
        folder_id = self.handler.get_folder_id("USA", "NASDAQ")
        self.assertIsInstance(folder_id, str)

    def test_remove_folder(self):
        """
        Test the remove_folder method without mocks.
        """
        folder_path = "real_folder"
        self.handler.remove_folder(folder_path)


if __name__ == "__main__":
    unittest.main()
