import { Navigate, Route, Routes } from "react-router-dom";

import AskPage from "../pages/AskPage.jsx";
import LoginPage from "../pages/LoginPage.jsx";
import NotFound from "../pages/NotFound.jsx";
import RegisterPage from "../pages/RegisterPage.jsx";
import ProtectedRoute from "./ProtectedRoute.jsx";

const AppRoutes = () => (
  <Routes>
    <Route path="/login" element={<LoginPage />} />
    <Route path="/register" element={<RegisterPage />} />
    <Route
      path="/ask"
      element={
        <ProtectedRoute>
          <AskPage />
        </ProtectedRoute>
      }
    />
    <Route path="/" element={<Navigate to="/login" replace />} />
    <Route path="*" element={<NotFound />} />
  </Routes>
);

export default AppRoutes;
