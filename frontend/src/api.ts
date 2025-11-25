import type { Category, Expense, DailyTotal, DashboardSummary } from "./types";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
    },
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

export async function getCategories(ownerId: number): Promise<Category[]> {
  return request(`/categories?owner_id=${ownerId}`);
}

export async function createCategory(data: Partial<Category> & { owner_id: number }) {
  return request<Category>(`/categories/`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getExpenses(ownerId: number): Promise<Expense[]> {
  return request(`/expenses?owner_id=${ownerId}`);
}

export async function createExpense(data: Omit<Expense, "id">): Promise<Expense> {
  return request(`/expenses/`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function deleteExpense(expenseId: number) {
  return request(`/expenses/${expenseId}`, { method: "DELETE" });
}

export async function fetchDaily(ownerId: number): Promise<DailyTotal[]> {
  return request(`/expenses/daily?owner_id=${ownerId}`);
}

export async function fetchDashboard(ownerId: number): Promise<DashboardSummary> {
  return request(`/reports/dashboard?owner_id=${ownerId}`);
}
