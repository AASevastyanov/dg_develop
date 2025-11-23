import Header from './components/Header/Header';
import AppRoutes from './Router';
import { AuthProvider } from './contexts/AuthContext';

export default function App() {
    return (
        <AuthProvider>
            <Header />
            <AppRoutes />
        </AuthProvider>
    );
}
