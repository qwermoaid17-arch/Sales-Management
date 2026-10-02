# 🛒 Full-Stack Sales & Inventory Management System

## 🌐 Live Demo & Web Dashboard

The application is deployed and accessible online via Render:

👉 **Web Dashboard**: [Sales Management System - Live Demo](https://sales-management-dk5m.onrender.com/selling_system/dashboard/)  
👉 **REST API Root**: [Sales Management API](https://sales-management-dk5m.onrender.com/selling_system/)

A robust, production-grade **Full-Stack Sales and Inventory Management System** built with **Python**, **Django**, **Django REST Framework (DRF)**, and a responsive **Bootstrap 5 (RTL)** frontend interface.

The system is designed to streamline retail operations, enforce strict financial data integrity, handle customer debt tracking with overpayment protection, and provide real-time interactive business intelligence dashboards for decision-makers.

---

## 🌟 Key Architecture & Engineering Highlights

* **Full-Stack Integration & Responsive UI**:
  * **Interactive Arabic Dashboard (RTL)**: Custom-built responsive frontend using Bootstrap 5, FontAwesome, and modern UI components.
  * **Real-Time Data Visualization**: Dynamic financial summary cards for daily sales, total customer debts, net profit metrics, top-selling items, and operational peak hours.
* **Strict Financial Data Integrity**:
  * **Overpayment Protection**: Enforced custom `Serializer.validate()` and form validation logic preventing payment amounts from exceeding a customer's total remaining debt.
  * **Atomic Transactions**: Leveraged `django.db.transaction.atomic()` for order creations, item stock deductions, and invoice cancellation handlers (e.g., returning stock vs. marking items as damaged) to prevent partial writes and database corruption.
* **Role-Based Access Control (RBAC)**:
  * Sensitive financial metrics (e.g., total net profits, system-wide debts, debtor rankings) are restricted exclusively to administrators (`IsAdminUser`), while store operators access general sales operations (`IsAuthenticated`).
* **Advanced Database Query Optimization**:
  * Utilized Django ORM aggregations (`Sum`, `F` expressions) and date extractions (`ExtractHour`, `ExtractWeekDay`) to compute net profits, peak sales hours, and weekly activity without loading raw datasets into memory.
* **Clean RESTful & Hybrid Architecture**:
  * Dual-layer access: Full HTML Server-Side / Hybrid Web Interface for end-users, alongside standardized RESTful JSON endpoints (`snake_case` routing) for mobile apps or external integrations.

---

## 🛠️ Tech Stack

* **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5 (RTL Support), FontAwesome 6
* **Backend**: Python 3.10+, Django 5.x, Django REST Framework (DRF)
* **Database**: PostgreSQL (Production) / MySQL / SQLite3 (Development)
* **Authentication**: Django Session Authentication & JWT (JSON Web Tokens)
* **Deployment & WSGI**: Gunicorn, WhiteNoise, Render Cloud Services

---

## 📦 System Modules & Feature Breakdown

### 1. Web Dashboard (`/selling_system/dashboard/`)
* Executive summary cards displaying real-time metrics (Total Products, Total Customers, Today's Sales, Outstanding Debts, Daily Net Profit).
* Operational widgets for Low Stock Alerts (<= 10 units), Top-Selling Products, and Peak Sales Hours/Days.
* Quick-action navigation bar for seamless workflow across products, customers, sales invoices, and debt payments.

### 2. Products & Inventory (`/selling_system/products/`)
* Full CRUD operations for product catalog with dynamic price and cost calculation.
* Staff view hides purchase cost price (`cost_price`), while Admin view displays full financial pricing details.
* Automated real-time stock deduction upon invoice generation.

### 3. Customer & Debt Management (`/selling_system/customers/`)
* Dynamic property calculations for `total_debt`, `total_paid`, and `total_remaining`.
* Complete ledger history linked to sales invoices and payment records.

### 4. Sales Processing & POS (`/selling_system/sales/` & `/selling_system/saleitems/`)
* Flexible payment modalities: `Cash`, `Card`, `Debt`, and `Transfer`.
* Mandatory customer association for `Debt` transactions.
* Invoice Cancellation Handler (`/sales/{id}/cancel/`): Automatically restores inventory if canceled, or writes off stock if marked as `DAMAGED`.

### 5. Payments (`/selling_system/payments/`)
* Records installment payments against unpaid customer balances.
* Custom validation ensures payments cannot exceed remaining customer debt or be <= 0.

### 6. Analytics & Business Intelligence (`/selling_system/statistics/`)
* **`earnings_statistics`** *(Admin Only)*: Total revenue and net profit aggregated across All-Time, Today, Past Week, Past Month, and Past Year.
* **`debt_statistics`** *(Admin Only)*: Total outstanding market debt and top 5 debtors list.
* **`sales_statistics`**: Top 5 best-selling products by quantity.
* **`products_statistics`**: Low-stock alert system highlighting products with inventory <= 10 units.
* **`peak_times_statistics`**: Identifies highest-volume sales hours and peak weekdays for operational staffing optimization.

---

## 🚦 System Routes & API Reference

### Web UI Pages
| Page | Route | Access Level | Description |
| :--- | :--- | :--- | :--- |
| **Dashboard** | `/selling_system/dashboard/` | Authenticated | Main analytics & control panel |
| **Products** | `/selling_system/products-page/` | Authenticated | Product inventory management interface |
| **Customers** | `/selling_system/customers-page/` | Authenticated | Customer ledger & debt tracking UI |
| **Sales** | `/selling_system/sales-page/` | Authenticated | Sales history & POS invoice generator |
| **Payments** | `/selling_system/payments-page/` | Authenticated | Debt collection & payment records |

### REST API Endpoints
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

---

## ⚙️ Local Setup & Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/qwermoaid17-arch/Sales-Management.git](https://github.com/qwermoaid17-arch/Sales-Management.git)
cd Sales-Management