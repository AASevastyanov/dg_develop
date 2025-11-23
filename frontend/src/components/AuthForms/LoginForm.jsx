import { useState } from 'react';
import {useNavigate, useLocation} from 'react-router-dom';
import { loginRequest } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import styles from './AuthForms.module.css';
import AuthForms from "./AuthForms";

export default function LoginForm() {
    const [email, setEmail] = useState('');
    const [pass, setPass] = useState('');
    const [error, setError] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    async function handleSubmit(e) {
        e.preventDefault();
        try {
            const { data } = await loginRequest({ email, password: pass });
            login({ access: data.access, refresh: data.refresh });
            const redirect = location.state?.from?.pathname || '/profile';
            navigate(redirect, { replace: true });
        } catch {
            setError('Неверные данные');
        }
    }

    return (
        <AuthForms
            title="Вход"
            subtitle="Рады, что вы вернулись!"
        >
            <form onSubmit={handleSubmit} className={styles['auth-form']}>
                <label htmlFor='email'>Почта</label>
                <input id={'email'} value={email} onChange={e=>setEmail(e.target.value)} placeholder="Email" />
                <label htmlFor='password'>Пароль</label>
                <input id={'password'} type="password" value={pass} onChange={e=>setPass(e.target.value)} placeholder="Пароль" />
                {error && <div>{error}</div>}
                <button type="submit">Войти</button>
            </form>
        </AuthForms>
);
}