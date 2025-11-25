import type { Category, Expense, DailyTotal, DashboardSummary } from "./types";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem("token");
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: getAuthHeaders(),
    ...options,
  });

  if (!res.ok) {
    const message = await res.text();
    throw new Error(message || "Request failed");
  }

  if (res.status === 204) {
    return null as T;
  }

  return res.json();
}

export async function getCategories(): Promise<Category[]> {
  return request(`/categories`);
}

export async function createCategory(data: Omit<Category, "id" | "owner_id">) {
  return request<Category>(`/categories/`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getExpenses(): Promise<Expense[]> {
  return request(`/expenses`);
}

export async function createExpense(data: Omit<Expense, "id" | "owner_id">): Promise<Expense> {
  return request(`/expenses/`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function deleteExpense(expenseId: number) {
  return request(`/expenses/${expenseId}`, { method: "DELETE" });
}

export async function fetchDaily(): Promise<DailyTotal[]> {
  return request(`/expenses/daily`);
}

export async function fetchDashboard(): Promise<DashboardSummary> {
  return request(`/reports/dashboard`);
}
