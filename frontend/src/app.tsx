import { Route, Routes } from "react-router-dom";
import { Layout } from "./components/layout";
import { EmployeeListPage } from "./pages/EmployeeListPage";
import { EmployeeDetailPage } from "./pages/EmployeeDetailPage";
import { AnalyticsPage } from "./pages/AnalyticsPage";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<EmployeeListPage />} />
        <Route path="/employees/:id" element={<EmployeeDetailPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
      </Routes>
    </Layout>
  );
}