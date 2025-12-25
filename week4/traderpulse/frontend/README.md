# TraderPulse Frontend

The **TraderPulse Frontend** is a high-performance financial dashboard built with **Next.js 16**. It is designed to feel like a professional trading terminal, featuring dark mode aesthetics, real-time data visualization, and instant AI feedback.

## 🌟 Features

- **High-Frequency UI**: Optimized for dense data display. Uses a "Dark/Cyan" theme typical of financial terminals.
- **Live Ticker Tape**: A marquee component that smoothly scrolls current market prices, giving the app an immediate sense of activity.
- **Interactive Charts**: Powered by `recharts`, allowing users to visualize price history.
- **AI Widgets**: Specialized UI components that render Gemini's text output into digestible "Sentiment Cards".
- **Responsive Design**: Fully responsive layout that adapts from large desktop monitors to mobile devices.

## 🧩 Key Components

### `TickerTape` (`src/components/dashboard/TickerTape.tsx`)
A horizontal scrolling bar. It accepts a list of symbols and independently polls their prices.
- **Tech**: `useSWR` for individual symbol fetching. CSS animations for the scroll.

### `MarketChart` (`src/components/dashboard/MarketChart.tsx`)
Displays the historical price trend.
- **Tech**: `recharts`. It handles loading states and empty data scenarios gracefully.

### `GamificationSidebar` (`src/components/dashboard/GamificationSidebar.tsx`)
A panel (currently mocked) designed to show user achievements and trading streaks, adding a layer of engagement to the learning process.

## 📜 Available Scripts

In the project directory, you can run:

- **`npm run dev`**: Starts the development server on `http://localhost:3000`.
- **`npm run build`**: Builds the app for production (creates `.next` folder).
- **`npm run start`**: Runs the built production application.
- **`npm run lint`**: Runs ESLint to check for code quality issues.

## 🚀 Deployment (Vercel)

The frontend is optimized for **Vercel**.

### Steps
1.  **Push to GitHub**: Ensure the repository is connected to Vercel.
2.  **Configuration**: In Vercel Project Settings > General, set **Root Directory** to `frontend`.
3.  **Environment Variables**: Add `NEXT_PUBLIC_API_URL` pointing to your deployed Backend URL.
4.  **Deploy**: Trigger a deployment from the dashboard.

For setup and running instructions, please see the **[Onboarding Guide](./ONBOARDING.md)**.
