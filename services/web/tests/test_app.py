from app.app import create_app
from datetime import datetime
import unittest
from bs4 import BeautifulSoup

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_crud_operations(self):
        # 1. Add transaction via POST request
        response = self.client.post('/add', data={'date': '2030-12-31', 'amount': '311229'})
        self.assertEqual(response.status_code, 302)  # Redirects after adding

        # 2. Fetch the latest transaction to retrieve the ID
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        # Parse response data to find the ID of the newly added transaction
        # Assume response.data contains the HTML with transaction details including ID
        # Parse for the transaction with date 2030-12-31 and amount 311229 to get its ID
        transactions = response.get_data(as_text=True)  # Get response data as text
        transaction_id = self.extract_transaction_id(transactions, '2030-12-31', '311229')
        self.assertIsNotNone(transaction_id, "Transaction ID should not be None")

        # 3. Edit the transaction
        response = self.client.post(f'/edit/{transaction_id}', data={'date': '2030-12-31', 'amount': '311230'})
        self.assertEqual(response.status_code, 302)

        # 4. Verify the transaction was updated
        response = self.client.get('/')
        self.assertIn(b'311230', response.data)  # New amount should appear
        self.assertNotIn(b'311229', response.data)  # Old amount should not appear

        # 5. Delete the transaction
        response = self.client.get(f'/delete/{transaction_id}')
        self.assertEqual(response.status_code, 302)

        # 6. Confirm deletion
        response = self.client.get('/')
        self.assertNotIn(b'2030-12-31', response.data)
        self.assertNotIn(b'311230', response.data)

    def extract_transaction_id(self, transactions_html, date, amount):
        from bs4 import BeautifulSoup
        import re

        soup = BeautifulSoup(transactions_html, 'html.parser')

        # Print the entire HTML content for debugging
        # print("transactions_html content:", transactions_html, flush=True)

        # Check each row
        for row in soup.find_all("tr"):
            cols = row.find_all("td")
            # print("Number of columns:", len(cols), "Contents:", [col.get_text(strip=True) for col in cols], flush=True)

            # Retrieve date and amount from the first two columns
            if len(cols) >= 3:
                transaction_date = cols[0].get_text(strip=True)
                transaction_amount = cols[1].get_text(strip=True)

                # print("Date:", transaction_date, "Amount:", transaction_amount, flush=True)

                # Check if data matches
                if transaction_date == date and transaction_amount == str(amount):
                    # Extract transaction_id from 'Edit' or 'Delete' links
                    edit_link = cols[2].find("a", href=True)
                    if edit_link:
                        transaction_id = re.search(r'/edit/(\d+)', edit_link['href'])
                        if transaction_id:
                            # print("Found transaction_id:", transaction_id.group(1), flush=True)
                            return int(transaction_id.group(1))

        # print("Transaction not found", flush=True)
        return None

if __name__ == "__main__":
    unittest.main()
