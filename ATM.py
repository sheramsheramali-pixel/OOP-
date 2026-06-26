import datetime
import streamlit as st

# ==========================================
# CLASS 1: ACCOUNT (UNCHANGED)
# ==========================================
class Account:
    """
    This class manages individual user account details, balance sheets, and PIN updates.
    OOP Concept Applied: ENCAPSULATION
    """
    def __init__(self, account_holder, pin, balance, account_number):
        self.holder_name = account_holder     
        self.pin = pin                                                                    
        self.balance = balance               
        self.account_number = account_number 
        self.transaction_history = []        

        self.add_transaction("Account Created", balance)

    def check_pin(self, input_pin):
        return self.pin == input_pin

    def update_pin(self, new_pin):
        self.pin = new_pin
        self.add_transaction("PIN CHANGED SUCCESSFULLY", 0)

    def add_transaction(self, tx_type, amount):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if amount > 0:
            record = f"[{now}] {tx_type}: Rs. {amount:,} (New Bal: Rs. {self.balance:,})"
        else:
            record = f"[{now}] {tx_type} (New Bal: Rs. {self.balance:,})"
        self.transaction_history.append(record)

# ==========================================
# CLASS 2: ATM MACHINE (UNCHANGED)
# ==========================================
class ATM:
    """
    This class simulates the ATM machine hardware and core operational terminal software logic.
    """
    def __init__(self, machine_location, vault_cash):
        self.location = machine_location       
        self.vault_cash = vault_cash           
        self.current_account = None            
        self.is_authenticated = False          

    def insert_card(self, user_account):
        if self.current_account is not None:
            return False, "⚠️ ERROR: A card is already in the slot! Please eject it first."
        
        self.current_account = user_account
        self.is_authenticated = False
        return True, f"💳 [CARD INSERTED]: Card successfully inserted for: {user_account.holder_name}."

    def authenticate(self, pin_input):
        if not self.current_account:
            return False, "⚠️ ERROR: No card detected! Please insert your card first."

        if self.current_account.check_pin(pin_input):
            self.is_authenticated = True
            return True, "🟢 [ACCESS GRANTED]: Welcome to EASY-BANK ATM Portal!"
        else:
            return False, "❌ [ACCESS DENIED]: Incorrect Security PIN! Please try again."

    def withdraw_cash(self, amount):
        if not self.is_authenticated:
            return False, "⚠️ ERROR: Authentication required! Please input your PIN first."

        if amount <= 0:
            return False, "❌ Invalid Amount! Please enter a value greater than zero."
        if amount % 500 != 0:
            return False, "❌ Dispense Error! Amount must be in multiples of Rs. 500."
        if amount > self.current_account.balance:
            return False, "❌ Insufficient Account Balance!"
        if amount > self.vault_cash:
            return False, "❌ Out of Cash! The ATM physical vault is low."

        self.current_account.balance -= amount
        self.vault_cash -= amount
        self.current_account.add_transaction("WITHDRAW", amount)
        return True, f"💵 [SUCCESS]: Rs. {amount:,} dispensed successfully!"

    def deposit_cash(self, amount):
        if not self.is_authenticated:
            return False, "⚠️ ERROR: Access denied! Authenticate to access deposits."

        if amount <= 0 or amount % 100 != 0:
            return False, "❌ Invalid Cash Deposit! Multiples of Rs. 100 only."

        self.current_account.balance += amount
        self.vault_cash += amount
        self.current_account.add_transaction("DEPOSIT", amount)
        return True, f"💚 [DEPOSIT SUCCESS]: Rs. {amount:,} deposited successfully!"

    def transfer_funds(self, target_account, amount):
        if not self.is_authenticated:
            return False, "⚠️ ERROR: Access denied!"
        if amount <= 0:
            return False, "❌ Invalid Transfer Amount!"
        if amount > self.current_account.balance:
            return False, "❌ Insufficient funds to complete this transfer."

        self.current_account.balance -= amount
        target_account.balance += amount
        
        self.current_account.add_transaction(f"TRANSFER TO {target_account.holder_name}", amount)
        target_account.add_transaction(f"RECEIVED FROM {self.current_account.holder_name}", amount)
        
        return True, f"🚀 [TRANSFER SUCCESS]: Rs. {amount:,} transferred to {target_account.holder_name}!"

    def eject_card(self):
        if self.current_account:
            msg = f"👋 [CARD EJECTED]: Thank you {self.current_account.holder_name}!"
            self.current_account = None
            self.is_authenticated = False
            return msg
        return "⚠️ Notice: Card reader slot is already empty."


# ==========================================
# WEB USER INTERFACE (STREAMLIT APP)
# ==========================================

# Page Setup
st.set_page_config(page_title="Easy-Bank ATM", page_icon="🏧", layout="centered")
st.title("🏧 EASY-BANK ATM & BANKING SYSTEM")
st.write("---")

# Session State Initialization (Persistent Storage)
if 'accounts_db' not in st.session_state:
    st.session_state.accounts_db = {
        "Ali Ahmed": Account("Ali Ahmed", "1234", 50000, "PK123456"),
        "Ayesha Khan": Account("Ayesha Khan", "4321", 120000, "PK654321")
    }

if 'my_atm' not in st.session_state:
    st.session_state.my_atm = ATM("Islamabad Markaz Terminal", 500000)

# Messages state
if 'success_msg' not in st.session_state:
    st.session_state.success_msg = ""
if 'error_msg' not in st.session_state:
    st.session_state.error_msg = ""

atm = st.session_state.my_atm
accounts_db = st.session_state.accounts_db

# Sidebar - ATM Machine Status & Registration Portal
st.sidebar.header("🏧 Machine Status")
st.sidebar.info(f"**Location:** {atm.location}")
st.sidebar.success(f"**Vault Cash:** Rs. {atm.vault_cash:,}")
st.sidebar.write("---")

# NEW ACCOUNT REGISTRATION INTERFACE
st.sidebar.subheader("🆕 Open New Bank Account")
with st.sidebar.form(key="registration_form", clear_on_submit=True):
    new_name = st.text_input("Full Name:")
    new_acc_num = st.text_input("Desired Account Number (e.g., PK786):")
    new_pin = st.text_input("Create 4-Digit Secure PIN (Numbers Only):", type="password", max_chars=4)
    initial_deposit = st.number_input("Initial Deposit Cash (Rs.):", min_value=500, step=500)
    
    submit_btn = st.form_submit_button(label="Register Account")
    
    if submit_btn:
        if not new_name or not new_acc_num or len(new_pin) != 4:
            st.sidebar.error("❌ Please provide valid inputs. PIN must be 4 digits.")
        elif new_name in accounts_db:
            st.sidebar.error("❌ An account with this name already exists!")
        else:
            accounts_db[new_name] = Account(new_name, new_pin, initial_deposit, new_acc_num)
            st.sidebar.success(f"🎉 Account created for {new_name}!")

# MAIN TERMINAL PANEL
# STEP 1: Card Insertion
if atm.current_account is None:
    st.session_state.success_msg = ""
    st.session_state.error_msg = ""
    
    st.subheader("💳 Please Insert Your Card")
    user_options = ["Select Your Card"] + list(accounts_db.keys())
    selected_user = st.selectbox("Choose a Card to Insert:", user_options)
    
    if selected_user != "Select Your Card":
        success, msg = atm.insert_card(accounts_db[selected_user])
        st.success(msg)
        st.rerun()

# STEP 2: Authentication (PIN Input)
elif atm.current_account is not None and not atm.is_authenticated:
    st.subheader(f"🔒 Security Verification: {atm.current_account.holder_name}")
    pin_input = st.text_input("Enter 4-Digit Secure PIN:", type="password", max_chars=4)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Verify PIN", type="primary"):
            success, msg = atm.authenticate(pin_input)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    with col2:
        if st.button("Cancel & Eject Card"):
            msg = atm.eject_card()
            st.warning(msg)
            st.rerun()

# STEP 3: ATM Dashboard (Main Menu)
else:
    st.subheader(f"👋 Welcome, {atm.current_account.holder_name.upper()}!")
    st.caption(f"Account Number: {atm.current_account.account_number}")
    
    # 🌟 NEW CHANGE: Global Alerts (Tabs ke upar display honge taake har page par nazar ayein)
    if st.session_state.success_msg:
        st.success(st.session_state.success_msg)
    if st.session_state.error_msg:
        st.error(st.session_state.error_msg)
        
    st.write("---")

    # 6 Tabs layout
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "💰 Balance Inquiry", 
        "💵 Withdraw Cash", 
        "📥 Deposit Cash", 
        "🚀 Fund Transfer",
        "⚙️ Change PIN",
        "📜 Mini Statement"
    ])
    
    with tab1:
        st.metric(label="Current Active Balance", value=f"Rs. {atm.current_account.balance:,}")
        
    with tab2:
        st.write("### 💵 Secure Cash Withdrawal")
        withdraw_amt = st.number_input("Enter Amount to Withdraw (Multiples of 500):", min_value=0, step=500, key="withdraw_val")
        if st.button("Confirm Withdrawal"):
            success, msg = atm.withdraw_cash(withdraw_amt)
            if success:
                st.session_state.success_msg = msg  
                st.session_state.error_msg = ""
                st.rerun()
            else:
                st.session_state.error_msg = msg
                st.session_state.success_msg = ""
                st.rerun()
                
    with tab3:
        st.write("### 📥 Instant Cash Deposit")
        deposit_amt = st.number_input("Enter Amount to Deposit (Multiples of 100):", min_value=0, step=100, key="deposit_val")
        if st.button("Confirm Deposit"):
            success, msg = atm.deposit_cash(deposit_amt)
            if success:
                st.session_state.success_msg = msg  
                st.session_state.error_msg = ""
                st.rerun()
            else:
                st.session_state.error_msg = msg
                st.session_state.success_msg = ""
                st.rerun()

    with tab4:
        st.write("### 🚀 Inter-Account Funds Transfer")
        recipient_options = [user for user in accounts_db.keys() if user != atm.current_account.holder_name]
        
        if not recipient_options:
            st.warning("⚠️ No other active bank accounts available to transfer funds.")
        else:
            chosen_recipient = st.selectbox("Select Target Beneficiary Account:", recipient_options)
            transfer_amt = st.number_input("Enter Transfer Amount (Rs.):", min_value=0, step=500, key="transfer_val")
            
            if st.button("Execute Transfer", type="primary"):
                success, msg = atm.transfer_funds(accounts_db[chosen_recipient], transfer_amt)
                if success:
                    st.session_state.success_msg = msg  
                    st.session_state.error_msg = ""
                    st.rerun()
                else:
                    st.session_state.error_msg = msg
                    st.session_state.success_msg = ""
                    st.rerun()

    with tab5:
        st.write("### ⚙️ Change Security PIN")
        current_pin_check = st.text_input("Enter Current 4-Digit PIN:", type="password", max_chars=4, key="curr_pin_val")
        new_pin_input = st.text_input("Enter New 4-Digit Security PIN:", type="password", max_chars=4, key="new_pin_val")
        confirm_pin_input = st.text_input("Confirm New 4-Digit Security PIN:", type="password", max_chars=4, key="conf_pin_val")
        
        if st.button("Update PIN"):
            if not atm.current_account.check_pin(current_pin_check):
                st.error("❌ Verification Failed: Current PIN is incorrect.")
            elif len(new_pin_input) != 4 or not new_pin_input.isdigit():
                st.error("❌ Invalid PIN format! Must be 4 numeric digits.")
            elif new_pin_input != confirm_pin_input:
                st.error("❌ Mismatch: New PIN and Confirm PIN do not match.")
            elif current_pin_check == new_pin_input:
                st.error("❌ Error: New PIN cannot be identical to your old PIN.")
            else:
                atm.current_account.update_pin(new_pin_input)
                st.session_state.success_msg = "🟢 PIN updated successfully! For security, please log in again."
                st.session_state.error_msg = ""
                atm.eject_card()
                st.rerun()
                
    with tab6:
        st.markdown("**Last 5 Transactions Ledger Logs:**")
        for tx in atm.current_account.transaction_history[-5:]:
            st.text(tx)
            
    st.write("---")
    if st.button("🔴 Exit & Eject Card", type="secondary"):
        msg = atm.eject_card()
        st.info(msg)
        st.rerun()