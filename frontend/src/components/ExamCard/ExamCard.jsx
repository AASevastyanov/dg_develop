import React from 'react';
import styles from './ExamCard.module.css';
import { Link } from 'react-router-dom';

function getLevelLabel(level) {
  const levels = {
    1: 'A1',
    2: 'A2', 
    3: 'B1',
    4: 'B2',
    5: 'C1',
    6: 'C2'
  };
  return levels[level] || level;
}

function getLevelColor(level) {
  const colors = {
    1: '#10b981', // зеленый для A1
    2: '#3b82f6', // синий для A2
    3: '#f59e0b', // желтый для B1
    4: '#ef4444', // красный для B2
    5: '#8b5cf6', // фиолетовый для C1
    6: '#ec4899'  // розовый для C2
  };
  return colors[level] || '#6b7280';
}

export default function ExamCard({ id, title, description, level }) {
  const levelColor = getLevelColor(level);
  
  return (
    <Link to={`/exam/${id}`} className={styles.examCardContainer}>
      <div className={styles.examCardGlow}></div>
      
      <div className={styles.examCardHeader}>
        <div 
          className={styles.levelBadge}
          style={{ '--level-color': levelColor }}
        >
          <span className={styles.levelText}>{getLevelLabel(level)}</span>
          <div className={styles.levelIcon}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 11H3l3.83-3.83A1 1 0 0 1 7.7 7h8.6a1 1 0 0 1 .87.17L20 11h-6"/>
              <path d="M9 19H3l3.83 3.83A1 1 0 0 0 7.7 23h8.6a1 1 0 0 0 .87-.17L20 19h-6"/>
              <path d="M9 15v4"/>
            </svg>
          </div>
        </div>
        
        <div className={styles.examActions}>
          <button className={styles.favoriteBtn}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
            </svg>
          </button>
        </div>
      </div>

      <div className={styles.examCardContent}>
        <h3 className={styles.examTitle}>{title}</h3>
        <p className={styles.examDescription}>{description}</p>
      </div>

      <div className={styles.examCardFooter}>
        <div className={styles.examStats}>
          <div className={styles.statItem}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 6v6l4 2"/>
            </svg>
            <span>15 мин</span>
          </div>
          <div className={styles.statItem}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 12l2 2 4-4"/>
              <path d="M21 12c-1 0-3-1-3-3s2-3 3-3 3 1 3 3-2 3-3 3"/>
            </svg>
            <span>10 вопросов</span>
          </div>
        </div>

        <button className={styles.startBtn}>
          <span>Начать тест</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        </button>
      </div>
    </Link>
  );
}
