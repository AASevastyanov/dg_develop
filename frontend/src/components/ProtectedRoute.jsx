import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function ProtectedRoute({ children }) {
    const { access, loading } = useAuth();
    const location = useLocation();
    if (loading) return null; // или прелоадер
    return access ? children : <Navigate to="/login" state={{ from: location }} replace />;
}