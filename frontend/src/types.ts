export type Category = {
  id: number;
  name: string;
  color: string;
  owner_id: number;
};

export type Expense = {
  id: number;
  description: string;
  amount: number;
  spent_at: string;
  owner_id: number;
  category_id: number | null;
};

export type DailyTotal = {
  day: string;
  total: number;
};

export type Budget = {
  id: number;
  owner_id: number;
  month: string;
  amount: number;
  category_id: number | null;
};

export type TopCategory = {
  category_id: number;
  name: string;
  color: string;
  total: number;
};

export type DashboardSummary = {
  total_spent: number;
  month_to_date: number;
  budgets: Budget[];
  top_categories: TopCategory[];
};
