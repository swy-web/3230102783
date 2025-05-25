import tkinter as tk
from tkinter import ttk, messagebox
import random
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib
import platform

# Set Chinese font for matplotlib based on the operating system
if platform.system() == 'Windows':
    matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # Windows
elif platform.system() == 'Darwin':
    matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # Mac
else:
    matplotlib.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei']  # Linux


class EnhancedEconomicGame:
    def __init__(self, master):
        self.master = master
        master.title("生产要素管理游戏")
        master.geometry("950x700")
        master.configure(bg="#F0F0F0")

        # Center the window on screen
        self.center_window()

        # 初始化数据结构
        self.sectors = ['农业', '工业', '科技']
        self.price_labels = {}
        self.res_labels = {}
        self.entries = {sector: {} for sector in self.sectors}
        self.buy_entries = {}
        self.efficiency = {sector: 1.0 for sector in self.sectors}
        self.validate_cmd = master.register(self.validate_input)
        self.history = []  # 存储历史数据用于图表

        # 样式配置
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Treeview", font=('微软雅黑', 10), rowheight=35,  # 增加行高
                             foreground="#333", fieldbackground="#FAFAFA")
        self.style.map("Treeview", background=[('selected', '#FAFAFA')])  # 禁用选中效果
        self.colors = {
            '农业': '#C8E6C9',
            '工业': '#BBDEFB',
            '科技': '#E1BEE7'
        }

        # 游戏数据初始化
        self.resources = {'labor': 100.00, 'capital': 1000.00, 'land': 100.00}
        self.prices = {'labor': 50.00, 'land': 100.00}
        self.round = 1  # 从第一轮开始

        # 构建界面
        self.create_header()
        self.create_resource_panel()
        self.create_allocation_controls()
        self.create_market_controls()
        self.create_main_panes()
        self.set_initial_focus()

        # 延迟显示介绍消息，避免焦点问题
        self.master.after(100, self.show_intro_message)

    def center_window(self):
        """Center the window on the screen"""
        self.master.update_idletasks()
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry(f'{width}x{height}+{x}+{y}')

    def show_intro_message(self):
        message = """【游戏说明】
1. 资源使用限制：为保证可持续，每轮最多使用90%资源
2. 资源消耗：投入的资源会剩余，资金除外
3. 生产效率：各行业生产效率不同
4. 市场价格：每轮随机波动
5. 特殊事件：可能影响生产效率"""
        messagebox.showinfo("游戏说明", message)

    def create_header(self):
        header = tk.Frame(self.master, bg="#3F51B5", height=40)
        header.pack(fill=tk.X, pady=(0, 5))

        # 轮次和实际可用资源显示
        status_frame = tk.Frame(header, bg="#3F51B5")
        status_frame.pack(side=tk.LEFT, padx=15)

        self.round_label = tk.Label(status_frame, text=f"第 {self.round} 轮 | 实际可用资源:",
                                    fg="white", bg="#3F51B5",
                                    font=("微软雅黑", 10))
        self.round_label.pack(side=tk.LEFT)

        self.labor_status = tk.Label(status_frame, text="劳动力: 0.00/90.00",
                                     fg="#4CAF50", bg="#3F51B5", font=("微软雅黑", 9))
        self.capital_status = tk.Label(status_frame, text="资金: 0.00/900.00",
                                       fg="#4CAF50", bg="#3F51B5", font=("微软雅黑", 9))
        self.land_status = tk.Label(status_frame, text="土地: 0.00/90.00",
                                    fg="#4CAF50", bg="#3F51B5", font=("微软雅黑", 9))

        separator = lambda: tk.Label(status_frame, text=" | ", fg="white", bg="#3F51B5")
        self.labor_status.pack(side=tk.LEFT)
        separator().pack(side=tk.LEFT)
        self.capital_status.pack(side=tk.LEFT)
        separator().pack(side=tk.LEFT)
        self.land_status.pack(side=tk.LEFT)

    def create_resource_panel(self):
        frame = tk.Frame(self.master, bg="#FAFAFA", bd=1, relief=tk.GROOVE)
        frame.pack(pady=5, padx=5, fill=tk.X)

        # 资产标题与数据齐平
        res_frame = tk.Frame(frame, bg='#FAFAFA')
        res_frame.pack(side=tk.TOP, padx=10, pady=3)

        tk.Label(res_frame, text="你拥有的资产:", font=("微软雅黑", 10),
                 bg="#FAFAFA").pack(side=tk.LEFT, padx=(0, 10))

        resources = [('labor', '👷 劳动力'), ('capital', '💰 资金'), ('land', '🌱 土地')]
        self.res_labels = {}

        for idx, (key, name) in enumerate(resources):
            sub = tk.Frame(res_frame, bg='#FAFAFA')
            sub.pack(side=tk.LEFT, padx=10)
            tk.Label(sub, text=name.split()[0], font=("Arial", 12), bg='#FAFAFA').pack(side=tk.LEFT)
            lbl = tk.Label(sub, text=f"{self.resources[key]:.2f}",
                           font=("微软雅黑", 10, "bold"), fg="#1A237E", bg='#FAFAFA')
            lbl.pack(side=tk.LEFT, padx=3)
            self.res_labels[key] = lbl

    def validate_input(self, new_val):
        return new_val == "" or new_val.replace('.', '', 1).isdigit()

    def create_allocation_controls(self):
        main_frame = tk.Frame(self.master, bg="#FAFAFA")
        main_frame.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

        # 分配控制面板
        alloc_frame = tk.Frame(main_frame, bg="#FAFAFA")
        alloc_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for col, sector in enumerate(self.sectors):
            sector_frame = tk.Frame(alloc_frame, bd=1, relief=tk.GROOVE,
                                    bg=self.colors[sector], padx=8, pady=8)
            sector_frame.grid(row=0, column=col, padx=3, sticky=tk.NSEW)
            alloc_frame.columnconfigure(col, weight=1)

            # 标题
            tk.Label(sector_frame, text=sector, font=("微软雅黑", 11, "bold"),
                     bg=self.colors[sector]).pack(pady=3)

            # 输入区域
            input_frame = tk.Frame(sector_frame, bg=self.colors[sector])
            input_frame.pack(fill=tk.BOTH, expand=True)

            for res, name in [('labor', '劳动力'), ('capital', '资金'), ('land', '土地')]:
                row = tk.Frame(input_frame, bg=self.colors[sector])
                row.pack(pady=3, fill=tk.X)

                tk.Label(row, text=f"分配{name}:", width=6, anchor=tk.W,
                         bg=self.colors[sector], font=("微软雅黑", 9)).pack(side=tk.LEFT)

                entry = tk.Entry(
                    row,
                    width=12,  # Increased width to show full content
                    validate="key",
                    validatecommand=(self.validate_cmd, '%P'),
                    font=("微软雅黑", 9),
                    relief=tk.SOLID,
                    borderwidth=1,
                    bg="white"
                )
                entry.pack(side=tk.RIGHT, padx=3)
                entry.insert(0, '0')
                entry.bind("<KeyRelease>", self.update_usage_display)
                self.entries[sector][res] = entry

        # 生产按钮放在右侧单独一栏
        btn_frame = tk.Frame(main_frame, bg="#FAFAFA", width=120)
        btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5))

        produce_btn = tk.Button(btn_frame, text="🚀\n开始生产", command=self.start_production,
                                bg="#8B0000", fg="white", font=("微软雅黑", 10),
                                padx=10, pady=10, relief=tk.RAISED, bd=2,
                                width=8, height=4, wraplength=70)
        produce_btn.pack(pady=10)

    def create_market_controls(self):
        frame = tk.Frame(self.master, bg="#FAFAFA", bd=1, relief=tk.GROOVE)
        frame.pack(pady=5, padx=5, fill=tk.X)

        # 使用grid布局使三部分均匀分布
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)

        # 价格显示
        price_frame = tk.Frame(frame, bg="#FAFAFA")
        price_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Center content vertically
        price_container = tk.Frame(price_frame, bg="#FAFAFA")
        price_container.pack(expand=True, pady=10)

        tk.Label(price_container, text="📈 市场价格", font=("微软雅黑", 10, "bold"),
                 bg="#FAFAFA").pack(anchor=tk.CENTER)

        for res in ['labor', 'land']:
            row = tk.Frame(price_container, bg="#FAFAFA")
            row.pack(pady=3, anchor=tk.CENTER)
            name = '劳动力' if res == 'labor' else '土地'
            tk.Label(row, text=f"{name}:", width=6, font=("微软雅黑", 9),
                     bg="#FAFAFA").pack(side=tk.LEFT)
            price_lbl = tk.Label(row, text=f"¥{self.prices[res]:.2f}",
                                 fg="#D32F2F", font=("微软雅黑", 10, "bold"), bg="#FAFAFA")
            price_lbl.pack(side=tk.LEFT)
            self.price_labels[res] = price_lbl

        # 采购控制
        buy_frame = tk.Frame(frame, bg="#FAFAFA")
        buy_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Center content vertically
        buy_container = tk.Frame(buy_frame, bg="#FAFAFA")
        buy_container.pack(expand=True, pady=10)

        tk.Label(buy_container, text="🛒 市场采购", font=("微软雅黑", 10, "bold"),
                 bg="#FAFAFA").pack(anchor=tk.CENTER)

        self.buy_entries = {}
        for res in ['labor', 'land']:
            row = tk.Frame(buy_container, bg="#FAFAFA")
            row.pack(pady=3, anchor=tk.CENTER)
            name = '劳动力' if res == 'labor' else '土地'
            tk.Label(row, text=f"购买{name}:", width=8, font=("微软雅黑", 9),
                     bg="#FAFAFA").pack(side=tk.LEFT)
            entry = tk.Entry(row, width=12, validate="key",
                             validatecommand=(self.validate_cmd, '%P'),
                             font=("微软雅黑", 9), bg="white")
            entry.pack(side=tk.LEFT, padx=3)
            entry.insert(0, '0')
            self.buy_entries[res] = entry

        # 确认购买按钮放在中间列
        btn_frame = tk.Frame(frame, bg="#FAFAFA")
        btn_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

        # Center content both vertically and horizontally
        btn_container = tk.Frame(btn_frame, bg="#FAFAFA")
        btn_container.pack(expand=True)

        # Add some padding at the top to align with input fields
        tk.Frame(btn_container, height=20, bg="#FAFAFA").pack()

        buy_btn = tk.Button(btn_container, text="确认购买", command=self.buy_resources,
                            bg="#228B22", fg="white", font=("微软雅黑", 9),
                            padx=10, pady=2, relief=tk.RAISED, bd=2)
        buy_btn.pack(pady=10)

    def create_main_panes(self):
        pane = tk.PanedWindow(self.master, orient=tk.HORIZONTAL, sashwidth=8, bg="#FAFAFA")
        pane.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)

        # 左侧面板 - 生产明细和图表
        left_pane = tk.PanedWindow(pane, orient=tk.VERTICAL, sashwidth=8, bg="#FAFAFA")

        # 生产明细和图表切换
        notebook = ttk.Notebook(left_pane)

        # 生产明细标签页
        production_frame = ttk.Frame(notebook)
        self.production_tree = ttk.Treeview(production_frame,
                                            columns=('round', 'details'),
                                            show='headings', height=10,
                                            selectmode='none')  # 禁用选择
        self.production_tree.heading('round', text='轮次', anchor=tk.CENTER)
        self.production_tree.heading('details', text='生产结果', anchor=tk.W)
        self.production_tree.column('round', width=80, anchor=tk.CENTER)
        self.production_tree.column('details', width=350, anchor=tk.W)

        # 斑马线样式
        self.production_tree.tag_configure('even', background='#F5F5F5')
        self.production_tree.tag_configure('odd', background='#FFFFFF')

        scrollbar = ttk.Scrollbar(production_frame, orient="vertical", command=self.production_tree.yview)
        self.production_tree.configure(yscrollcommand=scrollbar.set)

        self.production_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 图表标签页
        chart_frame = ttk.Frame(notebook)
        self.figure = Figure(figsize=(5, 3), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        notebook.add(production_frame, text='生产明细')
        notebook.add(chart_frame, text='生产图表')
        left_pane.add(notebook)

        # 右侧面板 - 事件日志
        event_frame = ttk.Frame(pane)
        tk.Label(event_frame, text="📰 重要事件", font=("微软雅黑", 10, "bold"),
                 bg="#FAFAFA").pack(anchor=tk.W, padx=5, pady=3)

        self.event_text = tk.Text(event_frame, height=20, wrap=tk.WORD,
                                  font=("微软雅黑", 9), padx=10, pady=8,
                                  bg="white", relief=tk.FLAT)
        # 设置为只读
        self.event_text.config(state="disabled")
        scrollbar = tk.Scrollbar(event_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.event_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.event_text.yview)
        self.event_text.pack(fill=tk.BOTH, expand=True)

        # 标签样式
        self.event_text.tag_config('price', foreground='#D32F2F')
        self.event_text.tag_config('tech', foreground='#00796B')
        self.event_text.tag_config('bonus', foreground='#689F38')

        pane.add(left_pane)
        pane.add(event_frame)

    def set_initial_focus(self):
        self.master.after(100, lambda: [
            self.entries['农业']['labor'].focus_set(),
            self.entries['农业']['labor'].icursor(0)
        ])

    def update_usage_display(self, event=None):
        total_used = {'labor': 0.0, 'capital': 0.0, 'land': 0.0}
        for sector in self.sectors:
            for res in self.entries[sector]:
                try:
                    value = float(self.entries[sector][res].get() or 0)
                    total_used[res] += value
                except:
                    pass

        max_labor = self.resources['labor'] * 0.9
        max_capital = self.resources['capital'] * 0.9
        max_land = self.resources['land'] * 0.9

        self.labor_status.config(
            text=f"劳动力: {total_used['labor']:.2f}/{max_labor:.2f}",
            fg="#4CAF50" if total_used['labor'] <= max_labor else "#D32F2F"
        )
        self.capital_status.config(
            text=f"资金: {total_used['capital']:.2f}/{max_capital:.2f}",
            fg="#4CAF50" if total_used['capital'] <= max_capital else "#D32F2F"
        )
        self.land_status.config(
            text=f"土地: {total_used['land']:.2f}/{max_land:.2f}",
            fg="#4CAF50" if total_used['land'] <= max_land else "#D32F2F"
        )

    def buy_resources(self):
        try:
            total_cost = 0.0
            purchased = {'labor': 0.0, 'land': 0.0}
            for res in self.buy_entries:
                amount = float(self.buy_entries[res].get() or 0)
                if amount < 0:
                    raise ValueError("不能输入负数")
                purchased[res] = amount
                total_cost += amount * self.prices[res]

            if total_cost > self.resources['capital']:
                messagebox.showerror("错误", "资金不足！")
                return

            confirm = messagebox.askyesno("确认购买",
                                          f"即将花费 ¥{total_cost:.2f}\n购买劳动力：{purchased['labor']:.2f} 单位\n购买土地：{purchased['land']:.2f} 单位\n确认购买？")
            if not confirm:
                return

            self.resources['labor'] += purchased['labor']
            self.resources['land'] += purchased['land']
            self.resources['capital'] -= total_cost
            self.update_resource_display()

            # 在插入文本前启用编辑，插入后禁用
            self.event_text.config(state="normal")
            self.event_text.insert(tk.END,
                                   f"第{self.round}轮：🛒 购买资源 - 劳动力+{purchased['labor']:.2f} 土地+{purchased['land']:.2f} 花费¥{total_cost:.2f}\n",
                                   'bonus')
            self.event_text.see(tk.END)
            self.event_text.config(state="disabled")

            # 清空购买输入框
            for entry in self.buy_entries.values():
                entry.delete(0, tk.END)
                entry.insert(0, '0')

        except ValueError as e:
            messagebox.showerror("输入错误", "请输入有效的非负数！")

    def update_resource_display(self):
        for res in self.res_labels:
            self.res_labels[res].config(text=f"{self.resources[res]:.2f}")
        self.update_usage_display()

    def generate_random_event(self):
        events = []
        if random.random() < 0.6:
            res = random.choice(['labor', 'land'])
            change = random.uniform(-0.25, 0.35)
            new_price = max(30.0 if res == 'labor' else 60.0, self.prices[res] * (1 + change))
            events.append({
                'message': f"⚠ 市场价格波动！{'劳动力' if res == 'labor' else '土地'}价格{'+' if change > 0 else ''}{(change * 100):.2f}% → ¥{new_price:.2f}",
                'effect': lambda r=res, np=new_price: self.update_price(r, np),
                'tag': 'price'
            })

        if random.random() < 0.4:
            sector = random.choice(self.sectors)
            modifier = random.uniform(0.85, 1.25)
            events.append({
                'message': f"⚡ 技术变革！{sector}效率{'+' if modifier > 1 else ''}{((modifier - 1) * 100):.2f}%",
                'effect': lambda s=sector, m=modifier: self.update_efficiency(s, m),
                'tag': 'tech'
            })

        if random.random() < 0.25:
            events.append({
                'message': "🎉 政府补贴！全产业+15%产量",
                'effect': lambda: [self.update_efficiency(s, 1.15) for s in self.sectors],
                'tag': 'bonus'
            })

        if events:
            event = random.choice(events)
            event['effect']()
            self.event_text.config(state="normal")
            self.event_text.insert(tk.END, f"第{self.round}轮：{event['message']}\n", event['tag'])
            self.event_text.see(tk.END)
            self.event_text.config(state="disabled")

    def update_price(self, resource, new_price):
        self.prices[resource] = round(new_price, 2)
        self.price_labels[resource].config(text=f"¥{self.prices[resource]:.2f}")

    def update_efficiency(self, sector, modifier):
        self.efficiency[sector] = round(self.efficiency[sector] * modifier, 2)

    def update_chart(self):
        self.figure.clear()

        if not self.history:
            return

        # 创建子图
        ax = self.figure.add_subplot(111)

        # 获取最近5轮数据
        recent_data = self.history[-5:] if len(self.history) > 5 else self.history

        # 准备数据
        rounds = [f"第{data['round']}轮" for data in recent_data]
        sectors = self.sectors

        # 生产结果图
        results_data = [[data['results'][sector] for data in recent_data] for sector in sectors]

        width = 0.2
        x = range(len(rounds))

        for i, sector in enumerate(sectors):
            ax.bar([xi + i * width for xi in x], results_data[i], width,
                   label=sector, color=self.colors[sector])

        ax.set_xticks([xi + width for xi in x])
        ax.set_xticklabels(rounds)
        ax.set_ylabel('生产收益 (¥)')
        ax.set_xlabel('轮次')
        ax.set_title('各行业生产收益对比')
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

        # 添加网格线
        ax.grid(True, linestyle='--', alpha=0.6)

        self.figure.tight_layout()
        self.canvas.draw()

    def show_summary(self):
        if self.round % 5 != 1 or self.round == 1:
            return

        # 创建总结窗口
        summary_window = tk.Toplevel(self.master)
        summary_window.title(f"第{self.round - 5}-{self.round - 1}轮总结")
        summary_window.geometry("700x500")

        # Center the summary window
        summary_window.update_idletasks()
        width = summary_window.winfo_width()
        height = summary_window.winfo_height()
        x = (summary_window.winfo_screenwidth() // 2) - (width // 2)
        y = (summary_window.winfo_screenheight() // 2) - (height // 2)
        summary_window.geometry(f'+{x}+{y}')

        # 创建图表
        fig = Figure(figsize=(7, 5), dpi=100)
        canvas = FigureCanvasTkAgg(fig, master=summary_window)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 获取最近5轮数据
        recent_data = self.history[-5:] if len(self.history) > 5 else self.history

        # 准备数据
        rounds = [f"第{data['round']}轮" for data in recent_data]
        sectors = self.sectors

        # 创建子图
        ax = fig.add_subplot(111)

        # 资源分配趋势图
        for sector in sectors:
            results = [data['results'][sector] for data in recent_data]
            ax.plot(rounds, results, 'o-', label=sector, color=self.colors[sector])

        ax.set_title('五轮生产结果趋势')
        ax.set_ylabel('生产收益 (¥)')
        ax.set_xlabel('轮次')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.6)

        fig.tight_layout()
        canvas.draw()

    def start_production(self):
        try:
            total_used = {'labor': 0.0, 'capital': 0.0, 'land': 0.0}
            allocations = {}
            for sector in self.sectors:
                allocations[sector] = {}
                for res in self.entries[sector]:
                    value = float(self.entries[sector][res].get() or 0)
                    total_used[res] += value
                    allocations[sector][res] = value

            error_msgs = []
            for res in total_used:
                max_use = self.resources[res] * 0.9
                if total_used[res] > max_use:
                    error_msgs.append(f"⚠️ {res}超额使用！({total_used[res]:.2f} > {max_use:.2f})")
            if error_msgs:
                return messagebox.showerror("错误", "\n".join(error_msgs))

            results = {}
            for sector in self.sectors:
                # 如果任何资源分配为0，则该行业产出为0
                if any(allocations[sector][res] == 0 for res in allocations[sector]):
                    results[sector] = 0.0
                else:
                    if sector == '农业':
                        results[sector] = (allocations[sector]['labor'] * 0.6 + allocations[sector]['land'] * 1.2) * \
                                          (1 + allocations[sector]['capital'] * 0.015) * 2.5 * self.efficiency[sector]
                    elif sector == '工业':
                        results[sector] = (allocations[sector]['labor'] * 0.8 + allocations[sector]['capital'] * 0.8) * \
                                          (1.25 + allocations['科技']['capital'] * 0.03) * 3.2 * self.efficiency[sector]
                    elif sector == '科技':
                        results[sector] = (allocations[sector]['labor'] * 0.5 + allocations[sector]['capital'] * 1.1) * \
                                          1.8 * 6 * self.efficiency[sector]

            # 更新资源 - 只消耗实际使用的资源
            for sector in self.sectors:
                # 如果该行业有产出才消耗资源
                if results[sector] > 0:
                    for res in allocations[sector]:
                        self.resources[res] -= allocations[sector][res]
                else:
                    # 没有产出的行业，保留输入框中的值
                    for res in allocations[sector]:
                        # 保留输入框中的值，不清零
                        pass

            total_income = sum(results.values())
            self.resources['capital'] += total_income

            # 保存历史数据
            self.history.append({
                'round': self.round,
                'allocations': allocations,
                'results': results,
                'efficiency': self.efficiency.copy(),
                'total_income': total_income
            })

            self.round += 1
            self.round_label.config(text=f"第 {self.round} 轮")
            # 资金上限限制
            self.resources['capital'] = min(self.resources['capital'], 5000.00)

            tag = 'even' if (self.round - 1) % 2 == 0 else 'odd'
            detail_lines = []
            for sector in self.sectors:
                if results[sector] > 0:
                    detail_lines.append(f"{sector}: ¥{results[sector]:.2f} (效率x{self.efficiency[sector]:.2f})")
                else:
                    detail_lines.append(f"{sector}: 无产出 (资源不足)")
            detail = "\n".join(detail_lines)

            # 插入新行
            item_id = self.production_tree.insert('', 'end', values=(self.round - 1, detail), tags=(tag,))

            line_count = len(detail_lines)
            self.style.configure("Treeview", rowheight=30 + (line_count - 1) * 15)

            self.generate_random_event()
            self.update_resource_display()
            self.update_chart()

            # 显示五轮总结
            self.show_summary()

            self.production_tree.see(item_id)
            self.event_text.see(tk.END)

        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字！")


if __name__ == "__main__":
    root = tk.Tk()
    game = EnhancedEconomicGame(root)
    root.mainloop()
