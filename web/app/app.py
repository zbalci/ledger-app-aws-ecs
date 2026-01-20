# Import libraries
from flask import Flask, redirect, request, render_template, url_for
from connector import get, add, edit, delete, search
# Instantiate Flask functionality
#app = Flask(__name__)

def create_app():
    app = Flask(__name__)

    # Read operation: List all transactions
    @app.route("/")
    def get_transactions():
        transactions = get()
        return render_template("transactions.html", transactions=transactions)

    # Create operation: Display add transaction form
    @app.route("/add", methods=["GET", "POST"])
    def add_transaction():
        if request.method == 'POST':
            add(request.form['date'],request.form['amount'])
            return redirect(url_for("get_transactions"))
        return render_template("form.html")

    # Update operation: Display edit transaction form
    @app.route("/edit/<int:transaction_id>", methods=["GET", "POST"])
    def edit_transaction(transaction_id):
        transactions = get()
        if request.method == 'POST':
            date = request.form['date']
            amount = float(request.form['amount'])
            edit(transaction_id, date, amount)

            return redirect(url_for("get_transactions"))

        for transaction in transactions:
            if transaction['id'] == transaction_id:
                return render_template("edit.html", transaction=transaction)

    # Delete operation: Delete a transaction
    @app.route("/delete/<int:transaction_id>")
    def delete_transaction(transaction_id):
        delete(transaction_id)
        return redirect(url_for("get_transactions"))

    # Search operation
    @app.route("/search", methods=["GET", "POST"])
    def search_transaction():
        if request.method == 'GET':
            return render_template("search.html")

        if request.method == 'POST':
            min_amount = float(request.form['min_amount'])
            max_amount = float(request.form['max_amount'])
            filtered_transactions = search(min_amount,max_amount)
            return render_template("transactions.html", transactions=filtered_transactions)

    # Total balance
    @app.route("/balance")
    def total_balance():
        balance = 0
        transactions = get()
        for transaction in transactions:
            balance += transaction['amount']
        return render_template("balance.html", transactions=transactions, balance=balance)

    return app

# # Run the Flask app
# if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=80, debug=True)
