import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './ExamResult.css';

export default function ExamResult() {
  const location = useLocation();
  const navigate = useNavigate();
  
  const { result, exam } = location.state || {};

  if (!location.state || !result) {
    navigate('/exams');
    return null;
  }

  const percent = Math.round(result.percent || 0);
  const correctAnswers = result.right_answers || 0;
  const score = result.score || 0;
  const status = result.result;

  const getScoreColor = () => {
    if (percent >= 80) return '#10b981';
    if (percent >= 60) return '#f59e0b';
    return '#ef4444';
  };

  const getScoreText = () => {
    if (status === 'passed') return 'Тест пройден!';
    if (status === 'failed') return 'Тест не пройден';
    return percent >= 80 ? 'Отлично!' : percent >= 60 ? 'Хорошо!' : 'Нужно улучшить результат';
  };

  const getRecommendation = () => {
    if (percent >= 80) {
      return 'Превосходный результат! Вы отлично знаете татарский язык на этом уровне.';
    }
    if (percent >= 60) {
      return 'Хороший результат! Рекомендуем повторить некоторые темы для закрепления.';
    }
    if (percent >= 40) {
      return 'Удовлетворительный результат. Стоит уделить больше времени изучению материала.';
    }
    return 'Рекомендуем начать с более простого уровня или дополнительно изучить основы.';
  };

  return (
    <div className="modern-exam-result">
      <div className="result-container">
        <div className="result-header">
          <div style={{ marginBottom: '2rem' }}>
            <div style={{ fontSize: '3.2rem', fontWeight: 900, color: getScoreColor(), lineHeight: 1, textAlign: 'center' }}>{percent}%</div>
            <div style={{ fontSize: '1.3rem', fontWeight: 700, color: getScoreColor(), textTransform: 'uppercase', letterSpacing: '0.05em', marginTop: '0.7rem', textAlign: 'center' }}>{getScoreText()}</div>
          </div>
          <h1 className="result-title">Результаты теста{exam ? ` "${exam.title}"` : ''}</h1>
          <p className="result-recommendation">{getRecommendation()}</p>
        </div>

        <div className="result-stats">
          <div className="stat-card">
            <div className="stat-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M20 6L9 17l-5-5"/>
              </svg>
            </div>
            <div className="stat-content">
              <div className="stat-number">{correctAnswers}</div>
              <div className="stat-label">Правильных ответов</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 6v6l4 2"/>
              </svg>
            </div>
            <div className="stat-content">
              <div className="stat-number">{score}</div>
              <div className="stat-label">Баллов</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14,2 14,8 20,8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
                <polyline points="10,9 9,9 8,9"/>
              </svg>
            </div>
            <div className="stat-content">
              <div className="stat-number">{percent}%</div>
              <div className="stat-label">Процент выполнения</div>
            </div>
          </div>
        </div>

        <div className="result-progress">
          <h3>Детализация результата</h3>
          <div className="progress-bar-container">
            <div className="progress-bar" style={{ '--progress': `${percent}%`, '--progress-color': getScoreColor() }}>
              <div className="progress-fill"></div>
            </div>
            <div className="progress-labels">
              <span>0%</span>
              <span>25%</span>
              <span>50%</span>
              <span>75%</span>
              <span>100%</span>
            </div>
          </div>
        </div>

        <div className="result-actions">
          <button 
            className="modern-btn modern-btn--secondary"
            onClick={() => navigate('/exams')}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            Вернуться к тестам
          </button>
          {exam && (
            <button 
              className="modern-btn modern-btn--primary"
              onClick={() => navigate(`/exam/${exam.id}`)}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
              </svg>
              Пройти заново
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
