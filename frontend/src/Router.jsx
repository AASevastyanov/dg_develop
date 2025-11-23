import { Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProfilePage from './pages/ProfilePage';
import OrganizationProfile from './pages/OrganizationProfile';
import Dashboard from './pages/Dashboard';
import HomePage from './pages/HomePage';
import ProtectedRoute from './components/ProtectedRoute';
import Events from "./pages/Events";
import EventDetail from "./pages/EventDetail/EventDetail";
import Courses from './pages/Courses';
import CourseDetail from './pages/CourseDetail';
import CreateCourse from './pages/CreateCourse';
import EditCourse from './pages/EditCourse';
import Exams from './pages/Exams';
import ExamDetail from './pages/ExamDetail';
import ExamResult from './pages/ExamResult'; // Новый компонент
import CreateExam from './pages/CreateExam';
import EditExam from './pages/EditExam';

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      
      <Route 
        path="/profile" 
        element={
          <ProtectedRoute>
            <ProfilePage />
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/organization-profile" 
        element={
          <ProtectedRoute>
            <OrganizationProfile />
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } 
      />

      <Route path="/events" element={<Events />} />
      <Route path="/event-detail" element={<EventDetail />} />

      <Route path="/courses" element={<Courses />} />
      <Route path="/course/:id" element={<CourseDetail />} />
      <Route path="/create-course" element={<ProtectedRoute><CreateCourse /></ProtectedRoute>} />
      <Route path="/edit-course/:id" element={<ProtectedRoute><EditCourse /></ProtectedRoute>} />

      <Route path="/exams" element={<Exams />} />
      <Route path="/exam/:id" element={<ProtectedRoute><ExamDetail /></ProtectedRoute>} />
      <Route path="/exam-result" element={<ProtectedRoute><ExamResult /></ProtectedRoute>} />
      <Route path="/create-exam" element={<ProtectedRoute><CreateExam /></ProtectedRoute>} />
      <Route path="/edit-exam/:id" element={<ProtectedRoute><EditExam /></ProtectedRoute>} />

      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}
