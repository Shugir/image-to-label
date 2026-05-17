import unittest
from unittest.mock import patch, MagicMock
from engine.printer import get_installed_printers, print_label

class TestPrinter(unittest.TestCase):
    @patch('engine.printer.win32print.EnumPrinters')
    def test_get_installed_printers(self, mock_enum):
        # Mock EnumPrinters to return a list of printer tuples
        # According to actual output: (flags, driver, name, comment)
        mock_enum.return_value = [(0, 'driver1', 'Printer1', ''), (0, 'driver2', 'Printer2', '')]
        printers = get_installed_printers()
        self.assertEqual(printers, ['Printer1', 'Printer2'])

    @patch('engine.printer.win32print.OpenPrinter')
    @patch('engine.printer.win32print.StartDocPrinter')
    @patch('engine.printer.win32print.StartPage')
    @patch('engine.printer.win32print.WritePrinter')
    @patch('engine.printer.win32print.EndPage')
    @patch('engine.printer.win32print.EndDocPrinter')
    @patch('engine.printer.win32print.ClosePrinter')
    def test_print_label_success(self, mock_close, mock_enddoc, mock_endpage, mock_write, mock_startpage, mock_startdoc, mock_open):
        # Mock the printer handle and doc handle
        mock_open.return_value = 123
        mock_startdoc.return_value = 456
        
        text = "Test Label Content"
        printer_name = "TestPrinter"
        copies = 1
        
        result = print_label(text, printer_name, copies)
        
        self.assertTrue(result)
        mock_open.assert_called_with(printer_name)
        mock_startdoc.assert_called()
        mock_write.assert_called()
        mock_enddoc.assert_called()

    def test_print_label_failure(self):
        # This will fail because win32print isn't actually mocked here, 
        # but we want to see it handle errors
        result = print_label("text", "NonExistentPrinter", 1)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
