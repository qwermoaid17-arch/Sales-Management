# 🛒 Sales & Inventory Management System (RESTful API)

A robust, production-grade **Sales and Inventory Management System API** built with **Python**, **Django**, and **Django REST Framework (DRF)**.

The system is designed to streamline retail operations, enforce strict financial data integrity, handle customer debt tracking with overpayment protection, and provide real-time business intelligence and analytics for decision-makers.

---

## 🌟 Key Architecture & Engineering Highlights

* **Strict Financial Data Integrity**:
  * **Overpayment Protection**: Enforced custom `Serializer.validate()` logic preventing payment amounts from exceeding a customer's total remaining debt.
  * **Atomic Transactions**: Leveraged `django.db.transaction.atomic()` for order creations, item stock deductions, and invoice cancellation handlers (e.g., returning stock vs. marking items as damaged) to prevent partial writes and database corruption.
* **Role-Based Access Control (RBAC)**:
  * Sensitive financial metrics (e.g., total profits, net earnings, top debtors) are restricted exclusively to administrators (`IsAdminUser`), while store operators access general sales operations (`IsAuthenticated`).
* **Advanced Database Query Optimization**:
  * Utilized Django ORM aggregations (`Sum`, `F` expressions) and date extractions (`ExtractHour`, `ExtractWeekDay`) to compute net profits, peak sales hours, and weekly activity without loading raw data into memory.
* **Clean RESTful Design**:
  * Standardized `snake_case` routing paths across all endpoints.
  * Intuitive relation representations using `SlugRelatedField` for human-readable nested payload handling.

---

## 🛠️ Tech Stack

* **Language**: Python 3.10+
* **Framework**: Django, Django REST Framework (DRF)
* **Database**: MySQL / SQLite3
* **Authentication**: Token / Session Authentication
* **Architecture Pattern**: Model-ViewSet-Serializer (RESTful API)

---

## 📦 System Modules & Feature Breakdown

### 1. Products & Inventory (`/selling_system/products/`)
* Full CRUD operations for product catalog.
* Staff view hides cost price (`cost_price`), while Admin view displays full financial pricing details.
* Automated real-time stock deduction on purchase.

### 2. Customer & Debt Management (`/selling_system/customers/`)
* Dynamic property calculations for `total_debt`, `total_paid`, and `total_remaining`.
* Complete ledger history linked to sales invoices and payment records.

### 3. Sales Processing (`/selling_system/sales/` & `/selling_system/saleitems/`)
* Flexible payment modalities: `Cash`, `Card`, `Debt`, and `Transfer`.
* Mandatory customer association for `Debt` transactions.
* Invoice Cancellation Handler (`/sales/{id}/cancel/`): Automatically restores inventory if canceled, or writes off stock if marked as `DAMAGED`.

### 4. Payments (`/selling_system/payments/`)
* Records installment payments against unpaid customer balances.
* Custom validation ensures payments cannot exceed remaining customer debt or be <= 0.

### 5. Analytics & Business Intelligence (`/selling_system/statistics/`)
* **`earnings_statistics`** *(Admin Only)*: Total revenue and net profit aggregated across All-Time, Today, Past Week, Past Month, and Past Year.
* **`debt_statistics`** *(Admin Only)*: Total outstanding market debt and top 5 debtors list.
* **`sales_statistics`**: Top 5 best-selling products by quantity.
* **`products_statistics`**: Low-stock alert system highlighting products with inventory <= 10 units.
* **`peak_times_statistics`**: Identifies highest-volume sales hours and peak weekdays for operational staffing optimization.

---

## 🚦 API Endpoints Reference

| Method | Endpoint | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `GET/POST` | `/selling_system/products/` | Authenticated | List products (`GET`) or add new product (`POST`) |
| `GET/PUT/DELETE` | `/selling_system/products/{id}/` | Authenticated | Retrieve, update or delete a product |
| `GET/POST` | `/selling_system/customers/` | Authenticated | List customer ledger (`GET`) or register new customer (`POST`) |
| `GET/POST` | `/selling_system/sales/` | Authenticated | List sales invoices (`GET`) or process new sale (`POST`) |
| `POST` | `/selling_system/sales/{id}/cancel/` | Authenticated | Cancel invoice (restores or damages stock) |
| `GET/POST` | `/selling_system/payments/` | Authenticated | List payments (`GET`) or record debt payment (`POST`) |
| `GET` | `/selling_system/statistics/` | Authenticated | Statistics navigation directory |
| `GET` | `/selling_system/statistics/earnings_statistics/` | **Admin Only** | Financial net profit & revenue reports |
| `GET` | `/selling_system/statistics/debt_statistics/` | **Admin Only** | System-wide debt analytics |
| `GET` | `/selling_system/statistics/sales_statistics/` | Authenticated | Best-selling products metrics |
| `GET` | `/selling_system/statistics/products_statistics/` | Authenticated | Low-stock inventory warnings |
| `GET` | `/selling_system/statistics/peak_times_statistics/` | Authenticated | Operational peak hours & days analysis |

---

## ⚙️ Installation & Local Setup

## ⚙️ Installation & Local Setup



### 1. Clone the Repository
```bash
git clone [https://github.com/qwermoaid17-arch/Sales-Management.git](https://github.com/qwermoaid17-arch/Sales-Management.git)