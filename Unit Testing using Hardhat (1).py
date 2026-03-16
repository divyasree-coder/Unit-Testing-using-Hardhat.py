import tkinter as tk
from tkinter import messagebox
from web3 import Web3
from web3.providers.eth_tester import EthereumTesterProvider
from solcx import compile_source, install_solc

# Install Solidity compiler
install_solc("0.8.20")

# Solidity Contract
contract_source_code = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract PersonalPortfolio {

    struct Portfolio {
        string name;
        string role;
        string description;
    }

    Portfolio private portfolio;

    event PortfolioUpdated(string name, string role, string description);

    constructor(string memory _name, string memory _role, string memory _description) {
        portfolio = Portfolio(_name, _role, _description);
    }

    function updatePortfolio(
        string memory _name,
        string memory _role,
        string memory _description
    ) public {
        portfolio = Portfolio(_name, _role, _description);
        emit PortfolioUpdated(_name, _role, _description);
    }

    function getPortfolio()
        public
        view
        returns (
            string memory,
            string memory,
            string memory
        )
    {
        return (portfolio.name, portfolio.role, portfolio.description);
    }
}
"""

# Compile contract
compiled_sol = compile_source(contract_source_code, solc_version="0.8.20")
contract_id, contract_interface = compiled_sol.popitem()

# Setup Web3
w3 = Web3(EthereumTesterProvider())
w3.eth.default_account = w3.eth.accounts[0]

# Deploy contract
Portfolio = w3.eth.contract(
    abi=contract_interface['abi'],
    bytecode=contract_interface['bin']
)

tx_hash = Portfolio.constructor(
    "John Doe",
    "Blockchain Developer",
    "Building decentralized applications"
).transact()

tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

contract = w3.eth.contract(
    address=tx_receipt.contractAddress,
    abi=contract_interface['abi']
)

# ================= GUI =================

root = tk.Tk()
root.title("Personal Portfolio DApp (Python GUI)")
root.geometry("500x400")

# Labels
tk.Label(root, text="Name").pack()
name_entry = tk.Entry(root, width=50)
name_entry.pack()

tk.Label(root, text="Role").pack()
role_entry = tk.Entry(root, width=50)
role_entry.pack()

tk.Label(root, text="Description").pack()
desc_entry = tk.Entry(root, width=50)
desc_entry.pack()

output_text = tk.Text(root, height=8, width=60)
output_text.pack(pady=10)

# Functions
def load_portfolio():
    name, role, description = contract.functions.getPortfolio().call()

    name_entry.delete(0, tk.END)
    role_entry.delete(0, tk.END)
    desc_entry.delete(0, tk.END)

    name_entry.insert(0, name)
    role_entry.insert(0, role)
    desc_entry.insert(0, description)

    output_text.insert(tk.END, "Loaded portfolio from blockchain\n")


def update_portfolio():
    name = name_entry.get()
    role = role_entry.get()
    description = desc_entry.get()

    try:
        tx = contract.functions.updatePortfolio(
            name, role, description
        ).transact()

        receipt = w3.eth.wait_for_transaction_receipt(tx)

        output_text.insert(
            tk.END,
            f"Portfolio updated!\nTx Hash: {receipt.transactionHash.hex()}\n\n"
        )

        messagebox.showinfo("Success", "Portfolio Updated Successfully!")

    except Exception as e:
        messagebox.showerror("Error", str(e))


# Buttons
tk.Button(root, text="Load Portfolio", command=load_portfolio, bg="lightblue").pack(pady=5)
tk.Button(root, text="Update Portfolio", command=update_portfolio, bg="lightgreen").pack(pady=5)

# Load initial data
load_portfolio()

root.mainloop()