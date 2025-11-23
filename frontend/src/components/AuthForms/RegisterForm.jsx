import { useState } from 'react';
import { registerRequest, loginRequest } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import AuthForms from './AuthForms';
import styles from './AuthForms.module.css';

export default function RegisterForm() {
    const [email, setEmail] = useState('');
    const [pass, setPass] = useState('');
    const [confirm, setConfirm] = useState('');
    const [role, setRole] = useState('user');
    const [error, setError] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();

    async function handleSubmit(e) {
        e.preventDefault();
        if (pass !== confirm) {
            setError('Пароли не совпадают');
            return;
        }
        try {
            await registerRequest({ email, password: pass, role });
            const { data } = await loginRequest({ email, password: pass });
            login({
                access: data.access,
                refresh: data.refresh,
                user: data.user // предполагая, что сервер возвращает информацию о пользователе
            });
            navigate('/profile', { replace: true });
        } catch {
            setError('Ошибка регистрации');
        }
    }

    return (
        <AuthForms title="Регистрация" subtitle="Создайте свой аккаунт">
            <form onSubmit={handleSubmit} className={styles['auth-form']}>
                <label htmlFor="email">Почта</label>
                <input
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="abv"
                />
                <label htmlFor="password">Пароль</label>
                <input
                    id="password"
                    type="password"
                    value={pass}
                    onChange={(e) => setPass(e.target.value)}
                    placeholder="Пароль"
                />
                <label htmlFor="confirm">Подтверждение пароля</label>
                <input
                    id="confirm"
                    type="password"
                    value={confirm}
                    onChange={(e) => setConfirm(e.target.value)}
                    placeholder="Подтверждение пароля"
                />
                <fieldset>
                    <legend>Тип аккаунта</legend>
                    <label>
                        <input
                            type="radio"
                            name="role"
                            value="user"
                            checked={role === 'user'}
                            onChange={(e) => setRole(e.target.value)}
                        />
                        Пользователь
                    </label>
                    <label>
                        <input
                            type="radio"
                            name="role"
                            value="organization"
                            checked={role === 'organization'}
                            onChange={(e) => setRole(e.target.value)}
                        />
                        Организация
                    </label>
                </fieldset>
                {error && <div>{error}</div>}
                <button type="submit">Зарегистрироваться</button>
            </form>
        </AuthForms>
    );
}
