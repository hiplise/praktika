import sqlite3

DB_NAME = 'budget_v2.db'

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor(1)
        # Таблица с финансовыми данными и целями
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budget_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                income REAL NOT NULL,
                expenses REAL NOT NULL,
                goal_name TEXT NOT NULL,
                goal_amount REAL NOT NULL,
                annual_deposit_rate REAL NOT NULL,
                annual_inflation_rate REAL NOT NULL
            )
        ''')
        # Таблица для сохранения истории экспериментов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS experiment_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_name TEXT,
                months_needed INTEGER,
                final_cost REAL,
                status TEXT
            )
        ''')
        # Добавляем тестовые данные для наглядного эксперимента, если база пустая
        cursor.execute("SELECT COUNT(*) FROM budget_goals")
        if cursor.fetchone()[0] == 0:
            test_data = [
                (100000, 60000, 'Автомобиль', 800000, 12.0, 7.0),
                (70000, 55000, 'Отпуск', 150000, 10.0, 6.0),
                (50000, 48000, 'Квартира', 3000000, 12.0, 8.0)
            ]
            cursor.executemany('''
                INSERT INTO budget_goals 
                (income, expenses, goal_name, goal_amount, annual_deposit_rate, annual_inflation_rate) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', test_data)

def add_user_goal():
    print("\n--- Добавление новой цели ---")
    try:
        income = float(input("Введите ежемесячный доход (руб.): "))
        expenses = float(input("Введите ежемесячные расходы (руб.): "))
        goal_name = input("Название цели: ")
        goal_amount = float(input("Текущая стоимость цели (руб.): "))
        dep_rate = float(input("Годовой процент по вкладу (например, 12): "))
        inf_rate = float(input("Годовая инфляция (например, 7): "))

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO budget_goals 
                (income, expenses, goal_name, goal_amount, annual_deposit_rate, annual_inflation_rate) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (income, expenses, goal_name, goal_amount, dep_rate, inf_rate))
        print("Цель успешно сохранена в базу данных!")
    except ValueError:
        print("Ошибка ввода: для числовых полей нужно вводить только цифры.")

def run_experiment():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM budget_goals")
        records = cursor.fetchall()

        if not records:
            print("База данных пуста.")
            return

        print("\n=== ЗАПУСК ВЫЧИСЛИТЕЛЬНОГО ЭКСПЕРИМЕНТА (V2) ===")
        for row in records:
            rec_id, income, expenses, goal_name, goal_amount, dep_rate, inf_rate = row
            monthly_savings = income - expenses
            monthly_dep = (dep_rate / 100) / 12
            monthly_inf = (inf_rate / 100) / 12

            print(f"\nСценарий #{rec_id}: Цель '{goal_name}' ({goal_amount:.0f} руб.)")
            print(f"Доход: {income:.0f} | Расход: {expenses:.0f} | Вклад: {dep_rate}% | Инфляция: {inf_rate}%")

            if monthly_savings <= 0:
                status = "Невозможно (расходы >= доходов)"
                print(f"Итог: {status}")
                cursor.execute("INSERT INTO experiment_logs (goal_name, months_needed, final_cost, status) VALUES (?, ?, ?, ?)",
                               (goal_name, 0, goal_amount, status))
                continue

            current_savings = 0.0
            current_goal_cost = goal_amount
            months = 0
            max_months = 120 # Ограничение в 10 лет

            while current_savings < current_goal_cost and months < max_months:
                months += 1
                current_savings = current_savings * (1 + monthly_dep) + monthly_savings
                current_goal_cost = current_goal_cost * (1 + monthly_inf)

            if current_savings >= current_goal_cost:
                status = "Достигнута"
                print(f"Итог: Накопите за {months} мес. Итоговая цена с инфляцией: {current_goal_cost:.2f} руб.")
            else:
                status = "Не достигнута за 10 лет"
                print(f"Итог: {status}. Накоплено {current_savings:.2f} из {current_goal_cost:.2f} руб.")

            cursor.execute("INSERT INTO experiment_logs (goal_name, months_needed, final_cost, status) VALUES (?, ?, ?, ?)",
                           (goal_name, months, round(current_goal_cost, 2), status))

def main():
    init_db()
    while True:
        print("\n=== ПРИЛОЖЕНИЕ ДЛЯ ВЕДЕНИЯ БЮДЖЕТА V2 ===")
        print("1. Добавить новую финансовую цель")
        print("2. Провести вычислительный эксперимент по всем целям")
        print("3. Выход")
        choice = input("Выберите действие (1-3): ")

        if choice == '1':
            add_user_goal()
        elif choice == '2':
            run_experiment()
        elif choice == '3':
            print("Выход из программы.")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()
