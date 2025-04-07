import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import yfinance as yf
from datetime import datetime, timedelta
import requests

# Additional import for the calendar widget
try:
    from tkcalendar import DateEntry
except ImportError:
    raise ImportError("Please install tkcalendar with 'pip install tkcalendar' to use the date picker.")

# --- AlTi Theme Colors ---
ALTI_DARK_BLUE = "#1A237E"
ALTI_MID_BLUE = "#1976D2"
ALTI_LIGHT_BLUE = "#00BCD4"
ALTI_FONT = ("Arial", 11)

# Backup the original requests.Session.request method
original_request = requests.Session.request

def disable_ssl_verification():
    def patched_request(self, method, url, **kwargs):
        kwargs['verify'] = False
        return original_request(self, method, url, **kwargs)
    requests.Session.request = patched_request

def enable_ssl_verification():
    requests.Session.request = original_request

def get_most_recent_business_day():
    today = datetime.today()
    if today.weekday() == 5:  # Saturday
        offset = 1
    elif today.weekday() == 6:  # Sunday
        offset = 2
    elif today.weekday() == 0:  # Monday
        offset = 3
    else:
        offset = 1
    return (today - timedelta(days=offset)).date()

# ------------------ STOCK PRICE EVENT ------------------
def get_stock_price():
    ticker = stock_ticker_var.get().upper().strip()
    if not ticker:
        messagebox.showerror("Input Error", "Please enter a valid ticker symbol.")
        return

    selected_date = stock_date_picker.get_date()
    today = datetime.today().date()
    if selected_date == today:
        selected_date = get_most_recent_business_day()

    start_date = selected_date.strftime("%Y-%m-%d")
    end_date = (selected_date + timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        disable_ssl_verification()
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
    finally:
        enable_ssl_verification()

    if data.empty:
        stock_result_label.config(text=f"No trading data for {ticker} on {selected_date}.")
    else:
        closing_price = float(data['Close'].iloc[0])
        stock_result_label.config(text=f"{stock_index_var.get()} | {ticker} on {selected_date}: ${closing_price:.2f}")

def show_stock_frame():
    main_frame.pack_forget()
    exchange_frame.pack_forget()
    stock_frame.pack(fill="both", expand=True)

def back_to_main_from_stock():
    stock_frame.pack_forget()
    main_frame.pack(fill="both", expand=True)

# ------------------ EXCHANGE RATE EVENT ------------------
country_currency = {
    "United Kingdom": "GBP",
    "Hong Kong": "HKD",
    "Singapore": "SGD",
    "USA": "USD",
    "France": "EUR",
    "Portugal": "EUR",
    "Italy": "EUR",
    "Switzerland": "CHF"
}

def get_exchange_rate():
    base_country = base_country_var.get()
    target_country = target_country_var.get()
    selected_period = exchange_period_var.get()

    if base_country == target_country:
        exchange_result_label.config(text="Both countries are the same (rate = 1.0)")
        return

    base_currency = country_currency[base_country]
    target_currency = country_currency[target_country]
    ticker = f"{base_currency}{target_currency}=X"

    # Map user selection to yfinance period
    period_map = {
        "Today": "1d",
        "Previous Day": "2d",
        "Last 5 Days": "5d"
    }
    period = period_map.get(selected_period, "1d")

    try:
        disable_ssl_verification()
        data = yf.download(ticker, period=period, progress=False)
    finally:
        enable_ssl_verification()

    if data.empty or len(data) == 0:
        exchange_result_label.config(text=f"No exchange rate data for {base_currency} to {target_currency}.")
        return

    if selected_period == "Previous Day" and len(data) >= 2:
        rate = float(data['Close'].iloc[-2])  # second-to-last closing price
        label = "Previous Day"
    else:
        rate = float(data['Close'].iloc[-1])
        label = selected_period

    exchange_result_label.config(text=f"{label}: 1 {base_currency} = {rate:.4f} {target_currency}")

def show_exchange_frame():
    main_frame.pack_forget()
    stock_frame.pack_forget()
    exchange_frame.pack(fill="both", expand=True)

def back_to_main_from_exchange():
    exchange_frame.pack_forget()
    main_frame.pack(fill="both", expand=True)

# ------------------ MAIN WINDOW (ROOT) ------------------
root = tk.Tk()
root.title("Financial Data")
root.geometry("400x400")
root.configure(bg=ALTI_LIGHT_BLUE)
root.resizable(False, False)

# ------------------ CREATE A STYLE FOR TTK ------------------
style = ttk.Style()
# We'll use the 'clam' theme as a base for more consistent styling
style.theme_use("clam")

# Frame styling
style.configure("TFrame", background=ALTI_LIGHT_BLUE)

# Label styling
style.configure("TLabel",
                background=ALTI_LIGHT_BLUE,
                foreground=ALTI_DARK_BLUE,
                font=ALTI_FONT)

# Button styling
style.configure("TButton",
                background=ALTI_MID_BLUE,
                foreground="white",
                font=ALTI_FONT,
                borderwidth=0,
                focusthickness=3,
                focuscolor="none")

style.map("TButton",
          background=[("active", ALTI_DARK_BLUE), ("disabled", "#B0B0B0")])

# Combobox styling
style.configure("TCombobox",
                fieldbackground="white",
                background="white",
                foreground=ALTI_DARK_BLUE,
                font=ALTI_FONT)

# ------------------ MAIN FRAME ------------------
main_frame = ttk.Frame(root, style="TFrame")
main_frame.pack(fill="both", expand=True)

# Use grid on the main_frame for even vertical spacing
main_frame.rowconfigure(0, weight=0)
main_frame.rowconfigure(1, weight=1)
main_frame.rowconfigure(2, weight=1)
main_frame.columnconfigure(0, weight=1)

main_label = ttk.Label(main_frame, text="Select an option:", style="TLabel", font=("Arial", 14, "bold"))
main_label.grid(row=0, column=0, pady=(20,10))

# Container frame for buttons to help with centering and even spacing
button_container = ttk.Frame(main_frame, style="TFrame")
button_container.grid(row=1, column=0, sticky="nsew", pady=(0,20))
button_container.rowconfigure(0, weight=1)
button_container.rowconfigure(1, weight=1)
button_container.columnconfigure(0, weight=1)

stock_button = ttk.Button(button_container, text="Stock Prices", command=show_stock_frame)
stock_button.grid(row=0, column=0, sticky="ew", padx=40, pady=10)

exchange_button = ttk.Button(button_container, text="Exchange Rates", command=show_exchange_frame)
exchange_button.grid(row=1, column=0, sticky="ew", padx=40, pady=10)

# ------------------ STOCK FRAME ------------------
stock_frame = ttk.Frame(root, style="TFrame")

stock_index_label = ttk.Label(stock_frame, text="Select Stock Index:")
stock_index_label.pack(pady=5)

stock_indices = ["NASDAQ", "S&P 500", "Dow Jones", "NYSE"]
stock_index_var = tk.StringVar()
stock_index_var.set(stock_indices[0])
stock_index_combo = ttk.Combobox(stock_frame, textvariable=stock_index_var, values=stock_indices, state="readonly")
stock_index_combo.pack(pady=5)

stock_ticker_label = ttk.Label(stock_frame, text="Enter Ticker Symbol:")
stock_ticker_label.pack(pady=5)

stock_ticker_var = tk.StringVar()
stock_ticker_entry = ttk.Entry(stock_frame, textvariable=stock_ticker_var, font=ALTI_FONT)
stock_ticker_entry.pack(pady=5)

stock_date_label = ttk.Label(stock_frame, text="Select a date (or leave as today):")
stock_date_label.pack(pady=5)

# The tkcalendar DateEntry doesn't fully adopt ttk styling, but we keep it for functionality
stock_date_picker = DateEntry(stock_frame, width=12, background='darkblue',
                              foreground='white', borderwidth=2, date_pattern='y-mm-dd')
stock_date_picker.pack(pady=5)

stock_get_price_button = ttk.Button(stock_frame, text="Get Closing Stock Price", command=get_stock_price)
stock_get_price_button.pack(pady=10)

stock_result_label = ttk.Label(stock_frame, text="", font=("Arial", 12), foreground=ALTI_DARK_BLUE)
stock_result_label.pack(pady=10)

stock_back_button = ttk.Button(stock_frame, text="Back", command=back_to_main_from_stock)
stock_back_button.pack(pady=10)

# ------------------ EXCHANGE FRAME ------------------
exchange_frame = ttk.Frame(root, style="TFrame")

base_country_label = ttk.Label(exchange_frame, text="Select Base Country:")
base_country_label.pack(pady=5)

countries = list(country_currency.keys())
base_country_var = tk.StringVar()
base_country_var.set(countries[0])
base_country_combo = ttk.Combobox(exchange_frame, textvariable=base_country_var, values=countries, state="readonly")
base_country_combo.pack(pady=5)

target_country_label = ttk.Label(exchange_frame, text="Select Target Country:")
target_country_label.pack(pady=5)

target_country_var = tk.StringVar()
target_country_var.set(countries[1])
target_country_combo = ttk.Combobox(exchange_frame, textvariable=target_country_var, values=countries, state="readonly")
target_country_combo.pack(pady=5)

exchange_period_label = ttk.Label(exchange_frame, text="Select Time Range:")
exchange_period_label.pack(pady=5)

period_options = ["Today", "Previous Day", "Last 5 Days"]
exchange_period_var = tk.StringVar()
exchange_period_var.set(period_options[0])
exchange_period_combo = ttk.Combobox(exchange_frame, textvariable=exchange_period_var, values=period_options, state="readonly")
exchange_period_combo.pack(pady=5)

exchange_get_rate_button = ttk.Button(exchange_frame, text="Get Exchange Rate", command=get_exchange_rate)
exchange_get_rate_button.pack(pady=10)

exchange_result_label = ttk.Label(exchange_frame, text="", font=("Arial", 12))
exchange_result_label.pack(pady=10)

exchange_back_button = ttk.Button(exchange_frame, text="Back", command=back_to_main_from_exchange)
exchange_back_button.pack(pady=10)

# ------------------ START APP ------------------
root.mainloop()
