import unittest
import os
from unittest.mock import MagicMock, patch
from utils import DotDict,create_local_file,remove_local_file
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
        self.root_folder_id = DotDict("secrets/Google_Drive/folder_ids.json").root

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
        file_path = 'test.txt'

        # Step 1: Create the local file
        create_local_file(file_path=file_path, content='test')

        # Step 2: Upload the file to Google Drive
        folder_id = DotDict("secrets/Google_Drive/folder_ids.json").USA.NASDAQ
        self.handler.upload_file(file_path, folder_id)

        # Step 3: Verify that the file exists on Google Drive

        
        files_on_drive = self.handler.list_files_by_pattern(folder_id=folder_id)

        file_found_on_drive = any(file['name'][0] == "test" for file in files_on_drive)

        self.assertTrue(file_found_on_drive, "File not found in Google Drive after upload.")

        # Step 4: Verify that the local file exists
        self.assertTrue(os.path.exists(file_path), "Local file was not created successfully.")

        # Step 5: Clean up by removing the file locally and from Google Drive
        remove_local_file(file_path)

        # Step 6: Verify that the local file has been deleted
        self.assertFalse(os.path.exists(file_path), "Local file was not deleted.")

        # Step 7: Remove the file from Google Drive (we use list_files_by_pattern() again to verify)
        files_on_drive = self.handler.list_files_by_pattern(folder_id=folder_id)

        file_found_on_drive = any(file['name'][0] == "test" for file in files_on_drive)

        if file_found_on_drive:
            # Assuming there's a method to remove file by id, otherwise you could list files, find the file and delete by id
            file_id_to_delete = next(file['id'] for file in files_on_drive if file['name'][0]== "test")
            self.handler.remove_file_from_drive(file_id=file_id_to_delete)

            # Step 8: Re-check if the file is still in Google Drive after deletion
            files_on_drive = self.handler.list_files_by_pattern()
            file_found_on_drive = any(file['name'][0]== "test" for file in files_on_drive)

            import pdb
            pdb.set_trace()
            self.assertFalse(file_found_on_drive, "File still exists on Google Drive after deletion.")


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



if __name__ == "__main__":
    unittest.main()
