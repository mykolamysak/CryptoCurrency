import requests
import customtkinter as ctk
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from matplotlib import dates as mdates
import asyncio
import mplcursors
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.after(201, lambda: self.iconbitmap('src/icon.ico'))
        self.title('Crypto Currency')
        self.geometry('1000x600')

        self.current_currency = 'bitcoin'

        self.init_main()

        # Update market info and plot data on startup
        self.update_global_market_info()
        self.update_coin_list()
        self.update_price()

        # Use after method to ensure UI is fully initialized before plotting
        self.after(100, lambda: self.get_data_and_plot('1'))

    def init_main(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(expand=True, fill='both')

        main_frame.columnconfigure(0, weight=1)  # Список монет (1/5 екрану)
        main_frame.columnconfigure(1, weight=4)  # Інформація про монету та графік (4/5 екрану)
        main_frame.rowconfigure(1, weight=1)

        font = ("Roboto", 16, "bold")

        # Top info labels
        self.global_market_info_label = ctk.CTkLabel(main_frame, text='Total market volume: volume$', font=font)
        self.global_market_info_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky='w')

        self.global_market_cap_label = ctk.CTkLabel(main_frame, text='Global market cap: cap$', font=font)
        self.global_market_cap_label.grid(row=0, column=1, padx=10, pady=10, sticky='e')

        # Coins list (1/5 of the screen)
        coins_list_container = ctk.CTkFrame(main_frame, width=200)  # Set a fixed width
        coins_list_container.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
        coins_list_container.grid_propagate(False)  # Prevent the frame from shrinking
        coins_list_container.columnconfigure(0, weight=1)
        coins_list_container.rowconfigure(2, weight=1)  # Update this to 2 to accommodate the search field

        # Add search functionality
        search_frame = ctk.CTkFrame(coins_list_container)
        search_frame.grid(row=0, column=0, pady=(5, 0), sticky='ew')
        search_frame.columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search coins...")
        self.search_entry.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        self.search_entry.bind('<KeyRelease>', self.filter_coins)


        # Update the row for the coins_list_frame
        self.coins_list_frame = ctk.CTkScrollableFrame(coins_list_container)
        self.coins_list_frame.grid(row=2, column=0, sticky='nsew')
        self.coins_list_frame.grid_columnconfigure((0, 1), weight=1, uniform="column")

        # Right side container (4/5 of the screen)
        right_container = ctk.CTkFrame(main_frame)
        right_container.grid(row=1, column=1, padx=10, pady=10, sticky='nsew')
        right_container.columnconfigure(0, weight=1)
        right_container.rowconfigure(1, weight=1)

        # Coin info
        coin_info_frame = ctk.CTkFrame(right_container)
        coin_info_frame.grid(row=0, column=0, padx=10, pady=10, sticky='ew')
        coin_info_frame.columnconfigure(0, weight=1)

        self.coin_name_label = ctk.CTkLabel(coin_info_frame, text='Coin (24H)',
                                            font=("Roboto", 18, "bold"),
                                            anchor='center')
        self.coin_name_label.grid(row=0, column=0, pady=(5, 10), sticky='ew')

        self.current_price_label = ctk.CTkLabel(coin_info_frame, text='Price $', font=font)
        self.current_price_label.grid(row=1, column=0, pady=5, sticky='w')

        self.price_percentage_label = ctk.CTkLabel(coin_info_frame, text='percentage%', font=font)
        self.price_percentage_label.grid(row=2, column=0, pady=5, sticky='w')

        self.total_volume_label = ctk.CTkLabel(coin_info_frame, text='Total volume: N/A', font=font)
        self.total_volume_label.grid(row=3, column=0, pady=5, sticky='w')

        # Graph plot area
        graph_frame = ctk.CTkFrame(right_container)
        graph_frame.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
        graph_frame.columnconfigure(0, weight=1)
        graph_frame.rowconfigure(0, weight=1)

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        # Time span buttons
        time_span_frame = ctk.CTkFrame(right_container)
        time_span_frame.grid(row=2, column=0, padx=10, pady=10, sticky='ew')
        time_span_frame.columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        self.btn_timespan_24H = ctk.CTkButton(time_span_frame, text='24H',
                                                command=lambda: self.get_data_and_plot('1'), width=50, height=30)
        self.btn_timespan_24H.grid(row=0, column=0, padx=5)

        self.btn_timespan_7_days = ctk.CTkButton(time_span_frame, text='7D',
                                                 command=lambda: self.get_data_and_plot('7'), width=50, height=30)
        self.btn_timespan_7_days.grid(row=0, column=1, padx=5)

        self.btn_timespan_30_days = ctk.CTkButton(time_span_frame, text='30D',
                                                  command=lambda: self.get_data_and_plot('30'), width=50, height=30)
        self.btn_timespan_30_days.grid(row=0, column=2, padx=5)

        self.btn_timespan_90_days = ctk.CTkButton(time_span_frame, text='90D',
                                                  command=lambda: self.get_data_and_plot('90'), width=50, height=30)
        self.btn_timespan_90_days.grid(row=0, column=3, padx=5)

        self.btn_timespan_1_year = ctk.CTkButton(time_span_frame, text='1Y',
                                                 command=lambda: self.get_data_and_plot('365'), width=50, height=30)
        self.btn_timespan_1_year.grid(row=0, column=4, padx=5)

        self.btn_timespan_all_time = ctk.CTkButton(time_span_frame, text='All',
                                                   command=lambda: self.get_data_and_plot('max'), width=50, height=30)
        self.btn_timespan_all_time.grid(row=0, column=5, padx=5)

    def filter_coins(self, event):
        search_term = self.search_entry.get().lower()
        for widget in self.coins_list_frame.winfo_children():
            widget.destroy()

        filtered_coins = [coin for coin in self.coins_data if
                          search_term in coin.get('name', '').lower() or search_term in coin.get('symbol', '').lower()]

        for index, coin in enumerate(filtered_coins):
            self.create_coin_widget(coin, index)

    def create_coin_widget(self, coin, index):
        column = index % 2
        row = index // 2

        frame = ctk.CTkFrame(self.coins_list_frame)
        frame.grid(row=row, column=column, pady=5, padx=5, sticky='nsew')
        frame.grid_columnconfigure(0, weight=1)

        name_frame = ctk.CTkFrame(frame)
        name_frame.grid(row=0, column=0, pady=(5, 0), sticky='ew')
        name_frame.grid_columnconfigure(0, weight=1)

        coin_label = ctk.CTkLabel(name_frame, text=coin.get('name', 'N/A'), font=("Roboto", 14, "bold"))
        coin_label.grid(row=0, column=0, padx=5, pady=(0, 5), sticky='ew')
        coin_label.bind('<Button-1>', lambda e, c=coin.get('id'): self.set_currency(c))
        coin_label.bind('<Enter>', lambda e: e.widget.config(cursor='hand2'))
        coin_label.bind('<Leave>', lambda e: e.widget.config(cursor=''))

        info_frame = ctk.CTkFrame(frame)
        info_frame.grid(row=1, column=0, sticky='ew')
        info_frame.grid_columnconfigure((0, 1), weight=1)

        price_label = ctk.CTkLabel(info_frame, text=f"${coin.get('current_price', 0):,}", font=("Roboto", 12))
        price_label.grid(row=0, column=0, padx=5, sticky='w')
        price_label.bind('<Button-1>', lambda e, c=coin.get('id'): self.set_currency(c))
        price_label.bind('<Enter>', lambda e: e.widget.config(cursor='hand2'))
        price_label.bind('<Leave>', lambda e: e.widget.config(cursor=''))

        change_percentage = coin.get('price_change_percentage_24h', 0)
        change_label = ctk.CTkLabel(info_frame, text=f"{change_percentage:.2f}%", font=("Roboto", 12))
        change_label.grid(row=0, column=1, padx=5, sticky='e')
        change_label.bind('<Button-1>', lambda e, c=coin.get('id'): self.set_currency(c))
        change_label.bind('<Enter>', lambda e: e.widget.config(cursor='hand2'))
        change_label.bind('<Leave>', lambda e: e.widget.config(cursor=''))

        if change_percentage >= 0:
            change_label.configure(text_color="green")
        else:
            change_label.configure(text_color="red")

    def update_coin_info(self, time_period):
        self.coin_name_label.configure(text=f'{self.current_currency.capitalize()} ({time_period})')

    def set_currency(self, currency):
        self.current_currency = currency
        self.update_coin_info('24H')  # Default to 24H when changing currency
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
        self.current_price_label.configure(text='$' + price_today)

    def get_data_plot(self, timespan):
        url = f'https://api.coingecko.com/api/v3/coins/{self.current_currency}/market_chart'
        params = {'vs_currency': 'usd', 'days': timespan}
        response = requests.get(url, params=params)
        self.data = response.json()
        if 'prices' not in self.data:
            raise ValueError('Server is overloaded. Try again later.')

        if 'total_volumes' in self.data:
            volumes = self.data['total_volumes']
            if volumes:
                self.total_volume = volumes[-1][1]
            else:
                self.total_volume = 'N/A'
        else:
            self.total_volume = 'N/A'

    def data_plot(self):
        x_list = []
        y_list = []
        if "prices" in self.data:
            for item in self.data["prices"]:
                x_list.append(datetime.utcfromtimestamp(item[0] / 1000))
                y_list.append(item[1])
        return x_list, y_list

    def plot(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        x, y = self.data_plot()

        # Налаштування графіка
        ax.plot(x, y, label=self.current_currency.capitalize(), color='#1E69A4')
        ax.fill_between(x, y, color='#00BFFF', alpha=0.1)

        # Фон та кольори осей і значень
        self.figure.patch.set_facecolor('#333333')  # Фон для всього графіка
        ax.set_facecolor('#333333')  # Фон для області графіка
        ax.spines['bottom'].set_color('#FFFFFF')  # Колір нижньої осі
        ax.spines['left'].set_color('#FFFFFF')  # Колір лівої осі
        ax.spines['top'].set_visible(False)  # Приховати верхню вісь
        ax.spines['right'].set_visible(False)  # Приховати праву вісь
        ax.tick_params(axis='x', colors='#FFFFFF')  # Колір значень на осі X
        ax.tick_params(axis='y', colors='#FFFFFF')  # Колір значень на осі Y

        # Додавання курсорів для показу значень
        cursor = mplcursors.cursor(ax, hover=True)
        cursor.connect("add", lambda sel: self.configure_annotation(sel))

        ax.yaxis.set_major_formatter('${x:1.2f}')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.figure.canvas.mpl_connect('axes_leave_event', lambda event: self.remove_annotation() if hasattr(self,
                                                                                                           'current_annotation') else None)
        ax.legend()
        self.canvas.draw()

        if len(y) > 1:
            percentage_diff = ((y[-1] - y[0]) / y[0]) * 100
            if percentage_diff > 0:
                self.price_percentage_label.configure(
                    text=f'↑ {percentage_diff:.2f}%', text_color="green")
            else:
                self.price_percentage_label.configure(
                    text=f'↓ {percentage_diff:.2f}%', text_color="red")
        else:
            self.price_percentage_label.configure(text='Change: N/A')

        if hasattr(self, 'total_volume'):
            self.total_volume_label.configure(text=f'Total volume: ${self.total_volume:,.2f}')

    def configure_annotation(self, sel):
        self.current_annotation = sel.annotation  # Зберігаємо поточну анотацію
        self.current_annotation.set_text(
            f'Date: {mdates.num2date(sel.target[0]).strftime("%Y-%m-%d %H:%M:%S")}\nPrice: ${sel.target[1]:,.2f}')
        self.current_annotation.set_backgroundcolor('#2B2B2B')  # Змінюємо колір фону анотації
        self.current_annotation.set_color('#FFFFFF')  # Змінюємо колір тексту анотації
        sel.annotation.draggable(True)  # Дозволяємо перетягування анотації
        sel.annotation.set_visible(True)  # Робимо анотацію видимою

    def remove_annotation(self):
        if hasattr(self, 'current_annotation'):
            self.current_annotation.set_visible(False)

    def get_data_and_plot(self, timespan):
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, self.fetch_and_plot, timespan)

        # Update the time period in the coin info
        time_period_map = {
            '1': '24H',
            '7': '7D',
            '30': '30D',
            '90': '90D',
            '365': '1Y'
        }
        self.update_coin_info(time_period_map.get(timespan, timespan))

    def fetch_and_plot(self, timespan):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._fetch_and_plot(timespan))

    async def _fetch_and_plot(self, timespan):
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            try:
                await loop.run_in_executor(pool, self.get_data_plot, timespan)
                self.after(0, self.plot)
                self.after(0, self.update_volume_info)  # Add this line
            except ValueError as e:
                self.after(0, lambda: self.show_error_message(str(e)))

    def update_volume_info(self):
        if hasattr(self, 'total_volume'):
            self.total_volume_label.configure(text=f'Total volume: ${self.total_volume:,.2f}')
    def update_global_market_info(self):
        url = 'https://api.coingecko.com/api/v3/global'
        response = requests.get(url)
        global_data = response.json().get('data')
        if global_data:
            total_volume = global_data['total_volume']['usd']
            market_cap = global_data['total_market_cap']['usd']
            self.global_market_info_label.configure(text=f'Total market volume: ${total_volume:,.2f}')
            self.global_market_cap_label.configure(text=f'Global market cap: ${market_cap:,.2f}')

    def update_coin_list(self):
        url = 'https://api.coingecko.com/api/v3/coins/markets'
        params = {'vs_currency': 'usd', 'order': 'market_cap_desc', 'per_page': 100, 'page': 1}
        response = requests.get(url, params=params)
        self.coins_data = response.json()

        for widget in self.coins_list_frame.winfo_children():
            widget.destroy()

        for index, coin in enumerate(self.coins_data):
            self.create_coin_widget(coin, index)

    def show_error_message(self, message="Server is overloaded. Try again later."):
        error_window = ctk.CTkToplevel(self)
        error_window.title("Error")
        error_window.geometry("400x200")
        self.center_window(error_window, 400, 200)
        label = ctk.CTkLabel(error_window, text=message, wraplength=350, justify="center")
        label.pack(pady=20)
        close_button = ctk.CTkButton(error_window, text="Close", command=error_window.destroy)
        close_button.pack(pady=10)

    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x_coordinate = (screen_width / 2) - (width / 2)
        y_coordinate = (screen_height / 2) - (height / 2)
        window.geometry(f"{width}x{height}+{int(x_coordinate)}+{int(y_coordinate)}")


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()