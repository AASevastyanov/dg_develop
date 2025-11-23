import styles from "./AuthForms.module.css";
import {Link} from "react-router-dom";
import logo from "../../assets/images/logo.svg";
import React from 'react';

const AuthForms = ({title, subtitle, children}) => {
    return (
        <div className={styles.container}>
            <div className={styles.background}></div>
            <Link to="/" >
                <img style={{maxWidth: 800}} src={logo} alt="logo" />
            </Link>
            <section className={styles['auth-section']}>
                <h1>{title}</h1>
                <p>{subtitle}</p>
                    {children}
            </section>
        </div>
    );
};

export default AuthForms;
