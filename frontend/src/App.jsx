// src/App.jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Home from './pages/Home';
import Explore from './pages/Explore';
import Profile from './pages/Profile';
import Chat from './pages/Chat';
import Login from './pages/Login';
import Register from './pages/Register';
import LLMLogs from './pages/LLMLogs';
import Feedback from './pages/Feedback';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Routes with Layout */}
          <Route element={<Layout />}>
            <Route path="/" element={<Home />} />
            <Route path="/explore" element={<Explore />} />
            <Route path="/ai-chat" element={<Chat />} />
            <Route path="/llm-logs" element={<LLMLogs />} />
            <Route path="/feedback" element={<Feedback />} />
            
            {/* Protected route - only profile requires authentication */}
            <Route path="/profile" element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            } />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
