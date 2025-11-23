import { createContext, useContext, useEffect, useState } from 'react';
import { getUserMe, refreshToken } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [access, setAccess] = useState(() => localStorage.getItem('access'));
    const [refresh, setRefresh] = useState(() => localStorage.getItem('refresh'));
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // попытка подтянуть данные пользователя при старте
    useEffect(() => {
        async function bootstrap() {
            if (!access) { setLoading(false); return; }
            try {
                const { data } = await getUserMe(access);
                setUser(data);
            } catch {
                try {
                    const { data } = await refreshToken(refresh);
                    setAccessToken(data.access);
                    // Повторная попытка получить данные пользователя
                    try {
                        const userData = await getUserMe(data.access);
                        setUser(userData.data);
                    } catch {
                        clearAuth();
                    }
                } catch {
                    clearAuth();
                }
            } finally { setLoading(false); }
        }
        bootstrap();
    }, [access, refresh]); // Добавляем зависимости

    function setAccessToken(token) {
        localStorage.setItem('access', token);
        setAccess(token);
    }

    function setRefreshToken(token) {
        localStorage.setItem('refresh', token);
        setRefresh(token);
    }

    function login({ access: a, refresh: r, user: u }) {
        setAccessToken(a);
        setRefreshToken(r);
        setUser(u);
    }

    function clearAuth() {
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        setAccess(null);
        setRefresh(null);
        setUser(null);
    }

    return (
        <AuthContext.Provider value={{ access, refresh, user, login, logout: clearAuth, loading }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() { return useContext(AuthContext); }