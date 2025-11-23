import { Link, useLocation } from 'react-router-dom';
import styles from './Header.module.css';
import logo from '../../assets/images/logo.svg';
import { useAuth } from '../../contexts/AuthContext';

export default function Header() {
    const { user, logout } = useAuth();
    const { pathname } = useLocation();
    const sections = document.querySelectorAll('a');
    const handleSwitchSection = (e) => {
        sections.forEach(section => section.classList.remove(styles.nav__sections_active));
        e.target.classList.toggle(styles.nav__sections_active);
    }
    const handleSwitchSectionHome = () => {
        sections.forEach(section => section.classList.remove(styles.nav__sections_active));
        sections[1].classList.toggle(styles.nav__sections_active);
    }
    if (pathname === '/login' || pathname === '/register') return null;
    return (
        <header className={styles.header}>
            <nav className={styles.nav}>
                <div className={styles.nav__sections}>
                    <Link to="/" onClick={handleSwitchSectionHome} className={styles.logo__home}>
                        <img className={styles.logo} src={logo} alt="logo" />
                    </Link>
                    <Link to="/" onClick={handleSwitchSection} className={styles.nav__sections_active}>Главная</Link>
                    <Link to="/courses" onClick={handleSwitchSection}>Курсы</Link>
                    <Link to="/events" onClick={handleSwitchSection}>Мероприятия</Link>
                    <Link to="/exams" onClick={handleSwitchSection}>Тесты</Link>
                </div>
                <div className={styles.nav__auth}>
                    {user ? (
                        <>
                            <Link 
                                to={user.role === 'organization' ? '/organization-profile' : '/profile'} 
                                className={styles.profile}
                            >
                                Профиль
                            </Link>
                            <button onClick={logout} className={styles.exit}>Выйти</button>
                        </>
                    ) : (
                        <>
                            <Link to="/login" className={styles.nav__auth__link}>Вход</Link>
                            <Link to="/register" className={styles.nav__auth__link}>Регистрация</Link>
                        </>
                    )}
                </div>
            </nav>

        </header>
    );
}
