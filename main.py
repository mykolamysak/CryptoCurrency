import asyncio
import requests
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk
from concurrent.futures import ThreadPoolExecutor

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.after(201, lambda: self.iconbitmap('scr/icon.ico'))
        self.title('Crypto Currency')
        self.geometry('854x620')

        self.data = None
        self.current_currency = 'bitcoin'  # Default currency

        self.init_main()

        self.update_price()
        self.get_data_and_plot('1')

    def init_main(self):
        # Create the main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(expand=True, fill='both')

        font = ("Roboto", 16, "bold")

        # Currency selection buttons
        currency_frame = ctk.CTkFrame(main_frame)
        currency_frame.pack(pady=10)
        self.btc_button = ctk.CTkButton(currency_frame, text='Bitcoin', command=lambda: self.set_currency('bitcoin'))
        self.btc_button.pack(side=ctk.LEFT, padx=10)
        self.eth_button = ctk.CTkButton(currency_frame, text='Ethereum', command=lambda: self.set_currency('ethereum'))
        self.eth_button.pack(side=ctk.LEFT, padx=10)

        # Label
        self.price_label = ctk.CTkLabel(main_frame, text='Price:', font=font)
        self.price_label.pack(pady=10)

        # Widget current price
        self.current_price = ctk.CTkLabel(main_frame, font=font)
        self.current_price.pack()

        # Widget price differece
        self.price_difference_label = ctk.CTkLabel(main_frame, font=font)
        self.price_difference_label.pack()

        # Create a frame for the chart
        chart_frame = ctk.CTkFrame(main_frame)
        chart_frame.pack(expand=True, fill='both', pady=10)

        # an instance of the figure for plotting the graph
        self.figure = plt.Figure()

        # Canvas Widget отображающий `figure`
        self.canvas = FigureCanvasTkAgg(self.figure, chart_frame)
        self.canvas.get_tk_widget().pack(expand=True, fill='both')

        # Create a frame for the buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=10)

        self.btn_timespan_today = ctk.CTkButton(button_frame, text='24H', command=lambda: self.get_data_and_plot('1'), width=50, height=30)
        self.btn_timespan_today.pack(side=ctk.LEFT, padx=5)

        self.btn_timespan_7_days = ctk.CTkButton(button_frame, text='7D', command=lambda: self.get_data_and_plot('7'), width=50, height=30)
        self.btn_timespan_7_days.pack(side=ctk.LEFT, padx=5)

        self.btn_timespan_30_days = ctk.CTkButton(button_frame, text='30D', command=lambda: self.get_data_and_plot('30'), width=50, height=30)
        self.btn_timespan_30_days.pack(side=ctk.LEFT, padx=5)

        self.btn_timespan_90_days = ctk.CTkButton(button_frame, text='90D', command=lambda: self.get_data_and_plot('90'), width=50, height=30)
        self.btn_timespan_90_days.pack(side=ctk.LEFT, padx=5)

        self.btn_timespan_1_year = ctk.CTkButton(button_frame, text='1Y', command=lambda: self.get_data_and_plot('365'), width=50, height=30)
        self.btn_timespan_1_year.pack(side=ctk.LEFT, padx=5)

        self.btn_timespan_all_time = ctk.CTkButton(button_frame, text='All', command=self.show_error_message, width=50, height=30)
        self.btn_timespan_all_time.pack(side=ctk.LEFT, padx=5)

    def set_currency(self, currency):
        self.current_currency = currency
        self.update_price()
        self.get_data_and_plot('1')  # Update graph with default timespan

    def get_price(self):
        url = 'https://api.coingecko.com/api/v3/simple/price'
        params = {'ids': self.current_currency, 'vs_currencies': 'usd'}
        response = requests.get(url, params=params)
        stats = response.json()
        print(f"API Response: {stats}")  # Debugging line to print API response
        if self.current_currency in stats:
            price = str(stats[self.current_currency]['usd'])
        else:
            price = "N/A"
            print(f"Error: '{self.current_currency}' not found in API response")
        return price

    def update_price(self):
        price_today = self.get_price()
        self.current_price.configure(text='$' + price_today)

    # function of receiving data via API and period of received prices
    def get_data_plot(self, timespan):
        url = f'https://api.coingecko.com/api/v3/coins/{self.current_currency}/market_chart'
        params = {'vs_currency': 'usd', 'days': timespan}
        response = requests.get(url, params=params)
        self.data = response.json()
        if 'prices' not in self.data:
            raise ValueError('Server is overloaded. Try again later.')

    # processing of received JSON data
    def data_plot(self):
        x_list = []
        y_list = []
        if "prices" in self.data:
            for item in self.data["prices"]:
                x_list.append(datetime.utcfromtimestamp(item[0] / 1000))
                y_list.append(item[1])
        return x_list, y_list

    # Graph plotting
    def plot(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        x, y = self.data_plot()
        ax.plot(x, y, label=self.current_currency.capitalize())
        ax.fill_between(x, y, alpha=.1)
        ax.yaxis.set_major_formatter('${x:1.0f}')
        ax.legend()
        ax.grid()
        self.canvas.draw()

        # Calculate and display the difference between the first and last data points
        if len(y) > 1:
            percentage_diff = ((y[-1] - y[0]) / y[0]) * 100
            if percentage_diff > 0:
                self.price_difference_label.configure(
                    text=f'↑ {percentage_diff:.2f}%', text_color="green")
            else:
                self.price_difference_label.configure(
                    text=f'↓ {percentage_diff:.2f}%', text_color="red")
        else:
            self.price_difference_label.configure(text='Change: N/A')

    def get_data_and_plot(self, timespan):
        # Use asynchronous call to avoid hanging
        asyncio.run(self.fetch_and_plot(timespan))

    async def fetch_and_plot(self, timespan):
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            try:
                await loop.run_in_executor(pool, self.get_data_plot, timespan)
                self.plot()
            except ValueError as e:
                self.show_error_message(str(e))

    def show_error_message(self, message="Your request exceeds the allowed time range. Public API users are limited to querying historical data within the past 365 days. Upgrade to a paid plan to enjoy full historical data access: https://www.coingecko.com/en/api/pricing."):
        error_window = ctk.CTkToplevel(self)
        error_window.title("Error")
        error_window.geometry("400x170")
        self.center_window(error_window, 400, 200)
        label = ctk.CTkLabel(error_window, text=message, wraplength=350, justify="left")
        label.pack(pady=20)
        button = ctk.CTkButton(error_window, text="OK", command=error_window.destroy)
        button.pack(pady=20)

    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        window.geometry(f'{width}x{height}+{x}+{y}')


if __name__ == '__main__':
    app = ctk.CTk()
    main = MainWindow()
    main.mainloop()
