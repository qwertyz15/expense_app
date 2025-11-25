import { useEffect, useMemo, useState } from "react";
import {
    createCategory,
    createExpense,
    deleteExpense,
    fetchDashboard,
    fetchDaily,
    getCategories,
    getExpenses,
} from "./api";
import type { Category, DailyTotal, DashboardSummary, Expense } from "./types";
import { useAuth } from "./AuthContext";

const currency = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });

function formatDate(value: string) {
    return new Date(value).toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

function buildIso(dateString: string) {
    return new Date(`${dateString}T12:00:00`).toISOString();
}

export default function Dashboard() {
    const { user, logout } = useAuth();
    const [categories, setCategories] = useState<Category[]>([]);
    const [expenses, setExpenses] = useState<Expense[]>([]);
    const [daily, setDaily] = useState<DailyTotal[]>([]);
    const [summary, setSummary] = useState<DashboardSummary | null>(null);
    const [expenseForm, setExpenseForm] = useState({
        description: "",
        amount: "",
        date: new Date().toISOString().slice(0, 10),
        category_id: "",
    });
    const [categoryForm, setCategoryForm] = useState({ name: "", color: "#8b5cf6" });
    const [error, setError] = useState<string | null>(null);

    const dailyMax = useMemo(() => Math.max(...daily.map((d) => Number(d.total)), 1), [daily]);

    async function bootstrap() {
        try {
            const [cats, exps, dailyStats, dash] = await Promise.all([
                getCategories(),
                getExpenses(),
                fetchDaily(),
                fetchDashboard(),
            ]);
            setCategories(cats);
            setExpenses(exps);
            setDaily(dailyStats);
            setSummary(dash);
            if (!expenseForm.category_id && cats.length) {
                setExpenseForm((prev) => ({ ...prev, category_id: String(cats[0].id) }));
            }
        } catch (err: any) {
            setError(err.message);
        }
    }

    useEffect(() => {
        bootstrap();
    }, []);

    async function handleExpenseSubmit(e: React.FormEvent) {
        e.preventDefault();
        setError(null);
        try {
            const payload = {
                description: expenseForm.description,
                amount: Number(expenseForm.amount),
                spent_at: buildIso(expenseForm.date),
                category_id: expenseForm.category_id ? Number(expenseForm.category_id) : null,
            };
            const created = await createExpense(payload as any);
            setExpenses((prev) => [created, ...prev]);
            setExpenseForm((prev) => ({ ...prev, description: "", amount: "" }));
            refreshStats();
        } catch (err: any) {
            setError(err.message);
        }
    }

    async function handleCategorySubmit(e: React.FormEvent) {
        e.preventDefault();
        setError(null);
        try {
            const created = await createCategory({
                name: categoryForm.name,
                color: categoryForm.color,
            });
            setCategories((prev) => [...prev, created]);
            setCategoryForm({ name: "", color: "#8b5cf6" });
            if (!expenseForm.category_id) setExpenseForm((prev) => ({ ...prev, category_id: String(created.id) }));
        } catch (err: any) {
            setError(err.message);
        }
    }

    async function handleDelete(expenseId: number) {
        await deleteExpense(expenseId);
        setExpenses((prev) => prev.filter((e) => e.id !== expenseId));
        refreshStats();
    }

    async function refreshStats() {
        const [dailyStats, dash] = await Promise.all([fetchDaily(), fetchDashboard()]);
        setDaily(dailyStats);
        setSummary(dash);
    }

    const totalThisWeek = daily.reduce((sum, item) => sum + Number(item.total), 0);

    return (
        <div className="page">
            <header className="hero">
                <div>
                    <p className="eyebrow">Daily Expense Studio</p>
                    <h1>Track spending, stay intentional.</h1>
                    <p className="lede">
                        Capture expenses in seconds, watch your daily burn, and keep budgets visible at all times.
                    </p>
                    {error && <div className="error">{error}</div>}
                </div>
                <div className="header-actions">
                    <div className="user-info">
                        <span>Welcome, {user?.name}</span>
                    </div>
                    <button className="logout-btn" onClick={logout}>
                        Logout
                    </button>
                </div>
            </header>

            <main className="grid">
                <section className="card">
                    <div className="card-header">
                        <h2>Add expense</h2>
                        <span className="badge">Today {currency.format(totalThisWeek)}</span>
                    </div>
                    <form className="form" onSubmit={handleExpenseSubmit}>
                        <label>
                            <span>Description</span>
                            <input
                                required
                                value={expenseForm.description}
                                onChange={(e) => setExpenseForm({ ...expenseForm, description: e.target.value })}
                                placeholder="Matcha latte, metro ride..."
                            />
                        </label>
                        <div className="row">
                            <label>
                                <span>Amount</span>
                                <input
                                    type="number"
                                    min="0"
                                    step="0.01"
                                    required
                                    value={expenseForm.amount}
                                    onChange={(e) => setExpenseForm({ ...expenseForm, amount: e.target.value })}
                                />
                            </label>
                            <label>
                                <span>Date</span>
                                <input
                                    type="date"
                                    required
                                    value={expenseForm.date}
                                    onChange={(e) => setExpenseForm({ ...expenseForm, date: e.target.value })}
                                />
                            </label>
                        </div>
                        <label>
                            <span>Category</span>
                            <select
                                value={expenseForm.category_id}
                                onChange={(e) => setExpenseForm({ ...expenseForm, category_id: e.target.value })}
                            >
                                <option value="">Uncategorized</option>
                                {categories.map((c) => (
                                    <option key={c.id} value={c.id}>
                                        {c.name}
                                    </option>
                                ))}
                            </select>
                        </label>
                        <button type="submit" className="primary">Save expense</button>
                    </form>
                </section>

                <section className="card">
                    <div className="card-header">
                        <h2>Create category</h2>
                        <span className="badge ghost">Palette</span>
                    </div>
                    <form className="form" onSubmit={handleCategorySubmit}>
                        <label>
                            <span>Name</span>
                            <input
                                value={categoryForm.name}
                                required
                                onChange={(e) => setCategoryForm({ ...categoryForm, name: e.target.value })}
                                placeholder="Cafes, Gym, Groceries"
                            />
                        </label>
                        <label className="color-picker">
                            <span>Color</span>
                            <input
                                type="color"
                                value={categoryForm.color}
                                onChange={(e) => setCategoryForm({ ...categoryForm, color: e.target.value })}
                            />
                        </label>
                        <button type="submit" className="secondary">Save category</button>
                    </form>

                    <div className="chips">
                        {categories.map((c) => (
                            <span key={c.id} className="chip" style={{ background: c.color }}>
                                {c.name}
                            </span>
                        ))}
                    </div>
                </section>

                <section className="card full">
                    <div className="card-header">
                        <h2>Dashboard</h2>
                        <span className="badge ghost">Live</span>
                    </div>
                    <div className="dash-grid">
                        <div className="stat">
                            <p>Total lifetime</p>
                            <h3>{currency.format(summary?.total_spent || 0)}</h3>
                        </div>
                        <div className="stat">
                            <p>Month to date</p>
                            <h3>{currency.format(summary?.month_to_date || 0)}</h3>
                        </div>
                        <div className="stat">
                            <p>Budgets</p>
                            <h3>{summary?.budgets?.length || 0}</h3>
                        </div>
                        <div className="stat">
                            <p>Categories</p>
                            <h3>{categories.length}</h3>
                        </div>
                    </div>

                    <div className="chart">
                        {daily.map((item) => (
                            <div key={item.day} className="bar">
                                <div
                                    className="fill"
                                    style={{ height: `${(Number(item.total) / dailyMax) * 100}%` }}
                                />
                                <span>{new Date(item.day).toLocaleDateString(undefined, { weekday: "short" })}</span>
                            </div>
                        ))}
                    </div>

                    <div className="top-cats">
                        {summary?.top_categories?.map((cat) => (
                            <div key={cat.category_id} className="top-card">
                                <div className="dot" style={{ background: cat.color }} />
                                <div>
                                    <p>{cat.name}</p>
                                    <strong>{currency.format(cat.total)}</strong>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

                <section className="card full">
                    <div className="card-header">
                        <h2>Recent expenses</h2>
                        <span className="badge ghost">{expenses.length}</span>
                    </div>
                    <div className="table">
                        {expenses.map((exp) => {
                            const cat = categories.find((c) => c.id === exp.category_id);
                            return (
                                <div key={exp.id} className="row-line">
                                    <div>
                                        <p className="title">{exp.description}</p>
                                        <p className="meta">{formatDate(exp.spent_at)}</p>
                                    </div>
                                    <div className="tag" style={{ background: cat?.color || "#475569" }}>
                                        {cat?.name || "Misc"}
                                    </div>
                                    <div className="amount">{currency.format(exp.amount)}</div>
                                    <button className="ghost" onClick={() => handleDelete(exp.id)}>
                                        Remove
                                    </button>
                                </div>
                            );
                        })}
                    </div>
                </section>
            </main>
        </div>
    );
}
